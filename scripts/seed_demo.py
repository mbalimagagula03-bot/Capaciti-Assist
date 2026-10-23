from sqlalchemy import select
from app.db.session import SessionLocal
from app.db.models import User,Role,UserRole,Department,Membership,Ticket
from app.auth.security import passwords
ROLES=['Requester','Support Agent','Team Lead','Administrator']
DEPTS=['IT','HR','Wellness','Legal','Admin','Finance','Operations']
ACCOUNTS=[('requester@demo.local','Requester','IT'),('agent.it@demo.local','Support Agent','IT'),('lead.it@demo.local','Team Lead','IT'),('agent.hr@demo.local','Support Agent','HR'),('lead.hr@demo.local','Team Lead','HR'),('administrator@demo.local','Administrator','Admin')]
def main():
 with SessionLocal() as db:
  for name in ROLES:
   if not db.scalar(select(Role).where(Role.name==name)):db.add(Role(name=name))
  for name in DEPTS:
   if not db.scalar(select(Department).where(Department.name==name)):db.add(Department(name=name,active=name not in ('Finance','Operations'),sensitivity_policy='CONFIDENTIAL' if name in ('HR','Wellness','Legal') else 'NORMAL'))
  db.flush()
  for email,role,department in ACCOUNTS:
   user=db.scalar(select(User).where(User.email==email))
   if not user:user=User(email=email,password_hash=passwords.hash('DemoOnly!2026'));db.add(user);db.flush()
   r=db.scalar(select(Role).where(Role.name==role));d=db.scalar(select(Department).where(Department.name==department))
   if not db.get(UserRole,(user.id,r.id)):db.add(UserRole(user_id=user.id,role_id=r.id))
   if not db.get(Membership,(user.id,d.id)):db.add(Membership(user_id=user.id,department_id=d.id))
  db.commit()
 print('Demo seed complete; accounts use password DemoOnly!2026 (LOCAL DEMO ONLY)')
if __name__=='__main__':main()
