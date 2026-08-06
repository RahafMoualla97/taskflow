"""
Email service for sending notifications via Resend API.
"""
import resend
from typing import Optional

from app.core.config import settings

# Initialize Resend with API key
resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Service for sending email notifications using Resend."""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email using Resend API.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.FROM_EMAIL)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            response = resend.Emails.send({
                "from": f"TaskFlow <{from_email or settings.FROM_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            })
            print(f"✅ Email sent to {to_email}: {response}")
            return True
        except Exception as e:
            print(f"❌ Email send failed: {e}")
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

        Args:
            to_email: Recipient email address
            token: Unique invitation token for acceptance
            project_name: Name of the project being invited to
            inviter_name: Name of the user who sent the invitation

        Returns:
            True if email was sent successfully, False otherwise
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

        Args:
            to_email: Recipient email address
            task_title: Title of the assigned task
            project_name: Name of the project
            assigner_name: Name of the user who assigned the task

        Returns:
            True if email was sent successfully, False otherwise
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