from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Role, UserRole, Department, Ticket, TicketEvent, Classification, Response, AIExecution
from app.auth.security import passwords,create_token,current_user,can_read,require_read,roles_for
from app.modules.ai.adapter import adapter
from app.core.config import settings
router=APIRouter(prefix='/api/v1')
class Login(BaseModel):email:str;password:str
class TicketCreate(BaseModel):subject:str=Field(min_length=3,max_length=200);description:str=Field(min_length=10,max_length=5000);requester_department_id:str
class DraftCreate(BaseModel):tone:str='Formal'
def ticket_json(t):return {'id':t.id,'subject':t.subject,'description':t.body,'status':t.status,'priority':t.suggested_priority,'assigned_department_id':t.assigned_department_id,'requester_id':t.requester_id,'created_at':t.created_at.isoformat(),'version':t.version}
@router.get('/health')
def health():return {'status':'ok','demo_mode':settings.demo_mode}
@router.post('/auth/login')
def login(payload:Login,db:Session=Depends(get_db)):
 user=db.scalar(select(User).where(User.email==payload.email))
 if not user or not passwords.verify(payload.password,user.password_hash) or not user.active:raise HTTPException(401,'Invalid credentials')
 return {'access_token':create_token(user.id),'token_type':'bearer'}
@router.get('/auth/me')
def me(user:User=Depends(current_user),db:Session=Depends(get_db)):
 return {'id':user.id,'email':user.email,'roles':sorted(roles_for(db,user))}
@router.post('/auth/logout')
def logout(user:User=Depends(current_user)):return {'message':'Discard the access token client-side; token revocation is not implemented in Week 1'}
@router.get('/departments')
def departments(user:User=Depends(current_user),db:Session=Depends(get_db)):
 return [{'id':d.id,'name':d.name} for d in db.scalars(select(Department).where(Department.active==True).order_by(Department.name))]
@router.post('/tickets',status_code=201)
def create_ticket(payload:TicketCreate,idempotency_key:str=Header(min_length=8,max_length=100),user:User=Depends(current_user),db:Session=Depends(get_db)):
 dept=db.get(Department,payload.requester_department_id)
 if not dept or not dept.active:raise HTTPException(422,'Invalid requester department')
 existing=db.scalar(select(TicketEvent).where(TicketEvent.actor_id==user.id,TicketEvent.event_type=='CREATED',TicketEvent.metadata_json['idempotency_key'].as_string()==idempotency_key))
 if existing:return ticket_json(db.get(Ticket,existing.ticket_id))
 ticket=Ticket(subject=payload.subject,body=payload.description,requester_id=user.id,requester_department_id=dept.id)
 db.add(ticket);db.flush();db.add(TicketEvent(ticket_id=ticket.id,actor_id=user.id,event_type='CREATED',metadata_json={'idempotency_key':idempotency_key}));db.commit();db.refresh(ticket)
 return ticket_json(ticket)
@router.get('/tickets')
def list_tickets(user:User=Depends(current_user),db:Session=Depends(get_db)):
 tickets=db.scalars(select(Ticket).order_by(Ticket.created_at.desc()).limit(200)).all()
 return [ticket_json(t) for t in tickets if can_read(db,user,t)]
@router.get('/tickets/{ticket_id}')
def detail(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t=db.get(Ticket,ticket_id);require_read(db,user,t)
 data=ticket_json(t)
 data['classification']=[{'department_id':c.predicted_department_id,'priority':c.predicted_priority,'confidence_estimate':c.raw_model_confidence,'status':c.result_status,'model':c.model} for c in db.scalars(select(Classification).where(Classification.ticket_id==t.id).order_by(Classification.created_at.desc()))]
 data['drafts']=[{'id':r.id,'text':r.draft_text,'tone':r.tone,'version':r.version,'status':r.status,'model':r.model} for r in db.scalars(select(Response).where(Response.ticket_id==t.id).order_by(Response.version.desc()))]
 return data
@router.post('/tickets/{ticket_id}/classify')
def classify(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t=db.get(Ticket,ticket_id);require_read(db,user,t)
 if not roles_for(db,user).intersection({'Support Agent','Team Lead','Administrator'}):
  if t.requester_id!=user.id:raise HTTPException(403,'Forbidden')
 departments={d.name:d.id for d in db.scalars(select(Department).where(Department.active==True))}
 ai=adapter();result=None;source='offline-fallback' if settings.demo_mode or not settings.gemini_api_key else settings.gemini_model
 try:result=ai.classify(t.subject,t.body,list(departments))
 except Exception:source='provider-failure';result=None
 if result and result.department in departments:
  t.assigned_department_id=departments[result.department];t.suggested_priority=result.priority
  t.sensitivity_level='CONFIDENTIAL' if result.department in ('HR','Wellness','Legal') else 'NORMAL'
  t.status='NEEDS_REVIEW' if t.sensitivity_level=='CONFIDENTIAL' else 'CLASSIFIED'
 else:t.status='NEEDS_REVIEW'
 db.add(Classification(ticket_id=t.id,predicted_department_id=departments.get(result.department) if result else None,predicted_priority=result.priority if result else None,raw_model_confidence=result.confidence if result else None,model=source,result_status='OK' if result else 'NEEDS_REVIEW'))
 db.add(AIExecution(ticket_id=t.id,purpose='classification',model=source,prompt_version='v1',outcome='OK' if result else 'FALLBACK_REVIEW'))
 db.add(TicketEvent(ticket_id=t.id,actor_id=user.id,event_type='CLASSIFIED' if result else 'MANUAL_REVIEW',metadata_json={'model':source}));db.commit()
 return {'status':t.status,'department':result.department if result else None,'priority':result.priority if result else None,'source':source}
@router.post('/tickets/{ticket_id}/drafts')
def draft(ticket_id:str,payload:DraftCreate,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t=db.get(Ticket,ticket_id);require_read(db,user,t)
 if payload.tone not in ('Formal','Friendly','Urgent'):raise HTTPException(422,'Invalid tone')
 if not roles_for(db,user).intersection({'Support Agent','Team Lead'}):raise HTTPException(403,'Only support agents or team leads can prepare drafts')
 if t.status=='NEEDS_REVIEW':raise HTTPException(409,'Manual classification review required before drafting')
 ai=adapter();source='offline-fallback' if settings.demo_mode or not settings.gemini_api_key else settings.gemini_model
 try:content=ai.draft(t.subject,t.body,payload.tone)
 except Exception:source='offline-fallback';from app.modules.ai.adapter import OfflineAdapter;content=OfflineAdapter().draft(t.subject,t.body,payload.tone)
 previous=db.scalars(select(Response).where(Response.ticket_id==t.id).order_by(Response.version.desc())).first()
 if previous:previous.status='SUPERSEDED'
 r=Response(ticket_id=t.id,version=(previous.version+1 if previous else 1),tone=payload.tone,draft_text=content,model=source,author_id=user.id)
 db.add(r);db.add(AIExecution(ticket_id=t.id,purpose='draft',model=source,prompt_version='v1',outcome='OK'));db.add(TicketEvent(ticket_id=t.id,actor_id=user.id,event_type='DRAFT_CREATED',metadata_json={'tone':payload.tone}));db.commit()
 return {'id':r.id,'version':r.version,'tone':r.tone,'text':r.draft_text,'status':r.status,'source':source}
@router.get('/tickets/{ticket_id}/events')
def events(ticket_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
 t=db.get(Ticket,ticket_id);require_read(db,user,t)
 return [{'type':e.event_type,'created_at':e.created_at.isoformat()} for e in db.scalars(select(TicketEvent).where(TicketEvent.ticket_id==t.id).order_by(TicketEvent.created_at))]
