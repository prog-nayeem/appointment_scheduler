from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from app.database.database import get_db
from app.models.models import Appointment, User
from app.schemas.schemas import AppointmentCreate, Appointment as AppointmentSchema, AppointmentUpdate, AvailabilityDate
from app.utils.auth import get_current_active_user
from app.utils.schedule import get_doctor_available_slots, book_appointment

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"]
)

@router.get("/doctor/{doctor_id}/slots", response_model=AvailabilityDate)
def get_available_slots(
    doctor_id: int,
    date: date = Query(..., description="Date to check for available slots"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get available appointment slots for a doctor on a specific date"""
    # Check if the doctor exists
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    
    # Get available slots
    return get_doctor_available_slots(db, doctor_id, date)

@router.post("/", response_model=AppointmentSchema)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Book a new appointment"""
    # Only patients can book appointments
    if current_user.role != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can book appointments"
        )
    
    try:
        new_appointment = book_appointment(
            db=db,
            doctor_id=appointment.doctor_id,
            patient_id=current_user.id,
            appointment_date=appointment.appointment_date,
            start_time=appointment.start_time
        )
        return new_appointment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[AppointmentSchema])
def get_user_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    start_date: date = Query(None, description="Filter by start date"),
    end_date: date = Query(None, description="Filter by end date")
):
    """Get all appointments for the current user"""
    query = None
    
    if current_user.role == "doctor":
        query = db.query(Appointment).filter(Appointment.doctor_id == current_user.id)
    else:  # patient
        query = db.query(Appointment).filter(Appointment.patient_id == current_user.id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Appointment.appointment_date >= start_date)
    
    if end_date:
        query = query.filter(Appointment.appointment_date <= end_date)
    
    # Order by date and time
    appointments = query.order_by(Appointment.appointment_date, Appointment.start_time).all()
    
    return appointments

@router.get("/{appointment_id}", response_model=AppointmentSchema)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific appointment"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if the user has permission to view this appointment
    if (current_user.role == "doctor" and appointment.doctor_id != current_user.id) or \
       (current_user.role == "patient" and appointment.patient_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this appointment"
        )
    
    return appointment

@router.patch("/{appointment_id}", response_model=AppointmentSchema)
def update_appointment_status(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an appointment status"""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check if the user has permission to update this appointment
    if (current_user.role == "doctor" and appointment.doctor_id != current_user.id) or \
       (current_user.role == "patient" and appointment.patient_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this appointment"
        )
    
    # Validate the status value
    valid_statuses = ["scheduled", "completed", "cancelled"]
    if update_data.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status must be one of: {', '.join(valid_statuses)}"
        )
    
    # Update the appointment
    appointment.status = update_data.status
    db.commit()
    db.refresh(appointment)
    
    return appointment 