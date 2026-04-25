# Task Management API

A production-grade REST API built with FastAPI, PostgreSQL, and JWT authentication.
Deployed on Railway with Docker and Alembic migrations.

## Live Demo

API Docs: https://task-management-api-production-49fc.up.railway.app/docs

## Features

- JWT Authentication — register, login, protected routes
- Full Task CRUD — create, read, update, delete
- Task Ownership — users can only access their own tasks
- Filtering — filter tasks by status and priority
- Search — search tasks by title
- Sorting — sort by created date, due date, or priority
- Pagination — skip and limit support
- Global error handling — consistent error responses
- Full pytest test suite — auth and task tests with isolated test database
- Docker + docker-compose — runs locally with one command
- Alembic migrations — safe schema management
- Deployed on Railway with PostgreSQL

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Auth | JWT (python-jose, passlib) |
| Validation | Pydantic v2 |
| Testing | pytest, httpx |
| Container | Docker, docker-compose |
| Deployment | Railway |

## Project Structure

```
Task_Manager/
├── app/
│   ├── main.py           # App setup, middleware, routers
│   ├── config.py         # Pydantic Settings
│   ├── database.py       # Engine, SessionLocal, get_db
│   ├── models/
│   │   ├── db_models.py  # SQLAlchemy models
│   │   └── schemas.py    # Pydantic schemas
│   ├── routers/
│   │   ├── auth.py       # Register, login, me
│   │   └── tasks.py      # Task CRUD, filters, pagination
│   └── core/
│       └── auth.py       # JWT logic
├── tests/
│   ├── conftest.py       # Test database, fixtures
│   ├── test_auth.py      # Auth tests
│   └── test_tasks.py     # Task CRUD tests
├── alembic/              # Database migrations
├── Dockerfile
├── docker-compose.yml
├── railway.toml
└── requirements.txt
```

## API Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /auth/register | Register new user | No |
| POST | /auth/login | Login, get JWT token | No |
| GET | /auth/me | Get current user | Yes |

### Tasks
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /tasks/ | Create a task | Yes |
| GET | /tasks/ | Get all your tasks | Yes |
| GET | /tasks/{id} | Get a single task | Yes |
| PUT | /tasks/{id} | Update a task | Yes |
| DELETE | /tasks/{id} | Delete a task | Yes |

### Query Parameters for GET /tasks/
| Parameter | Type | Description |
|-----------|------|-------------|
| status | enum | Filter: todo, in_progress, done |
| priority | enum | Filter: low, medium, high |
| search | string | Search by title |
| sort_by | enum | created_at, due_date, priority |
| order | enum | asc, desc |
| skip | int | Pagination offset |
| limit | int | Results per page (max 100) |

## Local Setup

### With Docker (recommended)

```bash
git clone https://github.com/vishnurajt/task-management-api.git
cd task-management-api
docker-compose up -d
docker-compose exec web alembic upgrade head
```

Open http://localhost:8000/docs

### Without Docker

```bash
git clone https://github.com/vishnurajt/task-management-api.git
cd task-management-api
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
# Set DATABASE_URL=sqlite:///./taskmanager.db in .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| DATABASE_URL | PostgreSQL or SQLite connection URL |
| SECRET_KEY | JWT signing secret |
| ALGORITHM | JWT algorithm — HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry in minutes |

## Running Tests

```bash
pytest tests/ -v
```

## Author

Vishnuraj T — Python Backend Engineer
GitHub: github.com/vishnurajt