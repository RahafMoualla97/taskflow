"""
Email service for sending notifications via Maileroo HTTP API.
"""
import requests
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications using Maileroo HTTP API."""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email via Maileroo HTTP API.
        """
        try:
            logger.info(f"📧 [MAILEROO_API] Attempting to send email to {to_email}")

            if not settings.MAILEROO_API_KEY:
                logger.error("❌ MAILEROO_API_KEY is not set")
                return False

            API_URL = "https://smtp.maileroo.com/api/v2/emails"
            FROM_EMAIL = from_email or settings.FROM_EMAIL

            payload = {
                "from": {
                    "address": FROM_EMAIL,
                    "display_name": "TaskFlow"
                },
                "to": [
                    {
                        "address": to_email,
                        "display_name": "User"
                    }
                ],
                "subject": subject,
                "html": html_content
            }

            headers = {
                "Authorization": f"Bearer {settings.MAILEROO_API_KEY}",
                "Content-Type": "application/json"
            }

            response = requests.post(API_URL, json=payload, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                logger.info(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"❌ Failed to send email: {response.text}")
                return False

        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return False

    @staticmethod
    def send_invitation_email(
        to_email: str,
        token: str,
        project_name: str,
        inviter_name: str
    ) -> bool:
        """
        Send a project invitation email.
        """
        accept_url = f"{settings.FRONTEND_URL}/invitations/accept?token={token}"
        subject = f"Invitation to join {project_name} on TaskFlow"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #fff; }}
                .header {{ background-color: #4a90e2; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .button {{ display: inline-block; background-color: #4a90e2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; border-top: 1px solid #ddd; }}
                .button:hover {{ background-color: #357abd; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">TaskFlow Invitation</h2>
                </div>
                <div class="content">
                    <h3>Hello!</h3>
                    <p><strong>{inviter_name}</strong> has invited you to join the project <strong>{project_name}</strong> on TaskFlow.</p>
                    <p>Click the button below to accept the invitation:</p>
                    <div style="text-align: center;">
                        <a href="{accept_url}" class="button" style="color: white;">Accept Invitation</a>
                    </div>
                    <p>This invitation will expire in <strong>7 days</strong>.</p>
                    <p>If you don't have a TaskFlow account yet, you'll be able to create one when you accept the invitation.</p>
                </div>
                <div class="footer">
                    <p>This email was sent by TaskFlow. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)

    @staticmethod
    def send_task_assignment_email(
        to_email: str,
        task_title: str,
        project_name: str,
        assigner_name: str
    ) -> bool:
        """
        Send a task assignment notification email.
        """
        subject = f"New task assigned: {task_title}"
        task_url = f"{settings.FRONTEND_URL}/tasks"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px; background-color: #fff; }}
                .header {{ background-color: #f39c12; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 20px; }}
                .button {{ display: inline-block; background-color: #f39c12; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #777; border-top: 1px solid #ddd; }}
                .button:hover {{ background-color: #d68910; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0;">New Task Assigned</h2>
                </div>
                <div class="content">
                    <h3>Hello!</h3>
                    <p><strong>{assigner_name}</strong> has assigned you a new task in project <strong>{project_name}</strong>.</p>
                    <h3>Task: {task_title}</h3>
                    <p>Log in to TaskFlow to view the full details and start working on it.</p>
                    <div style="text-align: center;">
                        <a href="{task_url}" class="button" style="color: white;">View Task</a>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent by TaskFlow. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService._send_email(to_email, subject, html_content)