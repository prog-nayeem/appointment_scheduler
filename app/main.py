from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database.database import engine, Base, get_db
from app.routers import auth, users, availability, appointments

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Doctor Appointment Scheduler API",
    description="API for scheduling doctor appointments with 40-minute time slots",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # React frontend
    "http://localhost:8000",  # FastAPI docs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(availability.router)
app.include_router(appointments.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Doctor Appointment Scheduler API"}

@app.get("/health-check")
def health_check(db: Session = Depends(get_db)):
    """Check if the API and database connection are working"""
    try:
        # Try to connect to the database
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)} 