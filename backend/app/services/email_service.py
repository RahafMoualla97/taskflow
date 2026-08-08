"""
Email service for sending notifications via SMTP (HARDCODED FOR TESTING).
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional


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
        Internal method to send an email via SMTP (HARDCODED).
        """
        try:
            # ============================================================
            # ✅ جميع الإعدادات ثابتة هنا للتجربة
            # ============================================================
            EMAIL_HOST = "smtp.gmail.com"
            EMAIL_PORT = 587
            EMAIL_USERNAME = "rahafmoualla31297@gmail.com"
            EMAIL_PASSWORD = "bxye yhke wewu zqrx"
            FROM_EMAIL = "rahafmoualla31297@gmail.com"
            TO_EMAIL = "rahafmoualla29@gmail.com"  # ثابت
            # ============================================================

            print(f"📧 [HARDCODED] Sending to: {TO_EMAIL}")
            print(f"📧 [HARDCODED] From: {FROM_EMAIL}")
            print(f"📧 [HARDCODED] Subject: {subject}")

            msg = MIMEMultipart('alternative')
            msg['From'] = f"TaskFlow <{FROM_EMAIL}>"
            msg['To'] = TO_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))

            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
            server.quit()

            print(f"✅✅✅ Email sent to {TO_EMAIL}")
            return True

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    @staticmethod
    def send_invitation_email(
        to_email: str,
        token: str,
        project_name: str,
        inviter_name: str
    ) -> bool:
        """
        Send a project invitation email (HARDCODED).
        """
        accept_url = f"https://taskflow-three-flax.vercel.app/invitations/accept?token={token}"
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
        task_url = f"https://taskflow-three-flax.vercel.app/tasks"

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