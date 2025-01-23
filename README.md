# One Health Portal Backend

A comprehensive healthcare management system built with FastAPI, featuring appointment scheduling, patient management, and ML-based disease prediction.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Database Schema](#database-schema)
- [Features](#features)
- [Security](#security)
- [Error Handling](#error-handling)

## Prerequisites

- Python 3.11+
- MySQL Server 8.0+
- pip
- Node.js 18+ (for frontend integration)

## Setup Instructions

### 1. Environment Setup

# Clone repository

git clone <repository-url>
cd portal_backend

# Create virtual environment

python -m venv venv
source venv/bin/activate # Linux/Mac
.\venv\Scripts\activate # Windows

# Install dependencies

pip install -r requirements.txt

### 2. Environment Configuration

Create `.env` file with:

SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=mysql+pymysql://root:root@localhost/onehealthportal

CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name

### 3. Database Setup

CREATE DATABASE onehealthportal;
mysql -u root -p onehealthportal < database.sql

### 4. Start Server

python run.py

## API Documentation

### Authentication Endpoints

| Method | Endpoint                    | Description            | Request Body             | Response                      |
| ------ | --------------------------- | ---------------------- | ------------------------ | ----------------------------- |
| POST   | `/api/auth/register`        | Register new user      | `RegisterRequest`        | `AuthResponse`                |
| POST   | `/api/auth/login`           | User login             | `AuthRequest`            | `AuthResponse`                |
| POST   | `/api/auth/2fa/enable`      | Enable 2FA             | `TwoFactorToggleRequest` | `TwoFactorResponse`           |
| POST   | `/api/auth/2fa/verify`      | Verify 2FA code        | `Verify2FARequest`       | `TwoFactorVerifyResponse`     |
| POST   | `/api/auth/2fa/status`      | Get 2FA status         | -                        | `TwoFactorStatusResponse`     |
| POST   | `/api/auth/reset-password`  | Request password reset | `PasswordResetRequest`   | `AuthResponse`                |
| GET    | `/api/auth/sessions`        | List active sessions   | -                        | `List[SessionDetailResponse]` |
| POST   | `/api/auth/sessions/revoke` | Revoke sessions        | `RevokeSessionRequest`   | `AuthResponse`                |
| POST   | `/api/auth/logout`          | User logout            | -                        | `AuthResponse`                |

### Dashboard Endpoints

| Method | Endpoint                         | Description                 | Response                       |
| ------ | -------------------------------- | --------------------------- | ------------------------------ |
| GET    | `/api/dashboard`                 | Get main dashboard stats    | `DashboardResponse`            |
| GET    | `/api/dashboard/appointments`    | Get appointment analytics   | `List[AppointmentAnalytics]`   |
| GET    | `/api/dashboard/distribution`    | Get department distribution | `List[DepartmentDistribution]` |
| GET    | `/api/dashboard/recent-patients` | Get recent patients         | `List[RecentPatient]`          |

### User Management

| Method | Endpoint                  | Description              | Request Body | Response       |
| ------ | ------------------------- | ------------------------ | ------------ | -------------- |
| GET    | `/api/users/{user_id}`    | Get user details         | -            | `UserResponse` |
| PUT    | `/api/users/{user_id}`    | Update user              | `UserUpdate` | `UserResponse` |
| DELETE | `/api/users/{user_id}`    | Delete user              | -            | -              |
| GET    | `/api/users/profile`      | Get current user profile | -            | `UserResponse` |
| PUT    | `/api/users/profile`      | Update profile           | `UserUpdate` | `UserResponse` |
| POST   | `/api/users/upload-photo` | Upload profile photo     | `File`       | `UserResponse` |

### Doctor Management

| Method | Endpoint                              | Description            | Request Body   | Response               |
| ------ | ------------------------------------- | ---------------------- | -------------- | ---------------------- |
| POST   | `/api/doctors`                        | Create doctor          | `DoctorCreate` | `DoctorResponse`       |
| GET    | `/api/doctors`                        | List all doctors       | -              | `List[DoctorResponse]` |
| GET    | `/api/doctors/{doctor_id}`            | Get doctor details     | -              | `DoctorResponse`       |
| PUT    | `/api/doctors/{doctor_id}`            | Update doctor          | `DoctorUpdate` | `DoctorResponse`       |
| DELETE | `/api/doctors/{doctor_id}`            | Delete doctor          | -              | -                      |
| GET    | `/api/doctors/hospital/{hospital_id}` | List hospital doctors  | -              | `List[DoctorResponse]` |
| GET    | `/api/doctors/specialization/{spec}`  | List by specialization | -              | `List[DoctorResponse]` |

### Hospital Management

| Method | Endpoint                       | Description          | Request Body     | Response                 |
| ------ | ------------------------------ | -------------------- | ---------------- | ------------------------ |
| POST   | `/api/hospitals`               | Create hospital      | `HospitalCreate` | `HospitalResponse`       |
| GET    | `/api/hospitals`               | List all hospitals   | -                | `List[HospitalResponse]` |
| GET    | `/api/hospitals/{hospital_id}` | Get hospital details | -                | `HospitalResponse`       |
| PUT    | `/api/hospitals/{hospital_id}` | Update hospital      | `HospitalUpdate` | `HospitalResponse`       |
| DELETE | `/api/hospitals/{hospital_id}` | Delete hospital      | -                | -                        |
| POST   | `/api/hospitals/upload-logo`   | Upload hospital logo | `File`           | `HospitalResponse`       |

### Appointment Management

| Method | Endpoint                                   | Description                  | Request Body               | Response                     |
| ------ | ------------------------------------------ | ---------------------------- | -------------------------- | ---------------------------- |
| POST   | `/api/appointments`                        | Create appointment           | `AppointmentCreateRequest` | `AppointmentResponse`        |
| GET    | `/api/appointments`                        | List all appointments        | -                          | `List[AppointmentResponse]`  |
| GET    | `/api/appointments/{id}`                   | Get appointment details      | -                          | `AppointmentResponse`        |
| PUT    | `/api/appointments/{id}`                   | Update appointment           | `AppointmentUpdate`        | `AppointmentResponse`        |
| DELETE | `/api/appointments/{id}`                   | Cancel appointment           | -                          | -                            |
| GET    | `/api/appointments/user/{user_id}`         | List user appointments       | -                          | `List[AppointmentResponse]`  |
| GET    | `/api/appointments/doctor/{doctor_id}`     | List doctor appointments     | -                          | `List[AppointmentResponse]`  |
| GET    | `/api/appointments/hospital/{hospital_id}` | List hospital appointments   | -                          | `List[AppointmentResponse]`  |
| POST   | `/api/appointments/timeslots`              | Get available slots          | `TimeSlotRequest`          | `AvailableTimeSlotsResponse` |
| GET    | `/api/appointments/{id}/receipt`           | Generate appointment receipt | -                          | `PDF File`                   |

### Lab Test Management

| Method | Endpoint                                | Description         | Request Body    | Response                 |
| ------ | --------------------------------------- | ------------------- | --------------- | ------------------------ |
| POST   | `/api/lab-tests`                        | Schedule test       | `LabTestCreate` | `LabTestResponse`        |
| GET    | `/api/lab-tests`                        | List all tests      | -               | `List[LabTestResponse]`  |
| GET    | `/api/lab-tests/{id}`                   | Get test details    | -               | `LabTestResponse`        |
| PUT    | `/api/lab-tests/{id}`                   | Update test         | `LabTestUpdate` | `LabTestResponse`        |
| DELETE | `/api/lab-tests/{id}`                   | Cancel test         | -               | -                        |
| GET    | `/api/lab-tests/user/{user_id}`         | List user tests     | -               | `List[LabTestResponse]`  |
| GET    | `/api/lab-tests/hospital/{hospital_id}` | List hospital tests | -               | `List[LabTestResponse]`  |
| POST   | `/api/lab-tests/timeslots`              | Get available slots | -               | `List[TimeSlotResponse]` |

### Payment Management

| Method | Endpoint                                     | Description             | Request Body    | Response          |
| ------ | -------------------------------------------- | ----------------------- | --------------- | ----------------- |
| POST   | `/api/payments`                              | Create payment          | `PaymentCreate` | `PaymentResponse` |
| GET    | `/api/payments/{id}`                         | Get payment details     | -               | `PaymentResponse` |
| PUT    | `/api/payments/{id}`                         | Update payment          | `PaymentUpdate` | `PaymentResponse` |
| GET    | `/api/payments/appointment/{appointment_id}` | Get appointment payment | -               | `PaymentResponse` |

### Feedback Management

| Method | Endpoint                       | Description          | Request Body     | Response                 |
| ------ | ------------------------------ | -------------------- | ---------------- | ------------------------ |
| POST   | `/api/feedback`                | Create feedback      | `FeedbackCreate` | `FeedbackResponse`       |
| GET    | `/api/feedback/{id}`           | Get feedback details | -                | `FeedbackResponse`       |
| PUT    | `/api/feedback/{id}`           | Update feedback      | `FeedbackUpdate` | `FeedbackResponse`       |
| GET    | `/api/feedback/user/{user_id}` | List user feedback   | -                | `List[FeedbackResponse]` |

### Disease Prediction

| Method | Endpoint                              | Description           | Request Body    | Response             |
| ------ | ------------------------------------- | --------------------- | --------------- | -------------------- |
| POST   | `/api/disease-prediction/symptoms`    | Predict from symptoms | `SymptomsInput` | `PredictionResponse` |
| GET    | `/api/disease-prediction/specialties` | List specialties      | -               | `List[str]`          |
| GET    | `/api/disease-prediction/conditions`  | List conditions       | -               | `List[str]`          |

### Hospital-Doctor Management

| Method | Endpoint                                         | Description                    | Request Body           | Response                 |
| ------ | ------------------------------------------------ | ------------------------------ | ---------------------- | ------------------------ |
| POST   | `/api/hospital-doctor`                           | Associate doctor with hospital | `HospitalDoctorCreate` | `HospitalDoctorResponse` |
| GET    | `/api/hospital-doctor/{hospital_id}/{doctor_id}` | Get association details        | -                      | `HospitalDoctorResponse` |
| PUT    | `/api/hospital-doctor/{hospital_id}/{doctor_id}` | Update association             | `HospitalDoctorUpdate` | `HospitalDoctorResponse` |
| DELETE | `/api/hospital-doctor/{hospital_id}/{doctor_id}` | Remove association             | -                      | -                        |

### File Upload

| Method | Endpoint                       | Description             | Request Body | Response         |
| ------ | ------------------------------ | ----------------------- | ------------ | ---------------- |
| POST   | `/api/upload/profile-picture`  | Upload profile picture  | `File`       | `UploadResponse` |
| POST   | `/api/upload/medical-document` | Upload medical document | `File`       | `UploadResponse` |
| POST   | `/api/upload/hospital-logo`    | Upload hospital logo    | `File`       | `UploadResponse` |

### Dashboard Administration

| Method | Endpoint                                | Description               | Request Body | Response                         |
| ------ | --------------------------------------- | ------------------------- | ------------ | -------------------------------- |
| GET    | `/api/dashboard/doctors`                | Get doctor statistics     | -            | `List[DashboardDoctorResponse]`  |
| GET    | `/api/dashboard/patients`               | Get patient statistics    | -            | `List[DashboardPatientResponse]` |
| GET    | `/api/dashboard/revenue`                | Get revenue analytics     | -            | `RevenueAnalyticsResponse`       |
| GET    | `/api/dashboard/appointments/analytics` | Get appointment analytics | -            | `AppointmentAnalyticsResponse`   |
| GET    | `/api/dashboard/performance`            | Get performance metrics   | -            | `PerformanceMetricsResponse`     |

## Database Schema

## Features

### Authentication & Security

- Supabase integration for user management
- Two-factor authentication via email
- JWT token-based authentication
- Role-based access control (Patient/Admin/Staff)

### File Management

- Cloudinary integration for file storage
- Profile picture upload support
- PDF report generation

### ML Integration

- Disease prediction from symptoms
- Confidence scoring
- Specialty recommendations

## Security

### Authentication Flow

1. User registers/logs in through Supabase
2. Backend verifies Supabase JWT
3. Optional 2FA verification
4. Session management with refresh tokens

### Data Protection

- Database connection pooling
- Prepared statements
- Input validation using Pydantic
- Rate limiting on sensitive endpoints
