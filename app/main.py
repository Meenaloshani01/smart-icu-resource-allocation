from fastapi import FastAPI
from app.database import engine, Base
from app import models
from app.routes import patients, vitals, allocation
from fastapi.middleware.cors import CORSMiddleware
from app.routes import icu

app = FastAPI(title="CTS NPN – Smart ICU Backend")

Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(vitals.router)
app.include_router(allocation.router)
app.include_router(icu.router)

@app.get("/")
def root():
    return {"message": "CTS NPN Backend Connected Successfully"}
