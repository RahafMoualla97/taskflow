from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_active_user
from app.models.user import User

# استيراد دالة الفحص مباشرة من الملف الفرعي الخاص بكِ
from test_email import test_email

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/email")
def test_email_endpoint(current_user: User = Depends(get_current_active_user)):
    """
    Test email connection using Maileroo HTTP API (Direct Call).
    """
    # استدعاء الدالة مباشرة بشكل سريع ونظيف بدون subprocess
    result = test_email()
    
    return {
        "status": "ok",
        "result": result
    }