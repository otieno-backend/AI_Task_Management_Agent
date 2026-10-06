# AI Task Management Agent

An AI-ready task management system that combines a **Django REST API** with a **Model Context Protocol (MCP) server**.

The project allows an MCP-compatible AI client to interact with the task management backend through tools for creating, retrieving, updating, completing, and listing tasks.

---

## 🚀 Project Overview

The project consists of two main components:

```text
AI / MCP Client
       │
       ▼
┌─────────────────────┐
│     MCP Server      │
│     Python + MCP    │
└──────────┬──────────┘
           │
        HTTP API
           │
           ▼
┌─────────────────────┐
│    Django REST API  │
│   Django + DRF      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Database       │
└─────────────────────┘

The MCP server acts as a bridge between an AI client and the existing Django Task Management API.

🤖 MCP Server

The MCP server exposes task-management functionality as tools that an MCP-compatible client can call.

Available MCP Tools
Tool	Purpose
hello_task_manager	Verify that the MCP server is working
list_tasks	Retrieve tasks from the Django API
create_task	Create a new task
get_task	Retrieve a specific task
update_task	Update an existing task
complete_task	Mark a task as completed

The MCP server communicates with the Django API using authenticated HTTP requests.

📋 Task Management Features

The Django backend supports:

User registration and authentication
Token-based authentication
User-specific tasks
Task creation and management
Task status workflows
Task priorities
Due dates
Categories
Filtering
Ordering
Pagination
Recurring tasks
Completion timestamps
Redis caching
Automated testing
Docker support
Cloud deployment
🔄 Task Workflow

Tasks support the following statuses:

PENDING
   ↓
IN_PROGRESS
   ↓
COMPLETED

Tasks can also be marked:

CANCELLED

When a task is completed, the API records the completion time.

Recurring tasks can also create the next task based on their recurrence setting.

🔌 MCP → Django Integration

The MCP server does not directly access the Django database.

Instead, it communicates with the Django REST API:

MCP Tool
   │
   │ HTTP Request
   ▼
Django REST API
   │
   │ Authentication
   ▼
Task ViewSet
   │
   ▼
Database
   │
   ▼
Django Response
   │
   ▼
MCP Tool

This separation keeps the MCP layer independent from the Django application's internal database logic.

🧪 End-to-End Testing

The MCP integration has been tested through MCP Inspector.

The following workflow was successfully tested:

Create Task
    ↓
Get Task
    ↓
Update Task
    ↓
Complete Task
    ↓
List Tasks
Example test

A task was created through the MCP server:

Title: End-to-End MCP Test
Priority: HIGH
Status: PENDING

It was then updated:

PENDING
   ↓
IN_PROGRESS

And completed:

IN_PROGRESS
   ↓
COMPLETED

The final list_tasks operation confirmed that the task was persisted by the Django backend.

🛠️ Technology Stack
Technology	Purpose
Python	Backend programming
Django	Web framework
Django REST Framework	REST API
MCP	AI-to-application integration
Requests	HTTP communication between MCP and Django
PostgreSQL	Production database
SQLite	Local development database
Redis	Caching
Celery	Background task processing
Docker	Containerization
Gunicorn	Production application server
Pytest	Automated testing
Render	Cloud deployment
Git/GitHub	Version control
📁 Project Structure
AI_Task_Management_Agent/
│
├── taskhub/
│   ├── accounts/
│   ├── Tasks/
│   ├── taskhub/
│   ├── manage.py
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── Procfile
│   └── requirements.txt
│
├── mcp_server/
│   ├── server.py
│   ├── .env
│   └── .venv/
│
├── .gitignore
└── README.md

.env and virtual environments are excluded from Git.

⚙️ Django API Setup
1. Enter the Django project
cd taskhub
2. Create a virtual environment
python -m venv .venv
3. Activate the virtual environment
Windows Git Bash
source .venv/Scripts/activate
4. Install dependencies
pip install -r requirements.txt
5. Run migrations
python manage.py migrate
6. Start Django
python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/
🤖 MCP Server Setup

Open another terminal.

1. Enter the MCP server directory
cd mcp_server
2. Create the virtual environment
python -m venv .venv
3. Activate it
source .venv/Scripts/activate
4. Install MCP
python -m pip install "mcp[cli]"

Install the additional dependencies:

pip install requests python-dotenv
🔐 Environment Variables

Create a .env file inside:

mcp_server/.env

Example:

DJANGO_API_URL=http://127.0.0.1:8000/api
DJANGO_API_TOKEN=YOUR_SECRET_TOKEN

Replace YOUR_SECRET_TOKEN with a valid Django API token.

Never commit your real token to GitHub.

The project .gitignore excludes .env files.

▶️ Running the MCP Server

Make sure Django is running first.

From the mcp_server directory:

mcp dev server.py

This starts the MCP development environment and opens MCP Inspector.

MCP Inspector can then be used to test the available tools.

🔑 Authentication

The Django API uses token authentication.

Protected API requests use:

Authorization: Token YOUR_TOKEN

The MCP server reads the token from the environment instead of hard-coding it in the source code.

📡 Django API Endpoints
Method	Endpoint	Description
POST	/api/register/	Register a user
POST	/api/login/	Login
POST	/api/logout/	Logout
GET	/api/tasks/	List tasks
POST	/api/tasks/	Create a task
GET	/api/tasks/<id>/	Get a task
PATCH	/api/tasks/<id>/	Update a task
DELETE	/api/tasks/<id>/	Delete a task
PATCH	/api/tasks/<id>/complete/	Complete a task
GET	/api/categories/	List categories
POST	/api/categories/	Create a category
📝 Example Task
{
  "title": "Complete Django API project",
  "description": "Finish API documentation and testing",
  "priority": "HIGH",
  "status": "PENDING",
  "recurrence": "NONE"
}

The authenticated user is automatically associated with the task.

🔎 Filtering

Tasks can be filtered by:

Status
Priority
Due date
Category

Example:

/api/tasks/?status=PENDING&priority=HIGH
↕️ Ordering

Tasks can be ordered by fields such as due date and priority.

Example:

/api/tasks/?ordering=-due_date
🔁 Recurring Tasks

Supported recurrence options:

NONE
DAILY
WEEKLY
MONTHLY

When a recurring task is completed, the backend can create the next task according to its recurrence configuration.

⚡ Redis Caching

The Django application uses Redis for caching.

Local Redis can be started with:

docker compose up -d redis

The Django application can then connect to the local Redis instance.

🐳 Docker

The Django application includes Docker configuration.

Build and start the services:

docker compose up --build

Docker is used to provide consistent development and deployment environments.

🧪 Testing

Run the Django test suite:

pytest -v

The tests cover important backend functionality including:

User creation
Authentication
Task creation
Task status changes
Task completion
Recurring tasks
Filtering
Ordering
Categories
☁️ Live API

The Django REST API is deployed on Render:

https://task-management-api-wpw5.onrender.com/api/

The MCP server currently runs locally and communicates with the Django API.

🧠 What This Project Demonstrates

This project demonstrates practical experience with:

REST API development
Django and Django REST Framework
Authentication and permissions
Database-backed applications
Task workflows
Recurring business logic
API filtering and ordering
Automated testing
Redis caching
Docker
Cloud deployment
MCP integration
AI-to-backend communication
Environment-based configuration
🔮 Future Improvements

Planned improvements include:

Additional MCP tools
MCP resources and prompts
Better structured tool responses
More comprehensive MCP tests
CI/CD with GitHub Actions
Production monitoring
Logging and metrics
Improved API documentation
More advanced AI task-management capabilities
👨‍💻 Author

Brian Otieno

Backend Developer focused on:

Python
Django
Django REST Framework
REST APIs
PostgreSQL
Docker
MCP integration

GitHub:

https://github.com/otieno-backend

⭐ Project

If you find the project useful, feel free to star the repository.

Repository:

https://github.com/otieno-backend/AI_Task_Management_Agent
