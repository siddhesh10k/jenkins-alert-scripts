import os
import sys
import smtplib
import json
import http.client
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# === Configuration ===
jira_base_url = "yourcompany.atlassian.net"  # No https:// here
jira_api_path = "/rest/api/2/issue"

# Email Configuration
EMAIL = "siddhesh10k@gmail.com"
PASSWORD = "giwo bvcf pejf knwy"
TO_EMAIL = "siddhesh.kirdat@ext.arconnet.com"

# === Email Sending Logic ===
subject = f"Build Failed: {job_name} #{build_number}"
email_body = f"""
Build failed for job: {job_name} #{build_number}
Jira Ticket: {issue_url}
Build URL: {build_url}

Description:
*Build Failure Notification*
* Job: {job_name}
* Build Number: {build_number}
* Build URL: {build_url}
"""

msg = MIMEMultipart()
msg['From'] = EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = subject
msg.attach(MIMEText(email_body, 'plain'))

# Send Email
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        print(f"✅ Email sent successfully to {TO_EMAIL}")
except Exception as e:
    print(f"❌ Failed to send email: {str(e)}")
    sys.exit(1)
