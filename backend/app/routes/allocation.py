from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import models

# Rule-based model
from app.ml.severity_model import predict_severity

# Logistic Regression model
from app.ml.lr_severity_model import predict_severity_ml


router = APIRouter(prefix="/allocate", tags=["ICU Allocation"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- Severity Explanation ----------------
def generate_severity_reasons(vitals):
    reasons = []

    if vitals["spo2"] < 92:
        reasons.append("Low oxygen saturation (SpO₂)")

    if vitals["heart_rate"] > 100:
        reasons.append("High heart rate")

    if vitals["heart_rate"] < 60:
        reasons.append("Low heart rate")

    if vitals["systolic_bp"] > 140:
        reasons.append("High systolic blood pressure")

    if vitals["diastolic_bp"] > 90:
        reasons.append("High diastolic blood pressure")

    if vitals["respiration_rate"] > 24:
        reasons.append("Abnormal respiration rate")

    if not reasons:
        reasons.append("Vitals are within normal range")

    return reasons
@router.get("/timeline")
def allocation_timeline(db: Session = Depends(get_db)):
    records = (
        db.query(models.Allocation)
        .order_by(models.Allocation.allocated_time.desc())
        .limit(10)
        .all()
    )

    return [
        {
            "patient_id": r.patient_id,
            "severity_score": r.severity_score,
            "bed_id": r.bed_id,
            "ventilator_id": r.ventilator_id,
            "time": r.allocated_time
        }
        for r in records
    ]


@router.post("/{patient_id}")
def allocate_resources(patient_id: int, db: Session = Depends(get_db)):

    # 1️⃣ Get latest vitals
    vitals = (
        db.query(models.Vitals)
        .filter(models.Vitals.patient_id == patient_id)
        .order_by(models.Vitals.recorded_time.desc())
        .first()
    )

    if not vitals:
        raise HTTPException(status_code=404, detail="Vitals not found")

    vitals_data = {
        "heart_rate": vitals.heart_rate,
        "spo2": vitals.spo2,
        "systolic_bp": vitals.systolic_bp,
        "diastolic_bp": vitals.diastolic_bp,
        "respiration_rate": vitals.respiration_rate
    }

    reasons = generate_severity_reasons(vitals_data)

    # 2️⃣ Rule-based prediction
    rule_score, rule_severity = predict_severity(vitals_data)

    # 3️⃣ ML-based prediction (safe fallback)
    try:
        ml_confidence, ml_severity = predict_severity_ml(vitals_data)
    except Exception:
        ml_confidence = rule_score
        ml_severity = rule_severity

    # 4️⃣ Final decision → ML preferred
    final_severity = ml_severity
    final_score = ml_confidence

    # 5️⃣ Find ICU bed
    bed = db.query(models.ICUResource).filter(
        models.ICUResource.resource_type == "BED",
        models.ICUResource.status == "AVAILABLE"
    ).first()

    if not bed:
        raise HTTPException(status_code=503, detail="No ICU bed available")

    bed.status = "OCCUPIED"
    bed.assigned_patient = patient_id

    # 6️⃣ Ventilator only if Critical
    ventilator = None
    if final_severity == "Critical":
        ventilator = db.query(models.ICUResource).filter(
            models.ICUResource.resource_type == "VENTILATOR",
            models.ICUResource.status == "AVAILABLE"
        ).first()

        if ventilator:
            ventilator.status = "OCCUPIED"
            ventilator.assigned_patient = patient_id

    # 7️⃣ Log allocation
    allocation = models.Allocation(
        patient_id=patient_id,
        bed_id=bed.resource_id,
        ventilator_id=ventilator.resource_id if ventilator else None,
        severity_score=final_score,
        decision_reason=f"Final decision based on ML: {final_severity}"
    )

    # 8️⃣ Update patient status
    patient = db.query(models.Patient).filter(
        models.Patient.patient_id == patient_id
    ).first()

    if patient:
        patient.status = final_severity

    db.add(allocation)
    db.commit()

    # 9️⃣ FINAL RESPONSE (for UI + VIVA)
    return {
        "patient_id": patient_id,

        "rule_based": {
            "severity": rule_severity,
            "score": rule_score
        },

        "ml_based": {
            "severity": ml_severity,
            "confidence": ml_confidence
        },

        "final_decision": final_severity,

        "bed_allocated": bed.resource_id,
        "ventilator_allocated": ventilator.resource_id if ventilator else None,
        "reasons": reasons
    }
