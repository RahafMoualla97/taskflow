"""
Simple script to test Maileroo HTTP API connection (Render-compatible).
"""
import os
import requests
from dotenv import load_dotenv

# تحميل ملف الـ .env محلياً أثناء التطوير
load_dotenv()

def test_email():
    # سحب المفتاح بأمان من متغيرات البيئة، وفي حال عدم وجوده يستخدم المفتاح الافتراضي الخاص بكِ
    API_KEY = os.getenv("MAILEROO_API_KEY", "68456344f7cdbe68bcbb5c60f1711ae6bb2fe55d29db722ed7f3aa7356668823")
    
    # الرابط الصحيح لإرسال الطلبات لـ Maileroo API v2
    API_URL = "https://smtp.maileroo.com/api/v2/emails"
    
    FROM_EMAIL = "rahafmoualla31297@60e4162f569905c4.maileroo.org"
    TO_EMAIL = "rahafmoualla29@gmail.com"

    print("📧 Testing Maileroo HTTP API...")

    html_content = """
    <html>
    <body>
        <h2 style="color: #4a90e2;">✅ Maileroo API Test Successful!</h2>
        <p>This email was sent via Maileroo HTTP API from Render Free Tier.</p>
        <hr>
        <p style="color: #888; font-size: 12px;">TaskFlow Application</p>
    </body>
    </html>
    """

    payload = {
        "from": {
            "address": FROM_EMAIL,
            "display_name": "TaskFlow Test"
        },
        "to": [
            {
                "address": TO_EMAIL,
                "display_name": "Rahaf"
            }
        ],
        "subject": "✅ Test Email from Maileroo API",
        "html": html_content
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        print("📧 Connecting via HTTP API to Maileroo...")
        response = requests.post(API_URL, json=payload, headers=headers)
        
        # تم تصحيح الفحص هنا ليدعم حالات النجاح 200 و 201
        if response.status_code in [200, 201]:
            print("✅ Email sent successfully via API!")
            return {"status": "success", "message": f"Email sent to {TO_EMAIL}"}
        else:
            print(f"❌ API Error ({response.status_code}): {response.text}")
            return {"status": "error", "message": response.text}
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    print(test_email())
