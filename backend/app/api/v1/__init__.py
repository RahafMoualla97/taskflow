from fastapi import APIRouter
from app.api.v1 import auth, projects, members, tasks, comments, invitations, notifications, activities, dashboard, users, timesheet

router = APIRouter()
router.include_router(auth.router)
router.include_router(projects.router)
router.include_router(members.router)
router.include_router(tasks.router)
router.include_router(comments.router)
router.include_router(invitations.router)
router.include_router(notifications.router)
router.include_router(activities.router)
router.include_router(dashboard.router)
router.include_router(users.router)
router.include_router(timesheet.router)