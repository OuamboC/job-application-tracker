# Job Application Tracker API

## Description
A REST API to track job applications built with FastAPI, SQLModel and SQLite.
Features CRUD operations, pagination, status filtering and JWT authentication.

## Tech Stack
- **FastAPI** - web framework
- **SQLModel** - ORM and data validation
- **SQLite** - database
- **JWT** - authentication
- **pwdlib** - password hashing

## Project Structure
job_application_tracker/
├── main.py
├── models.py
├── database.py
├── routers/
│   ├── applications.py
│   └── auth.py
└── auth/
    └── security.py

## Endpoints
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | /register | ❌ | Register a new user |
| POST | /token | ❌ | Login and get JWT token |
| GET | /users/me | ✅ | Get current user |
| POST | /applications | ❌ | Create application |
| GET | /applications | ❌ | Get all applications |
| GET | /applications/{id} | ❌ | Get one application |
| PATCH | /applications/{id} | ❌ | Update application |
| DELETE | /applications/{id} | ❌ | Delete application |

## How to run
```bash
git clone https://github.com/OuamboC/job-application-tracker
cd job-application-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
fastapi dev main.py
```

## What I learned
- Building REST APIs with FastAPI
- Database management with SQLModel
- JWT authentication and password hashing
- SOLID principles and project structure
- Pagination and filtering