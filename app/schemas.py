from pydantic import BaseModel
from typing import Optional

# -------- PATIENT SCHEMA --------
class PatientCreate(BaseModel):
    name: str
    age: int
    gender: str
    disease: str


class PatientResponse(BaseModel):
    patient_id: int
    name: str
    age: int
    gender: str
    disease: str

    class Config:
        from_attributes = True


# -------- VITALS SCHEMA --------
class VitalsCreate(BaseModel):
    patient_id: int
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int
    respiration_rate: int


class VitalsResponse(BaseModel):
    vital_id: int
    patient_id: int
    heart_rate: int
    spo2: int
    systolic_bp: int
    diastolic_bp: int
    respiration_rate: int

    class Config:
        from_attributes = True
