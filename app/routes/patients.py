from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models


from app.schemas import PatientCreate, PatientResponse

router = APIRouter(prefix="/patients", tags=["Patients"])

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- ADD PATIENT --------
@router.post("/add", response_model=PatientResponse)
def add_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    new_patient = models.Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        disease=patient.disease
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # IMPORTANT: return ORM object, not custom dict
    return new_patient

@router.get("/history")
def patient_history(db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()

    return [
        {
            "patient_id": p.patient_id,
            "name": p.name,
            "status": p.status
        }
        for p in patients
    ]


# -------- GET ALL PATIENTS --------
@router.get("/all")
def get_patients(db: Session = Depends(get_db)):
    return db.query(models.Patient).all()
