# Doctor Appointment Scheduler API

A FastAPI-based application for scheduling doctor appointments with 40-minute time slots.

## Features

- User authentication (doctors and patients)
- Doctors can set their availability by day of week and time
- Patients can book available 40-minute appointment slots
- Appointment management (create, view, update status)
- PostgreSQL database for data storage

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/appointment_scheduler.git
cd appointment_scheduler/backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the database:

   - Create a PostgreSQL database named `appointment_scheduler`
   - Update `.env` file with your database credentials

5. Run the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.

## API Documentation

Once the app is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- POST `/register` - Register a new user (doctor or patient)
- POST `/token` - Login and get access token

### Users

- GET `/users/me` - Get current user information
- GET `/users/doctors` - Get all doctors
- GET `/users/{user_id}` - Get a specific user's information

### Availability

- POST `/availability` - Create a new availability slot (doctors only)
- GET `/availability` - Get all availability slots for the current doctor
- GET `/availability/{doctor_id}` - Get all availability slots for a specific doctor
- DELETE `/availability/{availability_id}` - Delete an availability slot

### Appointments

- GET `/appointments/doctor/{doctor_id}/slots` - Get available slots for a doctor on a specific date
- POST `/appointments` - Book a new appointment
- GET `/appointments` - Get all appointments for the current user
- GET `/appointments/{appointment_id}` - Get a specific appointment
- PATCH `/appointments/{appointment_id}` - Update an appointment status
