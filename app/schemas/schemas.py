from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import date, time, datetime
from app.models.models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None

class DoctorAvailabilityBase(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

    @validator('day_of_week')
    def validate_day_of_week(cls, v):
        if v < 0 or v > 6:
            raise ValueError('day_of_week must be between 0 and 6')
        return v

    @validator('end_time')
    def validate_times(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v

class DoctorAvailabilityCreate(DoctorAvailabilityBase):
    pass

class DoctorAvailability(DoctorAvailabilityBase):
    id: int
    doctor_id: int

    class Config:
        from_attributes = True

class TimeSlot(BaseModel):
    start_time: time
    end_time: time
    is_available: bool

class AvailabilityDate(BaseModel):
    date: date
    time_slots: List[TimeSlot]

class AppointmentBase(BaseModel):
    doctor_id: int
    appointment_date: date
    start_time: time

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    patient_id: int
    end_time: time
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    status: str 