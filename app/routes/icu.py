from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ICUResource
from app import models

router = APIRouter(prefix="/icu", tags=["ICU"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status")
def get_icu_status(db: Session = Depends(get_db)):
    beds_available = db.query(ICUResource).filter(
        ICUResource.resource_type == "BED",
        ICUResource.status == "AVAILABLE"
    ).count()

    ventilators_available = db.query(ICUResource).filter(
        ICUResource.resource_type == "VENTILATOR",
        ICUResource.status == "AVAILABLE"
    ).count()

    return {
        "beds_available": beds_available,
        "ventilators_available": ventilators_available
    }
@router.get("/severity-stats")
def severity_stats(db: Session = Depends(get_db)):
    return {
        "Stable": db.query(models.Patient).filter(models.Patient.status == "Stable").count(),
        "Moderate": db.query(models.Patient).filter(models.Patient.status == "Moderate").count(),
        "Critical": db.query(models.Patient).filter(models.Patient.status == "Critical").count()
    }
