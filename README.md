# Task Management API

A production-style RESTful Task Management API built with **Python, Django REST Framework, and PostgreSQL**.

The API provides authenticated users with tools to create and manage tasks, update task status, organize tasks by category and priority, filter and order results, and manage recurring tasks.

## 🌐 Live API

**Base URL:**
https://task-management-api-wpw5.onrender.com/api/

The API is deployed on **Render** and can be used for testing.

## 🚀 Features

* User authentication
* Authenticated task management
* Create, view, update, and delete tasks
* Task status workflow

  * Pending
  * In Progress
  * Completed
  * Cancelled
* Task priority management
* Task categories
* Filtering by task fields
* Ordering and sorting
* Recurring tasks

  * Daily
  * Weekly
  * Monthly
* Automatic handling of completed recurring tasks
* Automated tests
* PostgreSQL database support
* Docker support
* Production deployment with Gunicorn
* Render deployment

## 🛠️ Tech Stack

* **Python**
* **Django**
* **Django REST Framework**
* **PostgreSQL**
* **Docker**
* **Gunicorn**
* **Pytest**
* **Render**

## 🏗️ Project Structure

```text
Task_Management_API/
│
├── accounts/              # User authentication and account functionality
├── Tasks/                 # Task management functionality
├── taskhub/               # Django project configuration
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Local container configuration
├── requirements.txt       # Python dependencies
└── manage.py              # Django management commands
```

## ⚙️ Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/otieno-backend/Task_Management_API.git

cd Task_Management_API
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/macOS

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

## 🔐 Authentication

The API uses token-based authentication.

After authentication, include the token in API requests:

```text
Authorization: Token YOUR_TOKEN
```

Authenticated users can access and manage their tasks according to the application's permissions.

## 📋 Example API Endpoints

| Method    | Endpoint           | Description         |
| --------- | ------------------ | ------------------- |
| POST      | `/api/...`         | User authentication |
| GET       | `/api/tasks/`      | List tasks          |
| POST      | `/api/tasks/`      | Create a task       |
| GET       | `/api/tasks/<id>/` | View a task         |
| PUT/PATCH | `/api/tasks/<id>/` | Update a task       |
| DELETE    | `/api/tasks/<id>/` | Delete a task       |

> Check the project's URL configuration for the complete list of available endpoints.

## 🔎 Task Management

Tasks support several fields and workflows, including:

* Title
* Description
* Status
* Priority
* Category
* Due date
* Recurrence

Supported statuses:

```text
PENDING
IN_PROGRESS
COMPLETED
CANCELLED
```

Supported recurrence options:

```text
NONE
DAILY
WEEKLY
MONTHLY
```

## 🧪 Testing

The project includes automated tests covering important API behavior, including:

* Task creation
* Authentication
* Task status changes
* Task completion
* Recurring task behavior
* Category filtering
* Status filtering
* Priority filtering
* Ordering

Run the test suite with:

```bash
pytest -v
```

## 🐳 Docker

The project includes Docker configuration for running the application in containers.

Build and start the services with:

```bash
docker compose up --build
```

## 🚀 Deployment

The application is deployed on **Render** using Django and Gunicorn.

Production deployment demonstrates experience with:

* Environment configuration
* PostgreSQL
* Gunicorn
* Docker
* Static files
* Production Django settings
* Cloud deployment

## API Documentation

The API uses token authentication for protected endpoints.

### Base URL

```text
https://task-management-api-wpw5.onrender.com/api/
```

### Authentication

Protected endpoints require a token in the request header:

```text
Authorization: Token YOUR_TOKEN
```

---

## Authentication Endpoints

### Register a User

**POST** `/api/register/`

Create a new user account.

#### Request

```json
{
  "username": "brian",
  "email": "brian@example.com",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "message": "User created successfully",
  "token": "YOUR_TOKEN",
  "user": {
    "id": 1,
    "username": "brian",
    "email": "brian@example.com"
  }
}
```

### Login

**POST** `/api/login/`

Authenticate a user and receive an API token.

#### Request

```json
{
  "username": "brian",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "message": "Login successful",
  "token": "YOUR_TOKEN",
  "user": {
    "id": 1,
    "username": "brian",
    "email": "brian@example.com"
  }
}
```

### Logout

**POST** `/api/logout/`

Logs out the authenticated user and removes their authentication token.

```text
Authorization: Token YOUR_TOKEN
```

#### Response

```json
{
  "message": "Logged out successfully"
}
```

---

## Task Endpoints

All task endpoints require authentication.

### List Tasks

**GET** `/api/tasks/`

Returns tasks belonging to the authenticated user.

```bash
curl -X GET https://task-management-api-wpw5.onrender.com/api/tasks/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### Create a Task

**POST** `/api/tasks/`

Create a new task.

#### Request

```json
{
  "title": "Complete Django API project",
  "description": "Finish API documentation and testing",
  "due_date": "2026-10-01T10:00:00Z",
  "priority": "HIGH",
  "status": "PENDING",
  "recurrence": "NONE"
}
```

A category can be assigned using `category_id`:

```json
{
  "title": "Complete Django API project",
  "description": "Finish API documentation",
  "priority": "HIGH",
  "status": "PENDING",
  "recurrence": "NONE",
  "category_id": 1
}
```

The authenticated user is automatically assigned to the task.

### Get a Single Task

**GET** `/api/tasks/{id}/`

Example:

```text
GET /api/tasks/1/
```

### Update a Task

**PATCH** `/api/tasks/{id}/`

Example:

```json
{
  "status": "IN_PROGRESS"
}
```

Tasks that are already completed have restricted updates.

### Delete a Task

**DELETE** `/api/tasks/{id}/`

Example:

```text
DELETE /api/tasks/1/
```

### Complete a Task

**PATCH** `/api/tasks/{id}/complete/`

Marks a task as completed and records the completion time.

```bash
curl -X PATCH https://task-management-api-wpw5.onrender.com/api/tasks/1/complete/ \
  -H "Authorization: Token YOUR_TOKEN"
```

For recurring tasks, completing a task can automatically create the next task based on its recurrence setting.

---

## Task Fields

| Field          | Description            |
| -------------- | ---------------------- |
| `title`        | Task title             |
| `description`  | Task description       |
| `due_date`     | Optional task deadline |
| `priority`     | Task priority          |
| `status`       | Current task status    |
| `category_id`  | Optional category ID   |
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

## Filtering

Tasks support filtering by status, priority, due date, and category.

### Filter by Status

```text
/api/tasks/?status=COMPLETED
```

### Filter by Priority

```text
/api/tasks/?priority=HIGH
```

### Filter by Due Date

```text
/api/tasks/?due_date=2026-10-01
```

### Filter by Category ID

```text
/api/tasks/?category=1
```

### Filter by Category Name

```text
/api/tasks/?category=Work
```

### Combine Filters

```text
/api/tasks/?status=PENDING&priority=HIGH
```

---

## Ordering

Tasks support ordering by `due_date` and `priority`.

### Order by Due Date

```text
/api/tasks/?ordering=due_date
```

### Reverse Due Date Order

```text
/api/tasks/?ordering=-due_date
```

### Order by Priority

```text
/api/tasks/?ordering=priority
```

### Reverse Priority Order

```text
/api/tasks/?ordering=-priority
```

If no supported ordering parameter is provided, tasks are ordered by newest first.

---

## Category Endpoints

Categories are linked to the authenticated user.

### List Categories

**GET** `/api/categories/`

### Create Category

**POST** `/api/categories/`

#### Request

```json
{
  "name": "Work"
}
```

### Get a Category

**GET** `/api/categories/{id}/`

Example:

```text
GET /api/categories/1/
```

### Update a Category

**PATCH** `/api/categories/{id}/`

```json
{
  "name": "Personal"
}
```

### Delete a Category

**DELETE** `/api/categories/{id}/`

---

## Task Workflow

Tasks support four statuses:

```text
PENDING → IN_PROGRESS → COMPLETED
```

A task can also be marked:

```text
CANCELLED
```

When a task is completed, the API records the `completed_at` timestamp.

Completed tasks have restricted updates to help preserve completion data.

---

## Recurring Tasks

Tasks support four recurrence options:

* `NONE`
* `DAILY`
* `WEEKLY`
* `MONTHLY`

Example:

```json
{
  "title": "Weekly project review",
  "description": "Review project progress",
  "priority": "MEDIUM",
  "status": "PENDING",
  "recurrence": "WEEKLY"
}
```

When a recurring task is completed, the API calculates the next due date and creates the next pending task.

---

## User Dashboards

### User Dashboard

**GET** `/api/user/dashboard/`

Requires authentication.

### Admin Dashboard

**GET** `/api/admin/dashboard/`

Requires authentication and the appropriate administrative permissions.

---

## Testing

The project includes automated tests covering areas such as:

* User authentication
* Task creation
* Task status changes
* Task completion
* Recurring tasks
* Category filtering
* Status filtering
* Priority filtering
* Task ordering

Run the tests with:

```bash
pytest -v
```

---

## Example Authentication Flow

### 1. Register

```text
POST /api/register/
```

### 2. Copy the returned token

```text
"token": "YOUR_TOKEN"
```

### 3. Add the token to protected requests

```text
Authorization: Token YOUR_TOKEN
```

### 4. Access the task API

```text
GET /api/tasks/
```

This allows an authenticated user to manage their own tasks.

---

## API Development Highlights

This project demonstrates practical backend development using:

* Django REST Framework
* RESTful API design
* Token authentication
* User-specific data
* CRUD operations
* Filtering and ordering
* Task status workflows
* Recurring tasks
* PostgreSQL
* Automated testing
* Docker
* Gunicorn
* Render deployment
* Response caching


## 📚 What I Built

This project demonstrates my experience with:

* Building RESTful APIs with Django REST Framework
* Designing database-backed applications
* Implementing authentication and permissions
* Building task workflows
* Implementing filtering and ordering
* Working with recurring tasks
* Writing automated tests
* Containerizing applications with Docker
* Deploying backend applications
* Debugging and improving production-style applications

## 🔮 Future Improvements

* CI/CD with GitHub Actions

## 👨‍💻 Author

**Brian Otieno**

Backend Developer focused on Python, Django, Django REST Framework, PostgreSQL, and REST APIs.

GitHub:
https://github.com/otieno-backend

## ⭐ Project

If you find this project useful, feel free to star the repository.
