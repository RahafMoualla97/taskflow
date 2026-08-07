"""
Email service for sending notifications.

Supported email delivery methods:
1. Gmail SMTP (Active) - Uses ports 25/465/587
   - Works with Gmail App Password
   - Currently used in production

2. Brevo HTTP API (Commented) - Uses port 443 (HTTPS)
   - No IP restrictions, works on Render Free Plan
   - Better logging and analytics
   - Uncomment when Brevo account is activated

3. Resend API (Commented) - Uses port 443 (HTTPS)
   - Alternative to Brevo
   - Uncomment when domain is verified

4. SendGrid SMTP (Commented) - Uses port 587
   - Alternative SMTP provider
   - Uncomment when SendGrid API key is set
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# import requests  # Uncomment for HTTP API methods
from app.core.config import settings

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailService:
    """
    Service for sending email notifications.
    Currently uses Gmail SMTP with App Password.
    """

    @staticmethod
    def _send_email_smtp_gmail(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using Gmail SMTP.

        This is the currently active method.
        Uses Gmail App Password for authentication.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            from_email: Sender email (defaults to settings.FROM_EMAIL)

        Returns:
            True if email was sent successfully, False otherwise
        """
        logger.info("=" * 60)
        logger.info("📧 [START] Email sending process initiated")
        logger.info(f"📧 [STEP 1] Target email: {to_email}")
        logger.info(f"📧 [STEP 1] Subject: {subject}")
        logger.info(f"📧 [STEP 1] From: {from_email or settings.FROM_EMAIL}")

        try:
            logger.info("📧 [STEP 2] Creating email message...")
            msg = MIMEMultipart('alternative')
            msg['From'] = f"TaskFlow <{from_email or settings.FROM_EMAIL}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            logger.info("📧 [STEP 2] ✅ Email message created successfully")

            logger.info(f"📧 [STEP 3] Connecting to SMTP server: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")

            if settings.EMAIL_PORT == 465:
                logger.info("📧 [STEP 3] Using SSL connection (port 465)")
                server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
            else:
                logger.info("📧 [STEP 3] Using STARTTLS connection (port 587)")
                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                logger.info("📧 [STEP 3] Starting TLS...")
                server.starttls()

            logger.info("📧 [STEP 3] ✅ SMTP connection established")

            logger.info(f"📧 [STEP 4] Attempting login with: {settings.EMAIL_USERNAME}")
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            logger.info("📧 [STEP 4] ✅ SMTP login successful")

            logger.info(f"📧 [STEP 5] Sending email to: {to_email}")
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
            logger.info("📧 [STEP 5] ✅ Email sent successfully")

            logger.info("📧 [STEP 6] Closing SMTP connection...")
            server.quit()
            logger.info("📧 [STEP 6] ✅ SMTP connection closed")

            logger.info("=" * 60)
            logger.info(f"📧 [SUCCESS] Email delivered to {to_email}")
            logger.info("=" * 60)
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error("=" * 60)
            logger.error(f"❌ [ERROR] SMTP Authentication failed: {e}")
            logger.error("❌ [ERROR] Please check EMAIL_USERNAME and EMAIL_PASSWORD")
            logger.error("❌ [ERROR] Make sure you're using an App Password, not your Gmail password")
            logger.error("=" * 60)
            return False

        except smtplib.SMTPException as e:
            logger.error("=" * 60)
            logger.error(f"❌ [ERROR] SMTP error: {e}")
            logger.error("❌ [ERROR] This could be due to network restrictions or server issues")
            logger.error("=" * 60)
            return False

        except ConnectionError as e:
            logger.error("=" * 60)
            logger.error(f"❌ [ERROR] Connection error: {e}")
            logger.error("❌ [ERROR] Render Free Plan may be blocking outbound SMTP connections")
            logger.error("❌ [ERROR] Try using Brevo HTTP API instead (commented in code)")
            logger.error("=" * 60)
            return False

        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ [ERROR] Unexpected error: {e}")
            logger.error(f"❌ [ERROR] Error type: {type(e).__name__}")
            logger.error("=" * 60)
            return False

    # ================================================================
    # OPTION 2: Brevo HTTP API (Commented)
    # Uncomment to use Brevo HTTP API instead of Gmail SMTP
    # ================================================================

    # @staticmethod
    # def _send_email_brevo_api(
    #     to_email: str,
    #     subject: str,
    #     html_content: str,
    #     from_email: Optional[str] = None
    # ) -> bool:
    #     """
    #     Send email using Brevo HTTP API.
    #
    #     This method uses port 443 (HTTPS) and works on all platforms.
    #     No IP whitelisting required.
    #     """
    #     try:
    #         logger.info("=" * 60)
    #         logger.info("📧 [START] Brevo API email process")
    #         logger.info(f"📧 Target email: {to_email}")
    #
    #         if not settings.BREVO_API_KEY:
    #             logger.error("❌ BREVO_API_KEY is not set")
    #             return False
    #
    #         import requests
    #
    #         url = "https://api.brevo.com/v3/smtp/email"
    #         headers = {
    #             "accept": "application/json",
    #             "api-key": settings.BREVO_API_KEY,
    #             "content-type": "application/json"
    #         }
    #         data = {
    #             "sender": {
    #                 "name": "TaskFlow",
    #                 "email": from_email or settings.FROM_EMAIL
    #             },
    #             "to": [{"email": to_email}],
    #             "subject": subject,
    #             "htmlContent": html_content
    #         }
    #
    #         logger.info("📧 Sending request to Brevo API...")
    #         response = requests.post(url, json=data, headers=headers, timeout=30)
    #
    #         if response.status_code == 201:
    #             logger.info(f"✅ Brevo API: Email sent successfully to {to_email}")
    #             return True
    #         else:
    #             logger.error(f"❌ Brevo API failed: {response.status_code} - {response.text}")
    #             return False
    #
    #     except Exception as e:
    #         logger.error(f"❌ Brevo API error: {e}")
    #         return False

    # ================================================================
    # OPTION 3: Resend API (Commented)
    # ================================================================

    # @staticmethod
    # def _send_email_resend_api(...):
    #     """Send email using Resend API."""
    #     # ... (code with logs)

    # ================================================================
    # OPTION 4: SendGrid SMTP (Commented)
    # ================================================================

    # @staticmethod
    # def _send_email_sendgrid_smtp(...):
    #     """Send email using SendGrid SMTP."""
    #     # ... (code with logs)

    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send email using the currently active method.

        Currently using: Gmail SMTP
        """
        logger.info(f"📧 [ROUTER] Using Gmail SMTP as primary method")
        return EmailService._send_email_smtp_gmail(to_email, subject, html_content, from_email)

    @staticmethod
    def send_invitation_email(
        to_email: str,
        token: str,
        project_name: str,
        inviter_name: str
    ) -> bool:
        """
        Send a project invitation email.

        This is the main entry point for invitation emails.
        Contains detailed logging for each step.
        """
        logger.info("=" * 60)
        logger.info("📧 [INVITATION] Starting invitation email process")
        logger.info(f"📧 [INVITATION] Recipient: {to_email}")
        logger.info(f"📧 [INVITATION] Project: {project_name}")
        logger.info(f"📧 [INVITATION] Inviter: {inviter_name}")
        logger.info(f"📧 [INVITATION] Token: {token}")

        try:
            accept_url = f"{settings.FRONTEND_URL}/invitations/accept?token={token}"
            subject = f"Invitation to join {project_name} on TaskFlow"

            logger.info("📧 [INVITATION] Building email HTML...")

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

            logger.info("📧 [INVITATION] ✅ HTML built successfully")
            logger.info(f"📧 [INVITATION] Accept URL: {accept_url}")

            logger.info("📧 [INVITATION] Delegating to _send_email()...")
            result = EmailService._send_email(to_email, subject, html_content)

            if result:
                logger.info("=" * 60)
                logger.info(f"📧 [INVITATION] ✅✅✅ Email sent successfully to {to_email}")
                logger.info("=" * 60)
            else:
                logger.error("=" * 60)
                logger.error(f"📧 [INVITATION] ❌❌❌ Email sending failed for {to_email}")
                logger.error("=" * 60)

            return result

        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ [INVITATION] Critical error: {e}")
            logger.error(f"❌ [INVITATION] Error type: {type(e).__name__}")
            logger.error("=" * 60)
            return False

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
        logger.info("=" * 60)
        logger.info(f"📧 [TASK_ASSIGN] Starting task assignment email process")
        logger.info(f"📧 [TASK_ASSIGN] Recipient: {to_email}")
        logger.info(f"📧 [TASK_ASSIGN] Task: {task_title}")
        logger.info(f"📧 [TASK_ASSIGN] Project: {project_name}")
        logger.info(f"📧 [TASK_ASSIGN] Assigner: {assigner_name}")

        try:
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
                logger.error(f"❌ Task assignment email failed for {to_email}")

            return result

        except Exception as e:
            logger.error(f"❌ Task assignment email error: {e}")
            return False