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
- **python-dotenv** - environment variables management

## Project Structure
```
job_application_tracker/
├── main.py
├── models.py
├── database.py
├── requirements.txt
├── routers/
│   ├── applications.py
│   └── auth.py
└── auth/
    └── security.py
```

## Endpoints
| Method | URL | Auth | Description |
|--------|-----|------|-------------|
| POST | /register | No | Register a new user |
| POST | /token | No | Login and get JWT token |
| GET | /users/me | Yes | Get current logged in user |
| POST | /applications | Yes | Create application |
| GET | /applications | No | Get all applications |
| GET | /applications/{id} | No | Get one application |
| PATCH | /applications/{id} | Yes | Update application |
| DELETE | /applications/{id} | Yes | Delete application |

## How to run
```bash
git clone https://github.com/OuamboC/job-application-tracker
cd job-application-tracker
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the root directory:
```
SECRET_KEY=your_secret_key_here
```

Generate your secret key with:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Then run:
```bash
fastapi dev main.py
```

## API Documentation
Once running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## What I learned
- Building REST APIs with FastAPI
- Database management with SQLModel
- JWT authentication and password hashing in Python
- Pagination and status filtering
- Environment variables management with python-dotenv
- Project structure following SOLID principles


