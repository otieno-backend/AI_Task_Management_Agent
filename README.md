# Task Management API

A production-style **REST API for managing tasks**, built to help users organize, prioritize, track, and complete their work through a secure backend service.

The project demonstrates practical backend development using **Python, Django REST Framework, PostgreSQL, Docker, automated testing, caching, and cloud deployment**.

## 🌐 Live API

**Base URL:**
https://task-management-api-wpw5.onrender.com/api/

The API is deployed on Render and can be used to explore the backend.

---

## 🎯 The Problem

Managing tasks becomes difficult when users need more than simple to-do lists.

A useful task management system should allow users to:

* Create and manage their own tasks
* Track progress
* Set priorities and deadlines
* Organize tasks into categories
* Filter and sort tasks
* Handle recurring work
* Protect user data
* Provide a reliable API that frontend or mobile applications can consume

## 💡 The Solution

I built this API as a backend service that provides these capabilities through RESTful endpoints.

The system handles authentication, task ownership, task workflows, filtering, recurring tasks, validation, automated testing, database operations, and deployment.

The API can serve as the backend for a **web application, mobile application, or other client application**.

---

# 🚀 Key Features

### 🔐 Authentication & User Management

* User registration
* User login
* Token-based authentication
* User logout
* Protected endpoints
* User-specific task access
* Permission-based access

### 📋 Task Management

Users can:

* Create tasks
* View tasks
* Update tasks
* Delete tasks
* Complete tasks
* Set due dates
* Set priorities
* Assign categories
* Track completion time

### 🔄 Task Workflow

Tasks support:

```text
PENDING
   ↓
IN_PROGRESS
   ↓
COMPLETED
```

Tasks can also be marked:

```text
CANCELLED
```

When a task is completed, the API records its completion time.

### 🔁 Recurring Tasks

The API supports:

* Daily tasks
* Weekly tasks
* Monthly tasks

When a recurring task is completed, the system can automatically create the next task based on its recurrence setting.

### 🔎 Filtering

Tasks can be filtered by:

* Status
* Priority
* Due date
* Category

Example:

```text
/api/tasks/?status=PENDING&priority=HIGH
```

### ↕️ Ordering

Tasks can be ordered by:

* Due date
* Priority

Example:

```text
/api/tasks/?ordering=-due_date
```

### 📄 Pagination

Task results are paginated to make the API more practical when working with larger datasets.

### ⚡ Caching

The project includes caching support to reduce unnecessary database operations and improve API performance.

### 🧪 Automated Testing

The project includes automated tests covering important backend behavior such as:

* User creation
* Authentication
* Task creation
* Task status changes
* Task completion
* Recurring tasks
* Filtering
* Ordering
* Category functionality

Run the tests with:

```bash
pytest -v
```

### 🐳 Docker

The application includes Docker configuration for consistent development and deployment environments.

```bash
docker compose up --build
```

### ☁️ Deployment

The API is deployed on **Render** using Django and Gunicorn.

The deployment demonstrates experience with:

* Production Django settings
* PostgreSQL
* Gunicorn
* Docker
* Static files
* Environment configuration
* Cloud deployment

---

# 🛠️ Technology Stack

| Technology            | Purpose                           |
| --------------------- | --------------------------------- |
| Python                | Backend programming               |
| Django                | Web framework                     |
| Django REST Framework | REST API development              |
| PostgreSQL            | Relational database               |
| Redis                 | Caching/background infrastructure |
| Celery                | Background task processing        |
| Docker                | Containerization                  |
| Gunicorn              | Production application server     |
| Pytest                | Automated testing                 |
| Render                | Cloud deployment                  |
| Git/GitHub            | Version control                   |

---

# 🏗️ Project Structure

```text
Task_Management_API/
│
├── accounts/                 # Authentication and user functionality
├── Tasks/                    # Task management functionality
├── taskhub/                  # Django project configuration
├── Dockerfile                # Docker configuration
├── docker-compose.yml        # Container configuration
├── requirements.txt          # Python dependencies
├── pytest.ini                # Test configuration
└── manage.py                 # Django management commands
```

---

# ⚙️ Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/otieno-backend/Task_Management_API.git
cd Task_Management_API
```

## 2. Create a virtual environment

```bash
python -m venv venv
```

## 3. Activate the virtual environment

### Windows

```bash
venv\Scripts\activate
```

### Linux/macOS

```bash
source venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run migrations

```bash
python manage.py migrate
```

## 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

---

# 🔐 Authentication

The API uses token-based authentication.

After logging in, include the token in protected requests:

```http
Authorization: Token YOUR_TOKEN
```

---

# 📋 API Endpoints

| Method | Endpoint                    | Description       |
| ------ | --------------------------- | ----------------- |
| POST   | `/api/register/`            | Register a user   |
| POST   | `/api/login/`               | Login             |
| POST   | `/api/logout/`              | Logout            |
| GET    | `/api/tasks/`               | List tasks        |
| POST   | `/api/tasks/`               | Create a task     |
| GET    | `/api/tasks/<id>/`          | Get a task        |
| PATCH  | `/api/tasks/<id>/`          | Update a task     |
| DELETE | `/api/tasks/<id>/`          | Delete a task     |
| PATCH  | `/api/tasks/<id>/complete/` | Complete a task   |
| GET    | `/api/categories/`          | List categories   |
| POST   | `/api/categories/`          | Create a category |
| GET    | `/api/user/dashboard/`      | User dashboard    |
| GET    | `/api/admin/dashboard/`     | Admin dashboard   |

---

# 📝 Example: Create a Task

```http
POST /api/tasks/
Authorization: Token YOUR_TOKEN
Content-Type: application/json
```

```json
{
  "title": "Complete Django API project",
  "description": "Finish API documentation and testing",
  "priority": "HIGH",
  "status": "PENDING",
  "recurrence": "NONE"
}
```

The authenticated user is automatically associated with the task.

---

# 🔄 Example: Complete a Task

```http
PATCH /api/tasks/1/complete/
Authorization: Token YOUR_TOKEN
```

When a task is completed:

* Its status changes to `COMPLETED`
* `completed_at` is recorded
* If the task is recurring, the next task can be created automatically

---

# 🗂️ Task Fields

| Field          | Description            |
| -------------- | ---------------------- |
| `title`        | Task title             |
| `description`  | Task description       |
| `due_date`     | Optional deadline      |
| `priority`     | Task priority          |
| `status`       | Current task status    |
| `category_id`  | Optional category      |
| `recurrence`   | Recurring task setting |
| `completed_at` | Completion timestamp   |
| `created_at`   | Creation timestamp     |
| `updated_at`   | Last update timestamp  |

### Priority Values

```text
LOW
MEDIUM
HIGH
```

### Status Values

```text
PENDING
IN_PROGRESS
COMPLETED
CANCELLED
```

### Recurrence Values

```text
NONE
DAILY
WEEKLY
MONTHLY
```

---

# 🔎 Filtering Examples

### Filter by status

```text
/api/tasks/?status=COMPLETED
```

### Filter by priority

```text
/api/tasks/?priority=HIGH
```

### Filter by due date

```text
/api/tasks/?due_date=2026-10-01
```

### Filter by category

```text
/api/tasks/?category=Work
```

### Combine filters

```text
/api/tasks/?status=PENDING&priority=HIGH
```

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest -v
```

The tests help verify important application behavior before changes are deployed.

---

# 🐳 Running with Docker

Build and start the application:

```bash
docker compose up --build
```

Docker provides a consistent environment for running the application and its supporting services.

---

# ☁️ Production Deployment

The application is deployed on Render.

The deployment demonstrates practical experience with:

* Django production configuration
* PostgreSQL
* Gunicorn
* Docker
* Static files
* Environment variables
* Cloud deployment
* Production debugging

**Live API:**

https://task-management-api-wpw5.onrender.com/api/

---

# 🧠 What This Project Demonstrates

This project is more than a CRUD application.

It demonstrates my ability to:

* Design RESTful APIs
* Build backend systems with Django
* Work with relational databases
* Implement authentication and permissions
* Build user-specific data access
* Design task workflows
* Implement filtering and ordering
* Handle recurring business logic
* Write automated tests
* Containerize applications
* Work with caching and background processing
* Deploy backend applications
* Debug and improve production-style applications

---

# 📈 Development Approach

The project was developed incrementally, with features added and tested step by step.

The development process focused on:

```text
Problem
   ↓
Design
   ↓
Implementation
   ↓
Testing
   ↓
Debugging
   ↓
Deployment
   ↓
Improvement
```

This approach helped turn the project from a basic task API into a more production-oriented backend service.

---

# 🔮 Future Improvements

Planned improvements include:

* More comprehensive API documentation
* CI/CD with GitHub Actions
* Improved production monitoring
* Application logging and metrics
* Performance improvements
* Additional background-processing features
* Expanded test coverage

---

# 👨‍💻 Author

**Brian Otieno**

Backend Developer focused on:

* Python
* Django
* Django REST Framework
* PostgreSQL
* REST APIs
* Docker

GitHub:
https://github.com/otieno-backend

---

# ⭐ Project

If you find the project useful, feel free to **star the repository**.

Repository:

https://github.com/otieno-backend/Task_Management_API
