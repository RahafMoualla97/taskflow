"""
Simple script to test Gmail SMTP connection.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_email():
    EMAIL_HOST = "smtp.gmail.com"
    EMAIL_PORT = 587
    EMAIL_USERNAME = "rahafmoualla31297@gmail.com"
    EMAIL_PASSWORD = "bxye yhke wewu zqrx"
    FROM_EMAIL = "rahafmoualla31297@gmail.com"
    TO_EMAIL = "rahafmoualla29@gmail.com"

    print("📧 Testing Gmail SMTP...")
    
    msg = MIMEMultipart('alternative')
    msg['From'] = f"TaskFlow Test <{FROM_EMAIL}>"
    msg['To'] = TO_EMAIL
    msg['Subject'] = "✅ Test Email from Render Server"
    msg.attach(MIMEText("<h2>✅ Test from Render</h2><p>If you see this, SMTP is working!</p>", 'html'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully!")
        return {"status": "success", "message": f"Email sent to {TO_EMAIL}"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(test_email())