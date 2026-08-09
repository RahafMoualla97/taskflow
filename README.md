# 🚀 TaskFlow - Project Management System

TaskFlow is a full-featured project management system built with **FastAPI** (backend) and **React + TypeScript** (frontend). It enables teams to collaborate on projects, track tasks, log work hours, and manage notifications in real-time.

---

## 🌐 Live Demo

- **Frontend:** [TaskFlow Frontend](https://taskflow-three-flax.vercel.app/)
- **Backend API:** [TaskFlow Backend](https://taskflow-backend-shcu.onrender.com)
- **API Documentation:** [Swagger UI](https://taskflow-backend-shcu.onrender.com/docs)

---

## 📊 Project Status

| Metric | Value |
|--------|-------|
| Status | Active |
| Version | 1.0.0 |
| License | MIT |
| Python | 3.11+ |
| FastAPI | 0.115.12 |
| React | 18 |
| TypeScript | 5 |
| Tailwind | 3 |
| PostgreSQL | 15 |
| Tests | 45 passing |
| Coverage | 73% |

---

## ✨ Features

### 🔐 Authentication

- Email/Password registration and login
- Google OAuth integration
- JWT token-based authentication
- Password reset via email
- Profile management (name, avatar)

### 👤 User Profile

- Update profile information (name, avatar)
- Avatar upload via Cloudinary
- Change password

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
- Deadline reminders (every 12 hours)

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
| Cloudinary | - | Image hosting for avatars |

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
| Cloudinary | - | Image upload |

### Deployment

| Platform | Service |
|----------|---------|
| Render | Backend API |
| Vercel | Frontend |
| Neon | PostgreSQL |

---

## 📁 Project Structure

```text
taskflow/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py
│   │   │       ├── projects.py
│   │   │       ├── tasks.py
│   │   │       ├── members.py
│   │   │       ├── comments.py
│   │   │       ├── notifications.py
│   │   │       ├── invitations.py
│   │   │       ├── activities.py
│   │   │       ├── dashboard.py
│   │   │       ├── timesheet.py
│   │   │       ├── users.py
│   │   │       └── password_reset.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py
│   │   │   └── security.py
│   │   │
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── member.py
│   │   │   ├── task.py
│   │   │   ├── comment.py
│   │   │   ├── invitation.py
│   │   │   ├── notification.py
│   │   │   ├── activity.py
│   │   │   ├── timesheet.py
│   │   │   └── password_reset.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── project.py
│   │   │   ├── task.py
│   │   │   ├── member.py
│   │   │   ├── comment.py
│   │   │   ├── invitation.py
│   │   │   ├── notification.py
│   │   │   ├── timesheet.py
│   │   │   └── password_reset.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── project_service.py
│   │   │   ├── task_service.py
│   │   │   ├── activity_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── invitation_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── timesheet_service.py
│   │   │   ├── password_reset_service.py
│   │   │   └── email_service.py
│   │   │
│   │   ├── scheduler/
│   │   │   └── tasks.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_projects.py
│   │   ├── test_tasks.py
│   │   ├── test_members.py
│   │   ├── test_comments.py
│   │   ├── test_dashboard.py
│   │   ├── test_timesheet.py
│   │   └── test_integration.py
│   │
│   ├── alembic/
│   │   └── versions/
│   │       └── 38cedd8015f9_initial_migration.py
│   │
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── Dockerfile
│   └── entrypoint.sh
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── Avatar.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── MembersList.tsx
│   │   │   ├── NotificationBell.tsx
│   │   │   └── Timesheet.tsx
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Projects.tsx
│   │   │   ├── ProjectBoard.tsx
│   │   │   ├── MyTasks.tsx
│   │   │   ├── TaskDetails.tsx
│   │   │   ├── MembersManagement.tsx
│   │   │   ├── NotificationsPage.tsx
│   │   │   ├── TimesheetReport.tsx
│   │   │   ├── Profile.tsx
│   │   │   ├── Settings.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── ForgotPassword.tsx
│   │   │   ├── ResetPassword.tsx
│   │   │   ├── InvitationAccept.tsx
│   │   │   └── AuthCallback.tsx
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   │
│   ├── public/
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml
├── render.yaml
├── .dockerignore
├── .gitignore
├── .env.production.example
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Installation |
|------|---------|--------------|
| Python | 3.11+ | [Download](https://www.python.org/downloads/) |
| Node.js | 18+ | [Download](https://nodejs.org/) |
| PostgreSQL | 15+ | [Download](https://www.postgresql.org/download/) |
| Docker | Latest | [Download](https://www.docker.com/products/docker-desktop/) |

### Option 1: Local Development

#### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/RahafMoualla97/taskflow.git
cd taskflow/backend

# 2. Create and activate virtual environment
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit .env with your credentials

# 6. Run database migrations
alembic upgrade head

# 7. Start the server
uvicorn app.main:app --reload
```

Backend will run at:

http://localhost:8000

#### Frontend Setup

```bash
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
```

Frontend will run at:

http://localhost:5173

### Option 2: Docker

```bash
# 1. Start all services
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f

# 4. Stop services
docker-compose down
```

Services:

| Service | URL |
|---------|-----|
| Backend | http://localhost:8000 |
| Frontend | http://localhost:5173 |
| Database | localhost:5433 |

---

## 📚 API Documentation

Once the backend is running, you can access:

| Documentation | URL |
|---------------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |

### Main API Endpoints

#### 🔐 Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login with email/password |
| GET | `/api/v1/auth/google` | Google OAuth login |
| GET | `/api/v1/auth/users/me` | Get current user profile |
| PUT | `/api/v1/auth/users/me` | Update current user profile |

#### 🔑 Password Reset

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/password-reset/request` | Request password reset |
| POST | `/api/v1/password-reset/verify` | Verify reset token |
| POST | `/api/v1/password-reset/reset` | Reset password |
| GET | `/api/v1/password-reset/user` | Get user from token |

#### 📁 Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/projects/` | Create a new project |
| GET | `/api/v1/projects/` | Get all user projects |
| GET | `/api/v1/projects/search` | Search projects |
| GET | `/api/v1/projects/{id}` | Get project by ID |
| PUT | `/api/v1/projects/{id}` | Update project |
| DELETE | `/api/v1/projects/{id}` | Delete project |

#### ✅ Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/tasks/` | Create a new task |
| GET | `/api/v1/tasks/project/{project_id}` | Get project tasks |
| GET | `/api/v1/tasks/search` | Search tasks |
| GET | `/api/v1/tasks/{id}` | Get task by ID |
| PUT | `/api/v1/tasks/{id}` | Update task |
| PATCH | `/api/v1/tasks/{id}/status` | Update task status |
| DELETE | `/api/v1/tasks/{id}` | Delete task |

#### 👥 Members

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects/{id}/members` | Get project members |
| POST | `/api/v1/projects/{id}/members` | Add member to project |
| PUT | `/api/v1/projects/{id}/members/{user_id}` | Update member role |
| DELETE | `/api/v1/projects/{id}/members/{user_id}` | Remove member |

#### 💬 Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/comments/task/{task_id}` | Add comment |
| GET | `/api/v1/comments/task/{task_id}` | Get task comments |
| DELETE | `/api/v1/comments/{id}` | Delete comment |

#### 🔔 Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | Get notifications |
| GET | `/api/v1/notifications/unread-count` | Get unread count |
| PATCH | `/api/v1/notifications/{id}/read` | Mark as read |
| PATCH | `/api/v1/notifications/read-all` | Mark all as read |
| DELETE | `/api/v1/notifications/{id}` | Delete notification |

#### 📨 Invitations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/invitations/` | Create invitation |
| POST | `/api/v1/invitations/accept` | Accept invitation |
| GET | `/api/v1/invitations/check` | Check invitation validity |

#### ⏱️ Timesheets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/timesheets/` | Log work hours |
| GET | `/api/v1/timesheets/task/{task_id}` | Get task timesheets |
| GET | `/api/v1/timesheets/my` | Get user timesheets |
| GET | `/api/v1/timesheets/weekly-summary` | Get weekly summary |
| DELETE | `/api/v1/timesheets/{id}` | Delete timesheet |

#### 📊 Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/stats` | Get dashboard stats |
| GET | `/api/v1/dashboard/tasks/recent` | Get recent tasks |
| GET | `/api/v1/dashboard/tasks/overdue` | Get overdue tasks |
| GET | `/api/v1/dashboard/tasks/my` | Get my tasks |
| GET | `/api/v1/dashboard/advanced-stats` | Get advanced stats |

#### 📝 Activities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/activities/project/{project_id}` | Get project activities |
| GET | `/api/v1/activities/task/{task_id}` | Get task activities |
| GET | `/api/v1/activities/recent` | Get recent activities |

---

## 🧪 Testing

```bash
# 1. Navigate to backend
cd backend

# 2. Activate virtual environment

# Linux/Mac
source venv/bin/activate

# Windows
# venv\Scripts\activate

# 3. Run all tests
pytest tests/ -v

# 4. Run tests with coverage
pytest tests/ -v --cov=app --cov-report=term-missing

# 5. Generate HTML coverage report
pytest tests/ -v --cov=app --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the coverage report.

### Test Coverage

| Metric | Value |
|--------|-------|
| Total Tests | 45 |
| Passing | ✅ 45 (100%) |
| Code Coverage | 73% |

---

## 🌐 Deployment

### Backend — Render

1. Push your code to GitHub.
2. Go to the Render Dashboard.
3. Click **New + → Web Service**.
4. Connect your GitHub repository.
5. Configure:

```text
Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

6. Add environment variables according to your `.env.example`.
7. Click **Create Web Service**.

### Frontend — Vercel

1. Push your code to GitHub.
2. Go to the Vercel Dashboard.
3. Click **Add New → Project**.
4. Import your GitHub repository.
5. Configure:

```text
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
```

6. Add the `VITE_API_URL` environment variable.
7. Click **Deploy**.

### Database — Neon

1. Create a new Neon project.
2. Copy the connection string.
3. Add it to the Render environment variables.

---

## 📝 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
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

# ========== Email (Maileroo) ==========
MAILEROO_API_KEY=your-maileroo-api-key
FROM_EMAIL=noreply@taskflow.com

# ========== Cloudinary ==========
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# ========== Environment ==========
ENVIRONMENT=development
DEBUG=true
```

> ⚠️ Never commit `.env` or any file containing secrets to version control.

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch:

```bash
git checkout -b feature/amazing-feature
```

3. Commit your changes:

```bash
git commit -m "Add amazing feature"
```

4. Push to the branch:

```bash
git push origin feature/amazing-feature
```

5. Open a Pull Request.

### Code Style

- **Backend:** Follow PEP 8
- **Frontend:** Follow ESLint + Prettier

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Rahaf Moualla**

- **GitHub:** [@RahafMoualla97](https://github.com/RahafMoualla97)
- **LinkedIn:** [Rahaf Moualla](https://www.linkedin.com/in/rahaf-moualla-767111325/)

---

## 🙏 Acknowledgments

- FastAPI — Modern Python web framework
- React — UI library
- Tailwind CSS — Utility-first CSS framework
- PostgreSQL — Relational database
- Cloudinary — Image hosting
- Vercel — Frontend hosting
- Render — Backend hosting
- Neon — PostgreSQL hosting


---

> Made with ❤️ by Rahaf Moualla