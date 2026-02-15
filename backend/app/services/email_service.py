import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv('RESEND_API_KEY')


def send_hot_lead_notification(lead_data: dict) -> bool:
    """Send email for hot leads"""
    
    if lead_data['quality_score'] < 70:
        return False
    
    try:
        params = {
            "from": "leads@resend.dev",
            "to": [os.getenv('NOTIFICATION_EMAIL')],
            "subject": f"🔥 Hot Lead: {lead_data['name']} (Score: {lead_data['quality_score']})",
            "html": f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="background: #2563eb; color: white; padding: 20px; border-radius: 8px;">
                        <h1>🔥 New Hot Lead!</h1>
                    </div>
                    <div style="background: #f9fafb; padding: 20px; margin-top: 10px;">
                        <h2 style="color: #059669;">Score: {lead_data['quality_score']}/100</h2>
                        <p><strong>Name:</strong> {lead_data['name']}</p>
                        <p><strong>Email:</strong> {lead_data['email']}</p>
                        <p><strong>Phone:</strong> {lead_data['phone']}</p>
                        <p><strong>Message:</strong> {lead_data['message']}</p>
                        <hr>
                        <h3>AI Analysis</h3>
                        <p><strong>Goal:</strong> {lead_data['goal']}</p>
                        <p><strong>Timeline:</strong> {lead_data['timeline']}</p>
                        <p><strong>Budget:</strong> {lead_data['budget_range']}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        }
        
        email = resend.Emails.send(params)
        print(f"Email sent: {email}")
        return True
        
    except Exception as e:
        print(f"Email error: {e}")
        return False