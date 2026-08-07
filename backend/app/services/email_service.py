"""
Email service for sending notifications via SMTP.

This service handles:
- Project invitation emails with accept links
- Task assignment notifications
- HTML email templates with styling
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings

# Configure logger
logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending various types of email notifications."""

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Internal method to send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.FROM_EMAIL)

        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"📧 [START] Sending email to {to_email}")
            logger.info(f"📧 [STEP 1] Subject: {subject}")
            logger.info(f"📧 [STEP 1] From: {from_email or settings.FROM_EMAIL}")

            msg = MIMEMultipart('alternative')
            msg['From'] = f"TaskFlow <{from_email or settings.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(html_content, 'html'))
            logger.info("📧 [STEP 2] Email message created")

            logger.info(f"📧 [STEP 3] Connecting to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")

            # Connect to SMTP server
            if settings.EMAIL_PORT == 465:
                logger.info("📧 [STEP 3] Using SSL connection (port 465)")
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                logger.info("📧 [STEP 3] Using STARTTLS connection (port 587)")
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.starttls()

            logger.info("📧 [STEP 4] Connection established, logging in...")
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            logger.info("📧 [STEP 5] Login successful")

            logger.info(f"📧 [STEP 6] Sending email to {to_email}...")
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
            server.quit()

            logger.info(f"✅ Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed: {e}")
            logger.error("❌ Please check EMAIL_USERNAME and EMAIL_PASSWORD")
            return False

        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error: {e}")
            return False

        except ConnectionError as e:
            logger.error(f"❌ Connection error: {e}")
            logger.error("❌ Network unreachable - Render may be blocking SMTP ports")
            logger.error("❌ Try changing EMAIL_PORT to 465 or use a different email service")
            return False

        except Exception as e:
            logger.error(f"❌ Error sending email to {to_email}: {str(e)}")
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
        logger.info("=" * 60)
        logger.info(f"📧 [INVITATION] Sending invitation to {to_email}")
        logger.info(f"📧 [INVITATION] Project: {project_name}")
        logger.info(f"📧 [INVITATION] Inviter: {inviter_name}")

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

        result = EmailService._send_email(to_email, subject, html_content)

        if result:
            logger.info(f"✅ Invitation email sent to {to_email}")
        else:
            logger.error(f"❌ Failed to send invitation email to {to_email}")

        logger.info("=" * 60)
        return result

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
        logger.info("=" * 60)
        logger.info(f"📧 [TASK_ASSIGN] Sending task assignment to {to_email}")
        logger.info(f"📧 [TASK_ASSIGN] Task: {task_title}")
        logger.info(f"📧 [TASK_ASSIGN] Project: {project_name}")

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

        result = EmailService._send_email(to_email, subject, html_content)

        if result:
            logger.info(f"✅ Task assignment email sent to {to_email}")
        else:
            logger.error(f"❌ Failed to send task assignment email to {to_email}")

        logger.info("=" * 60)
        return result