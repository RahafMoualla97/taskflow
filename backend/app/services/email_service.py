"""
Email service for sending notifications.

Supports multiple email delivery methods:
1. SMTP (Traditional) - works with Gmail, SendGrid, Brevo SMTP
   - Uses ports 25, 465, or 587
   - May have issues on Render Free Plan due to outbound port restrictions
2. Brevo HTTP API (Recommended for production)
   - Uses port 443 (HTTPS)
   - Works reliably on all platforms including Render Free Plan
   - No IP whitelisting required
   - Better logging and analytics
"""
import smtplib
import requests
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications.
    
    Supports two delivery methods:
    - SMTP (traditional, may have port restrictions)
    - Brevo HTTP API (recommended, uses HTTPS port 443)
    """

    @staticmethod
    def _send_email_smtp(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using SMTP protocol.
        
        This is the traditional method. Works with Gmail, SendGrid, Brevo SMTP.
        Note: May not work on Render Free Plan due to outbound port restrictions.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.FROM_EMAIL)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"SMTP: Attempting to send email to {to_email}")
            logger.info(f"SMTP: Using host {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")

            msg = MIMEMultipart('alternative')
            msg['From'] = f"TaskFlow <{from_email or settings.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(html_content, 'html'))

            if settings.EMAIL_PORT == 465:
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.starttls()

            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
            server.quit()

            logger.info(f"SMTP: Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"SMTP: Email send failed: {e}")
            return False

    @staticmethod
    def _send_email_api(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using Brevo HTTP API.
        
        This is the recommended method for production.
        - Uses port 443 (HTTPS) - works everywhere
        - No IP restrictions
        - Faster response times
        - Better logging and analytics
        - Works reliably on Render Free Plan
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.FROM_EMAIL)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"API: Attempting to send email to {to_email}")

            if not settings.BREVO_API_KEY:
                logger.warning("BREVO_API_KEY not set, falling back to SMTP")
                return EmailService._send_email_smtp(to_email, subject, html_content, from_email)

            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "accept": "application/json",
                "api-key": settings.BREVO_API_KEY,
                "content-type": "application/json"
            }
            data = {
                "sender": {
                    "name": "TaskFlow",
                    "email": from_email or settings.FROM_EMAIL
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "htmlContent": html_content
            }

            response = requests.post(url, json=data, headers=headers, timeout=30)

            if response.status_code == 201:
                logger.info(f"API: Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"API: Failed to send email: {response.text}")
                return False

        except requests.exceptions.Timeout:
            logger.error(f"API: Timeout sending email to {to_email}")
            return False
        except Exception as e:
            logger.error(f"API: Email send failed: {e}")
            return False

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using the preferred method.
        
        Priority:
        1. Brevo HTTP API (if BREVO_API_KEY is set)
        2. SMTP (fallback)
        """
        if settings.BREVO_API_KEY:
            return EmailService._send_email_api(to_email, subject, html_content, from_email)
        else:
            return EmailService._send_email_smtp(to_email, subject, html_content, from_email)

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