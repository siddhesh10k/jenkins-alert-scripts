import smtplib
from email.mime.text import MIMEText
import sys
import os

# Read console log from stdin
log_content = sys.stdin.read()

sender = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
receiver = sender  # Send to self

msg = MIMEText(log_content)
msg['Subject'] = "🚨 Jenkins Build Failed — Real-Time Console Log"
msg['From'] = sender
msg['To'] = receiver

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, [receiver], msg.as_string())
        print("✅ Email sent successfully.")
except Exception as e:
    print(f"❌ Failed to send email: {e}")
