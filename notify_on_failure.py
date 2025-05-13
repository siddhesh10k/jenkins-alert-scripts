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

# === Environment Variables ===
jira_user = os.getenv("JIRA_USER")
jira_token = os.getenv("JIRA_API_TOKEN")
jira_project_key = os.getenv("JIRA_PROJECT_KEY")

build_number = os.getenv("BUILD_NUMBER", "Unknown")
job_name = os.getenv("JOB_NAME", "Unknown")
build_url = os.getenv("BUILD_URL", "Unknown")

# === Check if JIRA section should be skipped ===
disable_jira = os.getenv("DISABLE_JIRA", "false").lower() == "true"

# === Validation ===
missing_vars = []
for var in ["JIRA_USER", "JIRA_API_TOKEN", "JIRA_PROJECT_KEY"]:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

# === Summary and Description for JIRA (Only if JIRA is not disabled) ===
if not disable_jira:
    summary = f"Build Failed - {job_name} #{build_number}"
    description = (
        f"*Build Failure Notification*\n\n"
        f"* Job: {job_name}\n"
        f"* Build Number: {build_number}\n"
        f"* Build URL: {build_url}\n"
    )

    payload = {
        "fields": {
            "project": { "key": jira_project_key },
            "summary": summary,
            "description": description,
            "issuetype": { "name": "Bug" }
        }
    }

    try:
        # Prepare Basic Auth header
        auth = f"{jira_user}:{jira_token}"
        encoded_auth = base64.b64encode(auth.encode()).decode()

        # Connect to JIRA
        conn = http.client.HTTPSConnection(jira_base_url)
        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }

        conn.request("POST", jira_api_path, body=json.dumps(payload), headers=headers)
        response = conn.getresponse()
        response_body = response.read().decode()

        if response.status == 201:
            issue_key = json.loads(response_body).get("key", "UNKNOWN")
            print(f"✅ Jira ticket created successfully: {issue_key}")
            issue_url = f"https://{jira_base_url}/browse/{issue_key}"
        else:
            print("❌ Failed to create Jira ticket")
            print(f"Status Code: {response.status}")
            print(f"Response: {response_body}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Exception while creating Jira ticket: {str(e)}")
        sys.exit(1)
else:
    print("⚠️ JIRA ticket creation is disabled by DISABLE_JIRA environment variable.")
    issue_url = "N/A"

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
