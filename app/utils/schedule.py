from datetime import datetime, timedelta, time, date
from typing import List, Dict
from sqlalchemy.orm import Session
from app.models.models import DoctorAvailability, Appointment, User
from app.schemas.schemas import TimeSlot, AvailabilityDate

def get_day_of_week(date_obj: date) -> int:
    """Get day of week (0-6, Monday is 0)"""
    # Convert from Python's day of week (0-6, Monday is 0) to our model's format
    return date_obj.weekday()

def create_time_slots(start_time: time, end_time: time, slot_duration: int = 40) -> List[Dict[str, time]]:
    """
    Create time slots of specified duration between start and end times
    Returns list of dicts with start_time and end_time
    """
    slots = []
    current_time = datetime.combine(date.today(), start_time)
    end_datetime = datetime.combine(date.today(), end_time)
    
    while current_time + timedelta(minutes=slot_duration) <= end_datetime:
        slot_end = current_time + timedelta(minutes=slot_duration)
        slots.append({
            "start_time": current_time.time(),
            "end_time": slot_end.time()
        })
        current_time = slot_end
    
    return slots

def get_doctor_available_slots(
    db: Session, 
    doctor_id: int, 
    check_date: date,
    slot_duration: int = 40
) -> AvailabilityDate:
    """
    Get all available time slots for a given doctor on a specific date
    """
    # Get day of week (0-6) from the date
    day_of_week = get_day_of_week(check_date)
    
    # Get doctor's availability for this day of week
    availabilities = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.day_of_week == day_of_week
    ).all()
    
    # If doctor is not available on this day
    if not availabilities:
        return AvailabilityDate(date=check_date, time_slots=[])
    
    # Get all appointments for this doctor on this date
    existing_appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == check_date,
        Appointment.status != "cancelled"
    ).all()
    
    # Create a list to store all available slots
    all_time_slots = []
    
    # For each availability timeframe
    for availability in availabilities:
        # Create all possible slots within this availability
        slots = create_time_slots(
            availability.start_time, 
            availability.end_time, 
            slot_duration
        )
        
        # Mark slots as available or not based on existing appointments
        for slot in slots:
            is_available = True
            
            for appointment in existing_appointments:
                # If appointment overlaps with this slot, mark as unavailable
                appt_start = appointment.start_time
                appt_end = appointment.end_time
                
                if (slot["start_time"] < appt_end and slot["end_time"] > appt_start):
                    is_available = False
                    break
            
            all_time_slots.append(
                TimeSlot(
                    start_time=slot["start_time"],
                    end_time=slot["end_time"],
                    is_available=is_available
                )
            )
    
    return AvailabilityDate(date=check_date, time_slots=all_time_slots)

def book_appointment(
    db: Session,
    doctor_id: int,
    patient_id: int,
    appointment_date: date,
    start_time: time,
    slot_duration: int = 40
) -> Appointment:
    """Book an appointment if the slot is available"""
    
    # Calculate end time
    start_datetime = datetime.combine(date.today(), start_time)
    end_datetime = start_datetime + timedelta(minutes=slot_duration)
    end_time = end_datetime.time()
    
    # Check if the doctor exists and is active
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor", User.is_active == True).first()
    if not doctor:
        raise ValueError("Doctor not found or not active")
    
    # Check if the patient exists and is active
    patient = db.query(User).filter(User.id == patient_id, User.role == "patient", User.is_active == True).first()
    if not patient:
        raise ValueError("Patient not found or not active")
    
    # Check if the slot is available
    day_of_week = get_day_of_week(appointment_date)
    
    # Check if doctor is available on this day
    availability = db.query(DoctorAvailability).filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.day_of_week == day_of_week,
        DoctorAvailability.start_time <= start_time,
        DoctorAvailability.end_time >= end_time
    ).first()
    
    if not availability:
        raise ValueError("The doctor is not available at this time")
    
    # Check if there's any conflicting appointment
    conflicting_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == appointment_date,
        Appointment.status != "cancelled",
        # Check for overlap
        ((Appointment.start_time <= start_time) & (Appointment.end_time > start_time)) |
        ((Appointment.start_time < end_time) & (Appointment.end_time >= end_time)) |
        ((Appointment.start_time >= start_time) & (Appointment.end_time <= end_time))
    ).first()
    
    if conflicting_appointment:
        raise ValueError("This time slot is already booked")
    
    # Create new appointment
    new_appointment = Appointment(
        doctor_id=doctor_id,
        patient_id=patient_id,
        appointment_date=appointment_date,
        start_time=start_time,
        end_time=end_time,
        status="scheduled"
    )
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    
    return new_appointment 