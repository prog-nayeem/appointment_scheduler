from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models.models import DoctorAvailability
from app.schemas.schemas import DoctorAvailabilityCreate, DoctorAvailability as DoctorAvailabilitySchema
from app.utils.auth import get_current_active_user, get_doctor_user
from app.models.models import User

router = APIRouter(
    prefix="/availability",
    tags=["availability"]
)

@router.post("/", response_model=DoctorAvailabilitySchema)
def create_availability(
    availability: DoctorAvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_doctor_user)
):
    """Create a new availability slot for the doctor"""
    # Check for overlapping availabilities for the same day
    overlapping = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == current_user.id,
        DoctorAvailability.day_of_week == availability.day_of_week,
        # Check for any overlap in time ranges
        ((DoctorAvailability.start_time <= availability.start_time) & 
         (DoctorAvailability.end_time > availability.start_time)) |
        ((DoctorAvailability.start_time < availability.end_time) & 
         (DoctorAvailability.end_time >= availability.end_time)) |
        ((DoctorAvailability.start_time >= availability.start_time) & 
         (DoctorAvailability.end_time <= availability.end_time))
    ).first()
    
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Overlapping availability exists for this day"
        )
    
    db_availability = DoctorAvailability(
        doctor_id=current_user.id,
        day_of_week=availability.day_of_week,
        start_time=availability.start_time,
        end_time=availability.end_time
    )
    
    db.add(db_availability)
    db.commit()
    db.refresh(db_availability)
    return db_availability

@router.get("/", response_model=List[DoctorAvailabilitySchema])
def get_doctor_availabilities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_doctor_user)
):
    """Get all availability slots for the current doctor"""
    availabilities = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == current_user.id
    ).all()
    
    return availabilities

@router.get("/{doctor_id}", response_model=List[DoctorAvailabilitySchema])
def get_specific_doctor_availabilities(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all availability slots for a specific doctor"""
    # Check if the doctor exists
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    availabilities = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id
    ).all()
    
    return availabilities

@router.delete("/{availability_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_availability(
    availability_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_doctor_user)
):
    """Delete an availability slot"""
    db_availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.id == availability_id,
        DoctorAvailability.doctor_id == current_user.id
    ).first()
    
    if not db_availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Availability not found or not owned by you"
        )
    
    db.delete(db_availability)
    db.commit()
    
    return None 