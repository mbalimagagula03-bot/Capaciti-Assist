from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.db.models import User, Role, UserRole, Membership, Ticket, TicketGrant, Department
passwords=PasswordHash.recommended()
bearer=HTTPBearer()
def create_token(user_id): return jwt.encode({'sub':user_id,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},settings.secret_key,algorithm='HS256')
def current_user(auth:HTTPAuthorizationCredentials=Depends(bearer),db:Session=Depends(get_db)):
 try: user_id=jwt.decode(auth.credentials,settings.secret_key,algorithms=['HS256'])['sub']
 except (jwt.PyJWTError,KeyError): raise HTTPException(401,'Invalid credentials')
 user=db.get(User,user_id)
 if not user or not user.active: raise HTTPException(401,'Invalid credentials')
 return user
def roles_for(db,user):
 return set(db.scalars(select(Role.name).join(UserRole,UserRole.role_id==Role.id).where(UserRole.user_id==user.id)).all())
def can_read(db,user,ticket):
 if ticket.requester_id==user.id:return True
 roles=roles_for(db,user)
 grant=db.scalar(select(TicketGrant.id).where(TicketGrant.user_id==user.id,TicketGrant.ticket_id==ticket.id,((TicketGrant.expires_at==None)|(TicketGrant.expires_at>datetime.now(timezone.utc)))))
 if grant:return True
 if not roles.intersection({'Support Agent','Team Lead'}):return False
 if ticket.sensitivity_level=='CONFIDENTIAL':return False
 return bool(db.scalar(select(Membership.user_id).where(Membership.user_id==user.id,Membership.department_id==ticket.assigned_department_id,Membership.active==True)))
def require_read(db,user,ticket):
 if not ticket or not can_read(db,user,ticket):raise HTTPException(404,'Ticket not found')
