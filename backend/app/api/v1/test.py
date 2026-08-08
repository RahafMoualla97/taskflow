from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_active_user
from app.models.user import User
import subprocess
import sys
import os

router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/email")
def test_email_endpoint(current_user: User = Depends(get_current_active_user)):
    """
    Test Gmail SMTP connection.
    """
    # استدعاء سكربت test_email.py
    script_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "test_email.py")
    result = subprocess.run(
        [sys.executable, script_path],
        capture_output=True,
        text=True
    )
    return {
        "status": "ok",
        "stdout": result.stdout,
        "stderr": result.stderr
    }