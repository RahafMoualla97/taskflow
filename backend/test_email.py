"""
Simple script to test Maileroo SMTP connection.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    # ===== بيانات Maileroo الثابتة =====
    EMAIL_HOST = "smtp.maileroo.com"
    EMAIL_PORT = 587
    EMAIL_USERNAME = "rahafmoualla31297@60e4162f569905c4.maileroo.org"
    EMAIL_PASSWORD = "a392a38cd110509ce8dff7a4"
    FROM_EMAIL = "rahafmoualla31297@60e4162f569905c4.maileroo.org"
    TO_EMAIL = "rahafmoualla29@gmail.com"
    # ===================================

    print("📧 Testing Maileroo SMTP...")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"TaskFlow Test <{FROM_EMAIL}>"
    msg['To'] = TO_EMAIL
    msg['Subject'] = "✅ Test Email from Maileroo"

    html_content = """
    <html>
    <body>
        <h2 style="color: #4a90e2;">✅ Maileroo Test Successful!</h2>
        <p>This email was sent via Maileroo SMTP from Render.</p>
        <p><strong>Time:</strong> Now</p>
        <hr>
        <p style="color: #888; font-size: 12px;">TaskFlow Application</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_content, 'html'))

    try:
        print(f"📧 Connecting to {EMAIL_HOST}:{EMAIL_PORT}...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        print("🔐 Logging in...")
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        print("📤 Sending email...")
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        return {"status": "success", "message": f"Email sent to {TO_EMAIL}"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(test_email())