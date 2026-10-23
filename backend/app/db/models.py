from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Text, DateTime, Boolean, ForeignKey, Integer, Float, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

def uid(): return str(uuid4())
def now(): return datetime.now(timezone.utc)
class User(Base):
 __tablename__='users'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
 password_hash:Mapped[str]=mapped_column(Text)
 active:Mapped[bool]=mapped_column(Boolean,default=True)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Role(Base):
 __tablename__='roles'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 name:Mapped[str]=mapped_column(String(40),unique=True)
class UserRole(Base):
 __tablename__='user_roles'
 user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
 role_id:Mapped[str]=mapped_column(ForeignKey('roles.id'),primary_key=True)
class Department(Base):
 __tablename__='departments'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 name:Mapped[str]=mapped_column(String(80),unique=True)
 active:Mapped[bool]=mapped_column(Boolean,default=True)
 sensitivity_policy:Mapped[str]=mapped_column(String(30),default='NORMAL')
class Membership(Base):
 __tablename__='user_department_memberships'
 user_id:Mapped[str]=mapped_column(ForeignKey('users.id'),primary_key=True)
 department_id:Mapped[str]=mapped_column(ForeignKey('departments.id'),primary_key=True)
 membership_role:Mapped[str]=mapped_column(String(30),default='MEMBER')
 active:Mapped[bool]=mapped_column(Boolean,default=True)
class Ticket(Base):
 __tablename__='tickets'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 subject:Mapped[str]=mapped_column(String(200))
 body:Mapped[str]=mapped_column(Text)
 requester_id:Mapped[str]=mapped_column(ForeignKey('users.id'),index=True)
 requester_department_id:Mapped[str]=mapped_column(ForeignKey('departments.id'))
 assigned_department_id:Mapped[str|None]=mapped_column(ForeignKey('departments.id'),nullable=True,index=True)
 sensitivity_level:Mapped[str]=mapped_column(String(30),default='NORMAL')
 suggested_priority:Mapped[str|None]=mapped_column(String(20),nullable=True)
 final_priority:Mapped[str|None]=mapped_column(String(20),nullable=True)
 status:Mapped[str]=mapped_column(String(30),default='NEW')
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
 first_response_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 resolved_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
 version:Mapped[int]=mapped_column(Integer,default=1)
class TicketGrant(Base):
 __tablename__='ticket_access_grants'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'),index=True)
 user_id:Mapped[str]=mapped_column(ForeignKey('users.id'))
 granted_by:Mapped[str]=mapped_column(ForeignKey('users.id'))
 reason:Mapped[str]=mapped_column(Text)
 expires_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class TicketAssignment(Base):
 __tablename__='ticket_assignments'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'))
 department_id:Mapped[str]=mapped_column(ForeignKey('departments.id'))
 assignee_user_id:Mapped[str|None]=mapped_column(ForeignKey('users.id'))
 actor_id:Mapped[str]=mapped_column(ForeignKey('users.id'))
 assigned_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Classification(Base):
 __tablename__='ai_classifications'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'),index=True)
 predicted_department_id:Mapped[str|None]=mapped_column(ForeignKey('departments.id'))
 predicted_priority:Mapped[str|None]=mapped_column(String(20))
 raw_model_confidence:Mapped[float|None]=mapped_column(Float)
 model:Mapped[str]=mapped_column(String(100))
 prompt_version:Mapped[str]=mapped_column(String(30),default='v1')
 result_status:Mapped[str]=mapped_column(String(30))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 human_override_department_id:Mapped[str|None]=mapped_column(ForeignKey('departments.id'))
 human_override_priority:Mapped[str|None]=mapped_column(String(20))
class Response(Base):
 __tablename__='ai_responses'
 __table_args__=(UniqueConstraint('ticket_id','version'),)
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'),index=True)
 version:Mapped[int]=mapped_column(Integer,default=1)
 tone:Mapped[str]=mapped_column(String(20))
 draft_text:Mapped[str]=mapped_column(Text)
 status:Mapped[str]=mapped_column(String(30),default='DRAFT')
 model:Mapped[str]=mapped_column(String(100))
 author_id:Mapped[str|None]=mapped_column(ForeignKey('users.id'))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class Approval(Base):
 __tablename__='approvals'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 response_id:Mapped[str]=mapped_column(ForeignKey('ai_responses.id'))
 reviewer_id:Mapped[str]=mapped_column(ForeignKey('users.id'))
 decision:Mapped[str]=mapped_column(String(30))
 reason:Mapped[str|None]=mapped_column(Text)
 decided_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class TicketEvent(Base):
 __tablename__='ticket_events'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'),index=True)
 actor_id:Mapped[str|None]=mapped_column(ForeignKey('users.id'))
 event_type:Mapped[str]=mapped_column(String(80))
 metadata_json:Mapped[dict]=mapped_column('metadata',JSON,default=dict)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class Outbox(Base):
 __tablename__='notification_outbox'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'))
 response_id:Mapped[str|None]=mapped_column(ForeignKey('ai_responses.id'))
 destination_kind:Mapped[str]=mapped_column(String(30))
 status:Mapped[str]=mapped_column(String(30),default='QUEUED')
 idempotency_key:Mapped[str]=mapped_column(String(120),unique=True)
 attempts:Mapped[int]=mapped_column(Integer,default=0)
 last_error_sanitized:Mapped[str|None]=mapped_column(Text)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
 processed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class AIExecution(Base):
 __tablename__='ai_execution_logs'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'))
 purpose:Mapped[str]=mapped_column(String(40))
 model:Mapped[str]=mapped_column(String(100))
 prompt_version:Mapped[str]=mapped_column(String(30))
 latency_ms:Mapped[int|None]=mapped_column(Integer)
 outcome:Mapped[str]=mapped_column(String(30))
 token_counts:Mapped[dict|None]=mapped_column(JSON)
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class RiskEvaluation(Base):
 __tablename__='risk_evaluations'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 ticket_id:Mapped[str]=mapped_column(ForeignKey('tickets.id'))
 response_id:Mapped[str|None]=mapped_column(ForeignKey('ai_responses.id'))
 rule:Mapped[str]=mapped_column(String(100))
 result:Mapped[str]=mapped_column(String(30))
 rationale:Mapped[str]=mapped_column(Text)
 reviewer_id:Mapped[str|None]=mapped_column(ForeignKey('users.id'))
 created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class ForecastRun(Base):
 __tablename__='forecast_runs'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 model_name:Mapped[str]=mapped_column(String(100))
 training_start:Mapped[datetime]=mapped_column(DateTime(timezone=True))
 training_end:Mapped[datetime]=mapped_column(DateTime(timezone=True))
 forecast_horizon:Mapped[int]=mapped_column(Integer)
 parameters:Mapped[dict]=mapped_column(JSON)
 validation_metrics:Mapped[dict]=mapped_column(JSON)
 generated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
class ForecastPoint(Base):
 __tablename__='forecast_points'
 id:Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
 run_id:Mapped[str]=mapped_column(ForeignKey('forecast_runs.id'))
 department_id:Mapped[str]=mapped_column(ForeignKey('departments.id'))
 period:Mapped[datetime]=mapped_column(DateTime(timezone=True))
 predicted_count:Mapped[float]=mapped_column(Float)
 lower_bound:Mapped[float|None]=mapped_column(Float)
 upper_bound:Mapped[float|None]=mapped_column(Float)
