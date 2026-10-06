from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import require_admin
from app.models.admin import Admin
from app.models.parent import Parent, ParentStudent
from app.models.student import Student

router=APIRouter(prefix="/admin/parents",tags=["Admin Parents"])
pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

class ParentCreate(BaseModel):
    full_name:str=Field(min_length=2,max_length=150)
    phone:str=Field(min_length=9,max_length=30)
    password:str=Field(min_length=8,max_length=128)
    student_ids:list[int]=[]

@router.get("/")
def list_parents(admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    rows=db.query(Parent).order_by(Parent.id.desc()).all(); result=[]
    for p in rows:
        children=db.query(Student).join(ParentStudent,ParentStudent.student_id==Student.id).filter(ParentStudent.parent_id==p.id).all()
        result.append({"id":p.id,"full_name":p.full_name,"phone":p.phone,"is_active":p.is_active,"children":[{"id":s.id,"full_name":s.full_name} for s in children]})
    return {"success":True,"parents":result}

@router.post("/")
def create_parent(data:ParentCreate,admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    phone=data.phone.strip().replace(" ","").replace("-","").replace("(","").replace(")","")
    if phone.startswith("+"): phone=phone[1:]
    if not phone.isdigit() or len(phone)!=12 or not phone.startswith("998"):
        raise HTTPException(status_code=400,detail="Telefon raqam 998XXXXXXXXX ko‘rinishida bo‘lishi kerak")
    if db.query(Parent).filter(Parent.phone==phone).first(): raise HTTPException(status_code=409,detail="Bu telefon raqam bilan ota-ona allaqachon mavjud")
    students=db.query(Student).filter(Student.id.in_(data.student_ids),Student.is_active==True).all() if data.student_ids else []
    if len(students)!=len(set(data.student_ids)): raise HTTPException(status_code=400,detail="Tanlangan o‘quvchilardan biri topilmadi yoki faol emas")
    p=Parent(full_name=data.full_name.strip(),phone=phone,password_hash=pwd_context.hash(data.password),is_active=True)
    db.add(p);db.flush()
    for s in students: db.add(ParentStudent(parent_id=p.id,student_id=s.id))
    try: db.commit()
    except IntegrityError: db.rollback();raise HTTPException(status_code=409,detail="Ota-ona ma’lumotlari takrorlangan")
    db.refresh(p)
    return {"success":True,"parent":{"id":p.id,"full_name":p.full_name,"phone":p.phone,"children":[{"id":s.id,"full_name":s.full_name} for s in students]}}

@router.post("/{parent_id}/students/{student_id}")
def link_student(parent_id:int,student_id:int,admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    p=db.query(Parent).filter(Parent.id==parent_id).first();s=db.query(Student).filter(Student.id==student_id,Student.is_active==True).first()
    if not p or not s: raise HTTPException(status_code=404,detail="Ota-ona yoki o‘quvchi topilmadi")
    if not db.query(ParentStudent).filter(ParentStudent.parent_id==parent_id,ParentStudent.student_id==student_id).first(): db.add(ParentStudent(parent_id=parent_id,student_id=student_id));db.commit()
    return {"success":True}

@router.delete("/{parent_id}/students/{student_id}")
def unlink_student(parent_id:int,student_id:int,admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    row=db.query(ParentStudent).filter(ParentStudent.parent_id==parent_id,ParentStudent.student_id==student_id).first()
    if row: db.delete(row);db.commit()
    return {"success":True}

@router.put("/{parent_id}/deactivate")
def deactivate_parent(parent_id:int,admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    p=db.query(Parent).filter(Parent.id==parent_id).first()
    if not p: raise HTTPException(status_code=404,detail="Ota-ona topilmadi")
    p.is_active=False;p.auth_version=(p.auth_version or 1)+1;db.commit();return {"success":True}

@router.put("/{parent_id}/activate")
def activate_parent(parent_id:int,admin:Admin=Depends(require_admin),db:Session=Depends(get_db)):
    p=db.query(Parent).filter(Parent.id==parent_id).first()
    if not p: raise HTTPException(status_code=404,detail="Ota-ona topilmadi")
    p.is_active=True;p.auth_version=(p.auth_version or 1)+1;db.commit();return {"success":True}
