# TaskFlow API

A Django REST Framework-based task management API for learning Django fundamentals and CI/CD with Buildkite.

---

## Table of Contents

- [Django 101: Concepts for Node.js/Express Developers](#django-101-concepts-for-nodejsexpress-developers)
- [Project Structure Walkthrough](#project-structure-walkthrough)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [API Endpoints](#api-endpoints)
- [Additional Resources](#additional-resources)

---

## Django 101: Concepts for Node.js/Express Developers

If you're coming from Node.js and Express, Django will feel both familiar and different. This section maps Django concepts to their Express equivalents.

### Framework Philosophy

**Express (Node.js):**
- Minimalist, unopinionated framework
- You choose your tools (ORM, template engine, etc.)
- Middleware-based request/response pipeline
- Asynchronous by default

**Django (Python):**
- "Batteries included" framework
- Opinionated with built-in ORM, admin panel, auth system
- Middleware-based but synchronous by default
- Convention over configuration

### Project vs App

**In Django:**

```
Project = Your entire website/API
App = A module within your project (e.g., tasks, users, blog)
```

**Express Equivalent:**

```
Project = Your Express server
App = A router/controller module (e.g., routes/tasks.js)
```

**Example:**
```
taskflow-api/          # Django Project (like your Express app root)
├── taskflow/          # Project settings (like app.js + config/)
│   ├── settings.py    # All configuration (DB, middleware, apps)
│   ├── urls.py        # Root URL routing (like main app.use())
│   └── wsgi.py        # Server entry point (like server.js)
└── tasks/             # Django App (like routes/tasks.js + models/)
    ├── models.py      # Database models (like Sequelize models)
    ├── views.py       # Request handlers (like Express route handlers)
    ├── urls.py        # App-specific routes (like router.get())
    └── serializers.py # Data transformation (like response formatting)
```

### Models (ORM)

Django has a built-in ORM similar to Sequelize or Prisma.

**Express + Sequelize:**

```javascript
// models/Task.js
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
  const Task = sequelize.define('Task', {
    title: {
      type: DataTypes.STRING,
      allowNull: false
    },
    status: {
      type: DataTypes.ENUM('TODO', 'IN_PROGRESS', 'DONE'),
      defaultValue: 'TODO'
    }
  });
  return Task;
};
```

**Django:**

```python
# tasks/models.py
from django.db import models

class Task(models.Model):
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('DONE', 'Done'),
    ]

    title = models.CharField(max_length=200)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TODO'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key Differences:**
- Django models inherit from `models.Model`
- Field types are methods: `CharField()`, `DateTimeField()`
- `auto_now_add=True` is like Sequelize's `timestamps: true`
- No need to call `sync()` - use migrations instead

### Migrations

**What are migrations?**

Migrations are version-controlled database schema changes. Think of them like Git for your database structure.

**Express/Sequelize:**

```javascript
// You might manually create tables or use sync()
await sequelize.sync({ alter: true });
```

**Django:**

```bash
# 1. Create migration files (detects model changes)
python manage.py makemigrations

# 2. Apply migrations to database
python manage.py migrate
```

**How migrations work:**

```
1. Edit models.py (add/change fields)
   ↓
2. Run makemigrations (creates migration file)
   ↓
3. Review migration file (in migrations/ directory)
   ↓
4. Run migrate (applies to database)
```

**Example Migration File:**

```python
# tasks/migrations/0001_initial.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=20)),
            ],
        ),
    ]
```

### Views (Route Handlers)

**Express:**

```javascript
// routes/tasks.js
router.get('/tasks', async (req, res) => {
  const tasks = await Task.findAll();
  res.json(tasks);
});

router.post('/tasks', async (req, res) => {
  const task = await Task.create(req.body);
  res.status(201).json(task);
});
```

**Django REST Framework:**

```python
# tasks/views.py
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # This single class provides:
    # - GET /api/tasks/ (list)
    # - POST /api/tasks/ (create)
    # - GET /api/tasks/{id}/ (retrieve)
    # - PUT /api/tasks/{id}/ (update)
    # - DELETE /api/tasks/{id}/ (delete)
```

**Key Differences:**
- `ModelViewSet` auto-generates CRUD endpoints
- No need to write each route handler manually
- Uses serializers for data validation (like Express validators)

### Serializers (Data Validation & Transformation)

Serializers are like a combination of Express validators and response formatters.

**Express:**

```javascript
// Validation + Response formatting manually
router.post('/tasks', async (req, res) => {
  const { title, description } = req.body;

  // Manual validation
  if (!title) {
    return res.status(400).json({ error: 'Title required' });
  }

  const task = await Task.create({ title, description });

  // Manual formatting
  res.json({
    id: task.id,
    title: task.title,
    description: task.description,
    created_at: task.createdAt
  });
});
```

**Django REST Framework:**

```python
# tasks/serializers.py
from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['created_at']

    # Automatic validation:
    # - title required (from model)
    # - max_length enforced
    # - date formatting
    # - JSON serialization
```

### URL Routing

**Express:**

```javascript
// app.js
const express = require('express');
const taskRoutes = require('./routes/tasks');

const app = express();

app.use('/api/tasks', taskRoutes);
```

**Django:**

```python
# taskflow/urls.py (main project)
from django.urls import path, include

urlpatterns = [
    path('api/', include('tasks.urls')),
]

# tasks/urls.py (app-specific)
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = router.urls
# Generates:
# /api/tasks/
# /api/tasks/{id}/
```

### Middleware

**Express:**

```javascript
app.use(express.json());
app.use(cors());
app.use(authMiddleware);
```

**Django:**

```python
# taskflow/settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

**Key Differences:**
- Middleware is configured in `settings.py`
- Order matters (top to bottom)
- Most common middleware is built-in

### Settings/Configuration

**Express:**

```javascript
// Multiple config files
// .env
DATABASE_URL=postgres://localhost/mydb
PORT=3000

// config.js
module.exports = {
  port: process.env.PORT || 3000,
  database: process.env.DATABASE_URL
};
```

**Django:**

```python
# taskflow/settings.py (single configuration file)
DEBUG = True
SECRET_KEY = 'your-secret-key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'rest_framework',
    'tasks',  # Your custom app
]
```

### Database Queries

**Express/Sequelize:**

```javascript
// Find all
const tasks = await Task.findAll();

// Filter
const tasks = await Task.findAll({
  where: { status: 'TODO' }
});

// Create
const task = await Task.create({ title: 'New Task' });
```

**Django ORM:**

```python
# Find all
tasks = Task.objects.all()

# Filter
tasks = Task.objects.filter(status='TODO')

# Create
task = Task.objects.create(title='New Task')

# Get by ID
task = Task.objects.get(id=1)

# Update
task.status = 'DONE'
task.save()
```

**Key Differences:**
- Django uses `objects` manager instead of model methods
- `filter()` returns QuerySet (lazy evaluation)
- No await - Django ORM is synchronous by default

### Authentication

**Express:**

```javascript
// Manual implementation or passport.js
const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization;
  const user = jwt.verify(token, SECRET);
  req.user = user;
  next();
};
```

**Django:**

```python
# Built-in authentication system
# tasks/views.py
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # request.user is automatically available
        serializer.save(created_by=self.request.user)
```

### Development Server

**Express:**

```javascript
// server.js
app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

```bash
node server.js
# or with nodemon
nodemon server.js
```

**Django:**

```bash
python manage.py runserver
# Runs on http://127.0.0.1:8000/
# Auto-reloads on code changes (like nodemon)
```

### Testing

**Express/Jest:**

```javascript
// tests/tasks.test.js
describe('Task API', () => {
  it('should create a task', async () => {
    const res = await request(app)
      .post('/api/tasks')
      .send({ title: 'Test Task' });

    expect(res.status).toBe(201);
    expect(res.body.title).toBe('Test Task');
  });
});
```

**Django/pytest:**

```python
# tests/unit/test_models.py
from django.test import TestCase
from tasks.models import Task

class TaskModelTest(TestCase):
    def test_create_task(self):
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user
        )

        self.assertEqual(task.title, 'Test Task')
```

---

## Project Structure Walkthrough

```
taskflow-api/
├── manage.py              # CLI tool for Django commands (like npm scripts)
│                          # Usage: python manage.py <command>
│
├── requirements.txt       # Production dependencies (like package.json)
├── requirements-dev.txt   # Development dependencies (like devDependencies)
│
├── pytest.ini            # pytest configuration (like jest.config.js)
│
├── db.sqlite3            # SQLite database file (like .db in local dev)
│
├── taskflow/             # PROJECT DIRECTORY (main configuration)
│   ├── __init__.py       # Makes this a Python package
│   ├── settings.py       # ALL configuration (DB, apps, middleware, etc.)
│   │                     # Think: app.js + config/ + .env combined
│   ├── urls.py           # Root URL routing (like main app.use())
│   ├── wsgi.py           # Web Server Gateway Interface (production server)
│   └── asgi.py           # Async Server Gateway Interface (for async apps)
│
├── tasks/                # APP DIRECTORY (a feature module)
│   │                     # In Express: like routes/tasks.js + models/ + controllers/
│   ├── __init__.py       # Makes this a Python package
│   │
│   ├── models.py         # Database models (ORM definitions)
│   │                     # Like: models/Task.js in Sequelize
│   │
│   ├── views.py          # Request handlers (route logic)
│   │                     # Like: controllers/taskController.js
│   │
│   ├── urls.py           # App-specific URL routing
│   │                     # Like: routes/tasks.js
│   │
│   ├── serializers.py    # Data validation & transformation
│   │                     # Like: validators + response formatters
│   │
│   ├── admin.py          # Django admin panel configuration
│   │                     # Auto-generates admin UI for models
│   │
│   ├── apps.py           # App configuration (metadata)
│   │
│   ├── tests.py          # Default test file (we use tests/ directory instead)
│   │
│   └── migrations/       # Database migration files (version control for DB)
│       ├── __init__.py
│       └── 0001_initial.py   # First migration (creates Task table)
│
└── tests/                # Test directory (like tests/ or __tests__/)
    ├── __init__.py
    └── unit/
        ├── __init__.py
        └── test_models.py    # Unit tests for Task model
```

### Key Files Explained

#### `manage.py`

The Django command-line utility. Think of it like npm scripts.

```bash
# Express equivalent: npm run commands
python manage.py runserver      # npm run dev
python manage.py migrate        # npm run db:migrate
python manage.py test           # npm test
python manage.py createsuperuser # npm run create-admin
```

#### `taskflow/settings.py`

Central configuration file. Contains:

```python
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Installed apps (like dependencies but for Django modules)
INSTALLED_APPS = [
    'django.contrib.admin',    # Admin panel
    'django.contrib.auth',     # Authentication
    'rest_framework',          # Django REST Framework
    'tasks',                   # Our custom app
]

# Middleware (request/response processors)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... more middleware
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'PAGE_SIZE': 10,
}
```

#### `tasks/models.py`

Database schema definitions:

```python
class Task(models.Model):
    # Fields define database columns
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    # Meta class for model configuration
    class Meta:
        ordering = ['-created_at']  # Default sort order

    # String representation (for admin panel, debugging)
    def __str__(self):
        return f"{self.title} ({self.status})"
```

#### `tasks/serializers.py`

Data validation and transformation:

```python
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status']
        read_only_fields = ['created_at']

    # Automatically handles:
    # - Validation (required fields, max length, etc.)
    # - JSON serialization
    # - Deserialization (JSON → Python objects)
```

#### `tasks/views.py`

Request handling logic:

```python
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    # Custom logic
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

#### `tasks/urls.py`

App-specific URL routing:

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)

urlpatterns = router.urls
```

This automatically creates:
- `GET /tasks/` - List tasks
- `POST /tasks/` - Create task
- `GET /tasks/{id}/` - Get specific task
- `PUT /tasks/{id}/` - Update task
- `DELETE /tasks/{id}/` - Delete task

---

## Setup Instructions

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd taskflow-api
```

### 2. Create a Virtual Environment

**What is a virtual environment?**

In Node.js, dependencies are installed in `node_modules/` per project. Python uses virtual environments to isolate project dependencies.

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You'll see (venv) in your terminal prompt
```

**Why virtual environments?**
- Isolates project dependencies (like node_modules)
- Prevents conflicts between projects
- Makes deployment easier

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (for testing)
pip install -r requirements-dev.txt
```

**What gets installed:**

Production (`requirements.txt`):
- Django 4.2.7 - Web framework
- djangorestframework 3.14.0 - REST API toolkit
- psycopg2-binary 2.9.9 - PostgreSQL adapter (for production)
- python-decouple 3.8 - Environment variable management
- gunicorn 21.2.0 - Production WSGI server

Development (`requirements-dev.txt`):
- pytest 7.4.3 - Testing framework
- pytest-django 4.7.0 - Django integration for pytest
- pytest-cov 4.1.0 - Code coverage
- factory-boy 3.3.0 - Test data factories
- faker 20.1.0 - Fake data generation

### 4. Run Migrations

**What are migrations?**

Migrations are version-controlled database schema changes. They create/modify database tables based on your models.

```bash
# Apply migrations (creates database tables)
python manage.py migrate
```

**What this does:**
1. Creates SQLite database file (`db.sqlite3`)
2. Creates all necessary tables:
   - `tasks_task` (our Task model)
   - `auth_user` (built-in User model)
   - `django_session` (session management)
   - And other Django system tables

**Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, tasks
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying tasks.0001_initial... OK
  ...
```

### 5. Create a Superuser (Optional but Recommended)

The superuser lets you access Django's admin panel.

```bash
python manage.py createsuperuser
```

**You'll be prompted for:**
- Username: (your choice, e.g., `admin`)
- Email: (your email)
- Password: (minimum 8 characters)

**Why create a superuser?**
- Access Django admin panel at `/admin/`
- Manually create/edit/delete tasks
- Manage users
- Useful for development and debugging

---

## Running the Application

### Start the Development Server

```bash
python manage.py runserver
```

**Output:**
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 27, 2025 - 12:00:00
Django version 4.2.7, using settings 'taskflow.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

**The server:**
- Runs on http://127.0.0.1:8000/
- Auto-reloads when you change code (like nodemon)
- Shows request logs in the terminal

### Custom Port

```bash
# Run on port 3000 instead
python manage.py runserver 3000
```

---

## Running Tests

### Run All Tests

```bash
# Run with pytest
pytest

# With verbose output
pytest -v

# With code coverage
pytest --cov=tasks
```

**Output:**
```
======================== test session starts ========================
collected 2 items

tests/unit/test_models.py::TaskModelTest::test_create_task PASSED
tests/unit/test_models.py::TaskModelTest::test_task_str PASSED

======================== 2 passed in 0.23s ==========================
```

### Run Specific Tests

```bash
# Run only model tests
pytest tests/unit/test_models.py

# Run a specific test class
pytest tests/unit/test_models.py::TaskModelTest

# Run a specific test method
pytest tests/unit/test_models.py::TaskModelTest::test_create_task
```

### Using Django's Test Runner

```bash
# Django's built-in test runner
python manage.py test

# With verbosity
python manage.py test --verbosity=2
```

### Test Structure

```python
# tests/unit/test_models.py
from django.test import TestCase
from tasks.models import Task

class TaskModelTest(TestCase):
    def setUp(self):
        # Runs before each test
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_create_task(self):
        # Test creating a task
        task = Task.objects.create(
            title='Test Task',
            created_by=self.user
        )
        self.assertEqual(task.title, 'Test Task')
```

**Key Testing Concepts:**

1. **TestCase** - Base class for tests (sets up test database)
2. **setUp()** - Runs before each test method
3. **Assertions** - `assertEqual()`, `assertTrue()`, etc.
4. **Test Database** - Django creates a temporary test database

---

## API Endpoints

### Authentication

All endpoints require authentication. Use Django's session authentication or browse the API through the browsable interface.

**Login via Browser:**
- Navigate to http://127.0.0.1:8000/api-auth/login/
- Login with your superuser credentials

### Task Endpoints

**Base URL:** `http://127.0.0.1:8000/api/`

#### List All Tasks

```
GET /api/tasks/
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Complete Django tutorial",
      "description": "Learn Django REST Framework",
      "status": "TODO",
      "priority": "HIGH",
      "assigned_to": null,
      "created_by": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
      },
      "created_at": "2025-12-27T12:00:00Z",
      "updated_at": "2025-12-27T12:00:00Z",
      "due_date": null
    }
  ]
}
```

#### Create a Task

```
POST /api/tasks/
Content-Type: application/json

{
  "title": "New Task",
  "description": "Task description",
  "status": "TODO",
  "priority": "MEDIUM"
}
```

**Response:** `201 Created`
```json
{
  "id": 2,
  "title": "New Task",
  "description": "Task description",
  "status": "TODO",
  "priority": "MEDIUM",
  "created_by": {...},
  "created_at": "2025-12-27T12:30:00Z",
  ...
}
```

#### Get a Specific Task

```
GET /api/tasks/{id}/
```

#### Update a Task

```
PUT /api/tasks/{id}/
Content-Type: application/json

{
  "title": "Updated Task",
  "status": "IN_PROGRESS"
}
```

#### Delete a Task

```
DELETE /api/tasks/{id}/
```

**Response:** `204 No Content`

### Using the Browsable API

Django REST Framework provides a web interface:

1. Open http://127.0.0.1:8000/api/tasks/ in your browser
2. You'll see a nice UI to:
   - View all tasks
   - Create new tasks via a form
   - Test API endpoints
   - See response formats

This is great for development and API exploration!

### Testing with cURL

```bash
# Login to get session cookie (if using session auth)
curl -X POST http://127.0.0.1:8000/api-auth/login/ \
  -d "username=admin&password=yourpassword" \
  -c cookies.txt

# List tasks
curl http://127.0.0.1:8000/api/tasks/ -b cookies.txt

# Create task
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "status": "TODO"}' \
  -b cookies.txt
```

---

## Common Django Commands

### Database

```bash
# Create migration files (after changing models)
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Rollback to specific migration
python manage.py migrate tasks 0001

# Show migration status
python manage.py showmigrations

# Open database shell
python manage.py dbshell
```

### Development

```bash
# Start development server
python manage.py runserver

# Start on custom port
python manage.py runserver 8080

# Start on all interfaces (for Docker/network access)
python manage.py runserver 0.0.0.0:8000

# Open Python shell with Django context
python manage.py shell
```

### Users

```bash
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword <username>
```

### App Management

```bash
# Create a new Django app
python manage.py startapp <app_name>

# Collect static files (for production)
python manage.py collectstatic
```

### Testing & Quality

```bash
# Run tests
python manage.py test

# Run tests with coverage
pytest --cov=tasks --cov-report=html

# Check for common issues
python manage.py check

# Check for missing migrations
python manage.py makemigrations --check --dry-run
```

---

## Understanding Migrations in Detail

Since migrations are different from typical Node.js workflows, here's a deeper dive:

### The Migration Workflow

```
1. Edit models.py
   └─> Add/modify/remove fields

2. Create migration
   └─> python manage.py makemigrations
   └─> Generates migration file in migrations/

3. Review migration
   └─> Check migrations/0001_initial.py

4. Apply migration
   └─> python manage.py migrate
   └─> Updates database schema
```

### Example: Adding a Field

**Step 1:** Edit the model

```python
# tasks/models.py
class Task(models.Model):
    title = models.CharField(max_length=200)
    # Add new field
    is_urgent = models.BooleanField(default=False)
```

**Step 2:** Create migration

```bash
python manage.py makemigrations
```

**Output:**
```
Migrations for 'tasks':
  tasks/migrations/0002_task_is_urgent.py
    - Add field is_urgent to task
```

**Step 3:** Review the migration file

```python
# tasks/migrations/0002_task_is_urgent.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('tasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_urgent',
            field=models.BooleanField(default=False),
        ),
    ]
```

**Step 4:** Apply migration

```bash
python manage.py migrate
```

**Output:**
```
Operations to perform:
  Apply all migrations: tasks
Running migrations:
  Applying tasks.0002_task_is_urgent... OK
```

### Migration Files

Migration files live in `tasks/migrations/`:

```
tasks/migrations/
├── __init__.py
├── 0001_initial.py       # First migration (creates table)
└── 0002_task_is_urgent.py  # Second migration (adds field)
```

**Why keep migration files?**
- Version control for database schema
- Can rollback changes
- Team members apply same changes
- Production deployment uses migrations

**In Express/Sequelize:**
You might use:
- `sequelize.sync()` (development)
- Migration tools like `sequelize-cli`
- Manual SQL scripts

**In Django:**
Migrations are first-class citizens and required for all schema changes.

---

## Troubleshooting

### Virtual Environment Issues

**Problem:** `command not found: python`

**Solution:**
```bash
# Use python3 instead
python3 -m venv venv
python3 manage.py runserver
```

**Problem:** Virtual environment not activated

**Check:** Your terminal should show `(venv)` at the start
```bash
# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### Migration Issues

**Problem:** "No changes detected" when running makemigrations

**Causes:**
- App not added to `INSTALLED_APPS` in `settings.py`
- Model file has syntax errors

**Solution:**
```python
# taskflow/settings.py
INSTALLED_APPS = [
    ...
    'tasks',  # Make sure your app is listed
]
```

**Problem:** "Table already exists" error

**Solution:**
```bash
# Option 1: Delete database and start fresh (development only!)
rm db.sqlite3
python manage.py migrate

# Option 2: Fake the migration
python manage.py migrate --fake
```

### Port Already in Use

**Problem:** "Address already in use"

**Solution:**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)

# Or use a different port
python manage.py runserver 8001
```

### Testing Issues

**Problem:** "ImproperlyConfigured: Requested setting" error

**Solution:**
Check `pytest.ini` has:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = taskflow.settings
```

### Import Errors

**Problem:** "ModuleNotFoundError: No module named 'rest_framework'"

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## Development Tips

### 1. Django Admin Panel

Access the admin panel at http://127.0.0.1:8000/admin/

**Register your models:**

```python
# tasks/admin.py
from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'created_by']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']
```

**Benefits:**
- Quick data entry/editing
- User management
- View database records
- No need to build admin UI

### 2. Django Shell

Interactive Python shell with Django context:

```bash
python manage.py shell
```

**Usage:**
```python
>>> from tasks.models import Task
>>> from django.contrib.auth.models import User

# Create a user
>>> user = User.objects.create_user('testuser', password='pass123')

# Create tasks
>>> Task.objects.create(title='Test Task', created_by=user)

# Query tasks
>>> Task.objects.filter(status='TODO')
>>> Task.objects.all().count()
```

### 3. Environment Variables

For production, use environment variables:

**Install python-decouple:**
```bash
pip install python-decouple
```

**Create `.env` file:**
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost/dbname
```

**Update settings.py:**
```python
from decouple import config

DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY')
```

### 4. Code Quality

**Install development tools:**
```bash
pip install black flake8 pylint
```

**Format code:**
```bash
black .
```

**Lint code:**
```bash
flake8 tasks/
```

---

## Additional Resources

### Official Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [pytest-django](https://pytest-django.readthedocs.io/)

### Tutorials

- [Django Girls Tutorial](https://tutorial.djangogirls.org/)
- [Django for Beginners](https://djangoforbeginners.com/)
- [Real Python Django Tutorials](https://realpython.com/tutorials/django/)

### Coming from Node.js/Express?

- [Django for JavaScript Developers](https://www.django-rest-framework.org/)
- [Python vs JavaScript Syntax](https://learnxinyminutes.com/docs/python/)

### This Project

This project is part of a Buildkite CI/CD learning course. As you progress through the course, you'll:
- Set up Buildkite pipelines
- Configure automated testing
- Deploy with CI/CD
- Learn infrastructure as code

---

## Quick Reference

### Common Commands

```bash
# Virtual Environment
source venv/bin/activate          # Activate venv

# Development
python manage.py runserver        # Start server
python manage.py shell            # Interactive shell

# Database
python manage.py makemigrations   # Create migrations
python manage.py migrate          # Apply migrations

# Testing
pytest                            # Run tests
pytest -v                         # Verbose output
pytest --cov=tasks                # With coverage

# Users
python manage.py createsuperuser  # Create admin user
```

### Express vs Django Cheat Sheet

| Express | Django | Description |
|---------|--------|-------------|
| `npm install` | `pip install -r requirements.txt` | Install dependencies |
| `node server.js` | `python manage.py runserver` | Start server |
| `npm test` | `pytest` | Run tests |
| `routes/` | `urls.py` | Routing |
| `controllers/` | `views.py` | Request handlers |
| `models/` (Sequelize) | `models.py` | Database models |
| `package.json` | `requirements.txt` | Dependencies |
| `.env` | `settings.py` | Configuration |
| `db.migrate()` | `python manage.py migrate` | Database migrations |
| `app.use(middleware)` | `MIDDLEWARE` in settings | Middleware |

---

## License

This project is for educational purposes.

## Contributing

This is a learning project. Feel free to experiment and break things!

---

**Happy Coding!**

For questions or issues, refer to the official Django documentation or the course materials.
