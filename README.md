# One Health Portal Backend

A comprehensive healthcare management system built with **FastAPI**, featuring appointment scheduling, patient management, and ML-based disease prediction. This backend powers the One Health Portal, providing APIs for user authentication, appointment management, lab test scheduling, and more.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setup Instructions](#setup-instructions)
3. [API Documentation](#api-documentation)
4. [Database Schema](#database-schema)
5. [Security](#security)

---

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.11+**
- **MySQL Server 8.0+**
- **pip** (Python package manager)
- **Node.js 18+** (for frontend integration, if applicable)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone [<repository-url>](https://github.com/One-Health-Portal/onehealth_portal_backend.git)
cd portal_backend
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
DATABASE_URL=mysql+pymysql://root:root@localhost/onehealthportal

CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_secret
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

### 5. Set Up the Database

1. Import the database:
   ```sql
   CREATE DATABASE onehealthportal;
   ```

2. Import the database schema:
   ```bash
   mysql -u root -p onehealthportal < database.sql
   ```

### 6. Start the Server

```bash
python run.py
```

The backend server will start running at `http://localhost:8000`.

---

## API Documentation

The backend provides a comprehensive set of APIs for managing users, appointments, lab tests, and more. Below is a summary of the available endpoints.

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

---

## Database Schema

The database schema includes tables for users, appointments, lab tests, hospitals, doctors, and more. Below is a high-level overview:

- **Users**: Stores user information (patients, doctors, admins).
- **Appointments**: Manages appointment details (date, time, doctor, patient).
- **LabTests**: Tracks lab test schedules and results.
- **Hospitals**: Stores hospital information.
- **Doctors**: Manages doctor profiles and specialties.
- **Payments**: Tracks payment details for appointments and lab tests.

For the full schema, refer to the `database.sql` file.

---

## Security

### Authentication Flow

1. User registers/logs in through Supabase.
2. Backend verifies Supabase JWT.
3. Optional 2FA verification.
4. Session management with refresh tokens.

### Data Protection

- **Database Connection Pooling**: Ensures efficient and secure database connections.
- **Prepared Statements**: Prevents SQL injection attacks.
- **Input Validation**: Uses Pydantic for robust input validation.
- **Rate Limiting**: Protects sensitive endpoints from abuse.

---
