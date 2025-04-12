from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Time, Date, Enum
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum
from datetime import datetime, time, date

class UserRole(str, enum.Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    
    doctor_availability = relationship("DoctorAvailability", back_populates="doctor")
    appointments_as_doctor = relationship("Appointment", back_populates="doctor", foreign_keys="Appointment.doctor_id")
    appointments_as_patient = relationship("Appointment", back_populates="patient", foreign_keys="Appointment.patient_id")

class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    day_of_week = Column(Integer)  # 0-6 for Monday-Sunday
    start_time = Column(Time)
    end_time = Column(Time)
    
    doctor = relationship("User", back_populates="doctor_availability")

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("users.id"))
    appointment_date = Column(Date)
    start_time = Column(Time)
    end_time = Column(Time)
    status = Column(String)  # 'scheduled', 'completed', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")
    patient = relationship("User", foreign_keys=[patient_id], back_populates="appointments_as_patient") 