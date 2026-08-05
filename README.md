# 🚀 TaskFlow - Project Management System

TaskFlow is a full-featured project management system built with **FastAPI** (backend) and **React + TypeScript** (frontend). It enables teams to collaborate on projects, track tasks, log work hours, and manage notifications in real-time.

---

## ✨ Features

### 🔐 Authentication
- Email/Password registration and login
- Google OAuth integration
- JWT token-based authentication

### 📁 Project Management
- Create, update, and delete projects
- Search projects by name, description, or key
- Project members with role-based access (Owner, Admin, Member, Viewer)

### ✅ Task Management
- Create, update, and delete tasks
- Drag & Drop Kanban board
- Task status transitions (ToDo → InProgress → Done)
- Task priority levels (Low, Medium, High)
- Assign tasks to team members

### 💬 Collaboration
- Comments with @mentions
- Task collaborators and watchers
- Project invitations via email
- Activity logs for all actions

### 🔔 Notifications
- Real-time notifications for task assignments, status changes, comments, and mentions
- Mark notifications as read/unread
- Unread count badge

### ⏱️ Time Tracking
- Log work hours on tasks
- Weekly summary reports
- Admin view for all timesheets
- Import/Export timesheets (CSV, Excel)

### 📊 Dashboard
- Overview statistics (projects, tasks, overdue)
- Tasks by status and priority charts
- Recent activity feed
- Weekly activity timeline

---

## 🛠️ Tech Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Programming language |
| FastAPI | 0.115.12 | Web framework |
| SQLAlchemy | 2.0.41 | ORM |
| PostgreSQL | 15 | Database |
| Alembic | 1.16.1 | Database migrations |
| JWT | - | Authentication |
| Google OAuth | - | Social login |
| APScheduler | 3.11.0 | Background tasks |
| Pytest | 8.3.5 | Testing |

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18 | UI framework |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 3 | Styling |
| Vite | 5 | Build tool |
| React Router | 6 | Routing |
| Heroicons | - | Icons |
| Recharts | - | Charts |
| @hello-pangea/dnd | - | Drag & Drop |

### Deployment

| Platform | Service |
|----------|---------|
| Render | Backend API |
| Vercel | Frontend |
| Neon | PostgreSQL |

---

## 📁 Project Structure
taskflow/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ │ └── v1/
│ │ │ ├── auth.py
│ │ │ ├── projects.py
│ │ │ ├── tasks.py
│ │ │ ├── members.py
│ │ │ ├── comments.py
│ │ │ ├── notifications.py
│ │ │ ├── invitations.py
│ │ │ ├── activities.py
│ │ │ ├── dashboard.py
│ │ │ ├── timesheet.py
│ │ │ └── users.py
│ │ ├── core/
│ │ │ ├── config.py
│ │ │ ├── database.py
│ │ │ ├── security.py
│ │ │ └── dependencies.py
│ │ ├── models/
│ │ │ ├── base.py
│ │ │ ├── user.py
│ │ │ ├── project.py
│ │ │ ├── member.py
│ │ │ ├── task.py
│ │ │ ├── comment.py
│ │ │ ├── invitation.py
│ │ │ ├── notification.py
│ │ │ ├── activity.py
│ │ │ └── timesheet.py
│ │ ├── schemas/
│ │ ├── services/
│ │ ├── scheduler/
│ │ └── main.py
│ ├── tests/
│ ├── alembic/
│ ├── requirements.txt
│ ├── Dockerfile
│ ├── entrypoint.sh
│ └── .env.example
├── frontend/
│ ├── src/
│ │ ├── api/
│ │ ├── components/
│ │ ├── context/
│ │ ├── pages/
│ │ ├── types/
│ │ ├── App.tsx
│ │ ├── main.tsx
│ │ └── index.css
│ ├── package.json
│ ├── vite.config.ts
│ ├── tailwind.config.js
│ └── Dockerfile
├── docker-compose.yml
├── render.yaml
└── README.md

text

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Python | 3.11+ | [Download](https://www.python.org/downloads/) |
| Node.js | 18+ | [Download](https://nodejs.org/) |
| PostgreSQL | 15+ | [Download](https://www.postgresql.org/download/) |
| Docker | Latest | [Download](https://www.docker.com/products/docker-desktop/) |

---

### Option 1: Local Development

#### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/RahafMoualla97/taskflow.git
cd taskflow/backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit .env with your credentials

# 6. Run database migrations
alembic upgrade head

# 7. Start the server
uvicorn app.main:app --reload
Backend will run at: http://localhost:8000

Frontend Setup
bash
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install dependencies
npm install

# 3. Create .env.local file
cp .env.example .env.local

# 4. Edit .env.local
# VITE_API_URL=http://localhost:8000/api/v1

# 5. Start the development server
npm run dev
Frontend will run at: http://localhost:5173

Option 2: Docker (Recommended for Production)
bash
# 1. Start all services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
Services:

Backend: http://localhost:8000

Frontend: http://localhost:5173

Database: localhost:5433 (PostgreSQL)

📚 API Documentation
Once the backend is running, you can access:

URL	Description
http://localhost:8000/docs	Swagger UI (Interactive API documentation)
http://localhost:8000/redoc	ReDoc (Alternative API documentation)
Main API Endpoints
Method	Endpoint	Description
Auth		
POST	/api/v1/auth/register	Register a new user
POST	/api/v1/auth/login	Login with email/password
GET	/api/v1/auth/google	Google OAuth login
GET	/api/v1/auth/users/me	Get current user profile
PUT	/api/v1/auth/users/me	Update current user profile
Projects		
POST	/api/v1/projects/	Create a new project
GET	/api/v1/projects/	Get all user projects
GET	/api/v1/projects/search	Search projects
GET	/api/v1/projects/{id}	Get project by ID
PUT	/api/v1/projects/{id}	Update project
DELETE	/api/v1/projects/{id}	Delete project
Tasks		
POST	/api/v1/tasks/	Create a new task
GET	/api/v1/tasks/project/{project_id}	Get project tasks
GET	/api/v1/tasks/search	Search tasks
GET	/api/v1/tasks/{id}	Get task by ID
PUT	/api/v1/tasks/{id}	Update task
PATCH	/api/v1/tasks/{id}/status	Update task status
DELETE	/api/v1/tasks/{id}	Delete task
Members		
GET	/api/v1/projects/{id}/members	Get project members
POST	/api/v1/projects/{id}/members	Add member to project
PUT	/api/v1/projects/{id}/members/{user_id}	Update member role
DELETE	/api/v1/projects/{id}/members/{user_id}	Remove member
Comments		
POST	/api/v1/comments/task/{task_id}	Add comment
GET	/api/v1/comments/task/{task_id}	Get task comments
DELETE	/api/v1/comments/{id}	Delete comment
Notifications		
GET	/api/v1/notifications/	Get notifications
GET	/api/v1/notifications/unread-count	Get unread count
PATCH	/api/v1/notifications/{id}/read	Mark as read
PATCH	/api/v1/notifications/read-all	Mark all as read
DELETE	/api/v1/notifications/{id}	Delete notification
Invitations		
POST	/api/v1/invitations/	Create invitation
POST	/api/v1/invitations/accept	Accept invitation
GET	/api/v1/invitations/check	Check invitation validity
Timesheets		
POST	/api/v1/timesheets/	Log work hours
GET	/api/v1/timesheets/task/{task_id}	Get task timesheets
GET	/api/v1/timesheets/my	Get user timesheets
GET	/api/v1/timesheets/weekly-summary	Get weekly summary
DELETE	/api/v1/timesheets/{id}	Delete timesheet
Dashboard		
GET	/api/v1/dashboard/stats	Get dashboard stats
GET	/api/v1/dashboard/tasks/recent	Get recent tasks
GET	/api/v1/dashboard/tasks/overdue	Get overdue tasks
GET	/api/v1/dashboard/tasks/my	Get my tasks
GET	/api/v1/dashboard/advanced-stats	Get advanced stats
Activities		
GET	/api/v1/activities/project/{project_id}	Get project activities
GET	/api/v1/activities/task/{task_id}	Get task activities
GET	/api/v1/activities/recent	Get recent activities
🧪 Testing
bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows

# 3. Run all tests
pytest tests/ -v

# 4. Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# 5. Generate HTML coverage report
pytest tests/ -v --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
Test Coverage
Metric	Value
Total Tests	45
Passing	✅ 45 (100%)
Code Coverage	73%
🌐 Deployment
Backend (Render)
Push your code to GitHub

Go to Render Dashboard

Click New + → Web Service

Connect your GitHub repository

Configure:

Build Command: pip install -r requirements.txt

Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000

Add environment variables (see .env.example)

Click Create Web Service

Frontend (Vercel)
Push your code to GitHub

Go to Vercel Dashboard

Click Add New → Project

Import your GitHub repository

Configure:

Framework Preset: Vite

Root Directory: frontend

Build Command: npm run build

Output Directory: dist

Add environment variable: VITE_API_URL

Click Deploy

Database (Neon)
Go to Neon

Create a new project

Copy the connection string

Add it to Render environment variables

📝 Environment Variables
Create a .env file in the backend/ directory:

env
# ========== Database ==========
DATABASE_URL=postgresql://taskflow_user:taskflow_pass@localhost:5433/taskflow_db

# ========== JWT Authentication ==========
SECRET_KEY=your_super_secret_key_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ========== Google OAuth ==========
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback

# ========== Frontend ==========
FRONTEND_URL=http://localhost:5173

# ========== Email (SMTP) ==========
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
FROM_EMAIL=noreply@taskflow.com

# ========== Environment ==========
ENVIRONMENT=development
DEBUG=true
⚠️ Never commit .env to version control!

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

Code Style
Backend: Follow PEP 8

Frontend: Follow ESLint + Prettier

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
Rahaf Moualla

GitHub: [@RahafMoualla97](https://github.com/RahafMoualla97)

LinkedIn: [Rahaf Moualla](https://www.linkedin.com/in/rahaf-moualla-767111325/)

🙏 Acknowledgments
FastAPI

React

Tailwind CSS

PostgreSQL