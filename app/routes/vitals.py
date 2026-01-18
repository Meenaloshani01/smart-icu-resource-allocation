from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models


from app.schemas import VitalsCreate, VitalsResponse

router = APIRouter(prefix="/vitals", tags=["Vitals"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- ADD VITALS --------
@router.post("/add", response_model=VitalsResponse)
def add_vitals(vitals: VitalsCreate, db: Session = Depends(get_db)):
    new_vitals = models.Vitals(**vitals.dict())
    db.add(new_vitals)
    db.commit()
    db.refresh(new_vitals)
    return new_vitals

# -------- GET VITALS BY PATIENT --------
@router.get("/{patient_id}")
def get_vitals(patient_id: int, db: Session = Depends(get_db)):
    return db.query(models.Vitals).filter(
        models.Vitals.patient_id == patient_id
    ).all()
