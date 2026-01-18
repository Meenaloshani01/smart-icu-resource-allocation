from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Float,
    TIMESTAMP,
    DateTime
)
from sqlalchemy.sql import func
from app.database import Base


# ---------------- USERS TABLE ----------------
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("ADMIN", "DOCTOR"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)


# ---------------- PATIENTS TABLE ----------------
class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum("Male", "Female", "Other"), nullable=False)
    disease = Column(String(100), nullable=False)
    admission_time = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    status = Column(
        Enum("Stable", "Moderate", "Critical"),
        default="Stable",
        nullable=False
    )


# ---------------- VITALS TABLE ----------------
class Vitals(Base):
    __tablename__ = "vitals"

    vital_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)

    heart_rate = Column(Integer, nullable=False)
    spo2 = Column(Integer, nullable=False)
    systolic_bp = Column(Integer, nullable=False)
    diastolic_bp = Column(Integer, nullable=False)
    respiration_rate = Column(Integer, nullable=False)

    recorded_time = Column(TIMESTAMP, server_default=func.now(), nullable=False)


# ---------------- ICU RESOURCES TABLE ----------------
class ICUResource(Base):
    __tablename__ = "icu_resources"

    resource_id = Column(Integer, primary_key=True, index=True)
    resource_type = Column(Enum("BED", "VENTILATOR"), nullable=False)
    status = Column(Enum("AVAILABLE", "OCCUPIED"), default="AVAILABLE", nullable=False)
    assigned_patient = Column(
        Integer,
        ForeignKey("patients.patient_id"),
        nullable=True
    )


# ---------------- ALLOCATIONS TABLE ----------------
class Allocation(Base):
    __tablename__ = "allocations"

    allocation_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)

    bed_id = Column(Integer, nullable=True)
    ventilator_id = Column(Integer, nullable=True)

    severity_score = Column(Float, nullable=False)
    decision_reason = Column(String(500), nullable=True)

    allocated_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
