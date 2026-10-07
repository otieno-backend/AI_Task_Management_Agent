# AI Task Management Agent

An AI-ready backend system that combines a **Django REST API** with a **Model Context Protocol (MCP) server**.

The project allows an MCP-compatible AI client to interact with a task-management backend through authenticated tools for creating, retrieving, updating, completing, and listing tasks.

This project demonstrates practical backend development with **Python, Django, Django REST Framework, PostgreSQL, Redis, Celery, Docker, automated testing, cloud deployment, and AI/MCP integration**.

---

## 🚀 Why This Project?

Traditional task-management applications require users to interact directly with a web or mobile interface.

This project adds an AI integration layer that allows an MCP-compatible AI client to interact with the backend through structured tools.

For example, an AI client can use the MCP server to:

- Create a task
- Retrieve a task
- Update a task
- Complete a task
- List tasks

The MCP server communicates with the Django REST API instead of accessing the database directly.

This creates a clear separation between the **AI integration layer** and the **backend application layer**.

---

## 🏗️ Architecture

```text
                 AI / MCP Client
                        │
                        │ MCP
                        ▼
              ┌───────────────────┐
              │    MCP Server     │
              │   Python + MCP    │
              └─────────┬─────────┘
                        │
                        │ HTTP
                        │ Authenticated API Request
                        ▼
              ┌───────────────────┐
              │   Django REST API │
              │    Django + DRF   │
              └─────────┬─────────┘
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
       ┌─────────────┐     ┌─────────────┐
       │ PostgreSQL  │     │    Redis    │
       │  Database   │     │    Cache    │
       └─────────────┘     └─────────────┘
                                  │
                                  ▼
                             Celery Tasks
Request Flow
AI Client
   ↓
MCP Tool
   ↓
MCP Server
   ↓
Authenticated HTTP Request
   ↓
Django REST API
   ↓
Authentication & Permissions
   ↓
Task ViewSet / Business Logic
   ↓
Database
   ↓
API Response
   ↓
MCP Tool Response
   ↓
AI Client
🤖 MCP Server

The MCP server acts as a bridge between an AI client and the Django REST API.

Available MCP Tools
Tool	Purpose
hello_task_manager	Verify that the MCP server is working
list_tasks	Retrieve tasks from the Django API
create_task	Create a new task
get_task	Retrieve a specific task
update_task	Update an existing task
complete_task	Mark a task as completed

The MCP server uses authenticated HTTP requests to communicate with the Django backend.

The MCP layer does not directly access the Django database.

📋 Backend Features

The Django REST API supports:

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
Background task processing with Celery
Automated testing
Docker support
Cloud deployment
🔄 Task Workflow

Tasks support the following statuses:

PENDING
   │
   ▼
IN_PROGRESS
   │
   ▼
COMPLETED

Tasks can also be marked:

CANCELLED

When a task is completed, the backend records the completion timestamp.

For recurring tasks, completing a task can create the next task according to its recurrence configuration.

Supported recurrence options:

NONE
DAILY
WEEKLY
MONTHLY
🔐 Authentication

The Django API uses token authentication.

Protected requests use:

Authorization: Token YOUR_TOKEN

The MCP server reads the API token from environment variables instead of storing credentials directly in source code.

Example:

DJANGO_API_URL=http://127.0.0.1:8000/api
DJANGO_API_TOKEN=YOUR_SECRET_TOKEN

Never commit real API tokens or secrets to GitHub.

📡 Django REST API
Authentication
Method	Endpoint	Description
POST	/api/register/	Register a user
POST	/api/login/	Login
POST	/api/logout/	Logout
Tasks
Method	Endpoint	Description
GET	/api/tasks/	List tasks
POST	/api/tasks/	Create a task
GET	/api/tasks/<id>/	Retrieve a task
PATCH	/api/tasks/<id>/	Update a task
DELETE	/api/tasks/<id>/	Delete a task
PATCH	/api/tasks/<id>/complete/	Complete a task
Categories
Method	Endpoint	Description
GET	/api/categories/	List categories
POST	/api/categories/	Create a category
🔎 Filtering

Tasks can be filtered by:

Status
Priority
Due date
Category

Example:

/api/tasks/?status=PENDING&priority=HIGH
↕️ Ordering

Tasks can be ordered by supported fields such as due date and priority.

Example:

/api/tasks/?ordering=-due_date
📝 Example Task
{
  "title": "Complete Django API project",
  "description": "Finish API documentation and testing",
  "priority": "HIGH",
  "status": "PENDING",
  "recurrence": "NONE"
}

The authenticated user is automatically associated with the task.

🔁 Recurring Tasks

The API supports:

NONE
DAILY
WEEKLY
MONTHLY

When a recurring task is completed, the backend can create the next task based on the recurrence configuration.

This demonstrates backend business logic beyond basic CRUD operations.

⚡ Redis and Celery

Redis is used as a caching layer for the Django application.

Celery is included for background task processing.

This provides a foundation for handling operations that should not block normal API requests.

For local Redis development:

docker compose up -d redis
🐳 Docker

The Django application includes Docker configuration.

Build and start the services:

docker compose up --build

Docker helps provide consistent development and deployment environments.

🧪 Testing

Run the Django test suite:

pytest -v

Tests cover important backend functionality including:

User creation
Authentication
Task creation
Task status changes
Task completion
Recurring tasks
Filtering
Ordering
Categories

The MCP integration has also been tested using MCP Inspector.

MCP End-to-End Workflow
Create Task
     ↓
Get Task
     ↓
Update Task
     ↓
Complete Task
     ↓
List Tasks

A task created through the MCP server is persisted by the Django backend and can subsequently be retrieved through the API.

☁️ Deployment

The Django REST API is deployed on Render.

Live API:

https://task-management-api-wpw5.onrender.com/api/

The MCP server currently runs locally and communicates with the deployed Django API when configured with the appropriate API URL and authentication token.

🛠️ Technology Stack
Technology	Purpose
Python	Backend programming
Django	Web framework
Django REST Framework	REST API development
MCP	AI-to-application integration
Requests	HTTP communication
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
│   └── requirements.txt
│
├── .gitignore
└── README.md

Environment files and virtual environments are excluded from Git.

⚙️ Local Django Setup
1. Clone the repository
git clone https://github.com/otieno-backend/AI_Task_Management_Agent.git
cd AI_Task_Management_Agent
2. Enter the Django project
cd taskhub
3. Create a virtual environment
python -m venv .venv
4. Activate the virtual environment

Windows Git Bash:

source .venv/Scripts/activate
5. Install dependencies
pip install -r requirements.txt
6. Run migrations
python manage.py migrate
7. Start Django
python manage.py runserver

The API will be available at:

http://127.0.0.1:8000/
🤖 MCP Server Setup

Open another terminal.

1. Enter the MCP server
cd mcp_server
2. Create a virtual environment
python -m venv .venv
3. Activate the environment

Windows Git Bash:

source .venv/Scripts/activate
4. Install dependencies
python -m pip install "mcp[cli]"
pip install requests python-dotenv
5. Configure environment variables

Create:

mcp_server/.env

Add:

DJANGO_API_URL=http://127.0.0.1:8000/api
DJANGO_API_TOKEN=YOUR_SECRET_TOKEN

Replace YOUR_SECRET_TOKEN with a valid Django API token.

6. Start the MCP server

Make sure the Django API is running first.

mcp dev server.py

MCP Inspector can then be used to interact with and test the available tools.

🧠 Backend Engineering Skills Demonstrated

This project demonstrates practical experience with:

REST API development
Django and Django REST Framework
API authentication
Permissions
Database-backed applications
Backend business logic
Task workflows
Recurring operations
Filtering and ordering
Pagination
Redis caching
Celery background processing
Automated testing
Docker
Cloud deployment
Environment-based configuration
MCP integration
AI-to-backend communication
HTTP API integration
🔮 Future Improvements

Planned improvements include:

Additional MCP tools
MCP resources and prompts
Better structured tool responses
More comprehensive MCP tests
GitHub Actions CI/CD
Production monitoring
Structured logging
Application metrics
Improved API documentation
More advanced AI task-management capabilities
👨‍💻 Author
Brian Otieno

Backend Developer focused on building reliable APIs and backend systems with Python and Django.

Core technologies:

Python
Django
Django REST Framework
REST APIs
PostgreSQL
Redis
Celery
Docker
MCP / AI integration

GitHub:

https://github.com/otieno-backend

⭐ Project

If you find this project useful, feel free to star the repository.

Repository:

https://github.com/otieno-backend/AI_Task_Management_Agent
