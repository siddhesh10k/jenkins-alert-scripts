import os
import sys
import json
import base64
import http.client
from urllib.parse import urlparse

# Read log filename from command-line argument
log_filename = sys.argv[1]
with open(log_filename, 'r') as f:
    console_log = f.read()

# Jenkins environment variables
jira_user = os.environ['JIRA_USER']
jira_token = os.environ['JIRA_API_TOKEN']
jira_url = os.environ['JIRA_URL']
project_key = os.environ['JIRA_PROJECT_KEY']
job_name = os.environ.get('JOB_NAME', 'Unknown Job')
build_number = os.environ.get('BUILD_NUMBER', '0')

summary = f"Jenkins build failed: {job_name} #{build_number}"
description = "Jenkins build failed.\nPlease see the attached log file for details."

issue_data = {
    "fields": {
        "project": {"key": project_key},
        "summary": summary,
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": description}
                    ]
                }
            ]
        },
        "issuetype": {"name": "Task"}
    }
}

# Prepare auth and headers
auth_string = f"{jira_user}:{jira_token}"
auth_bytes = base64.b64encode(auth_string.encode()).decode()
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_bytes}"
}

# Parse Jira URL
parsed_url = urlparse(jira_url)
conn = http.client.HTTPSConnection(parsed_url.netloc)

# Create Jira issue
conn.request(
    "POST",
    "/rest/api/3/issue",
    body=json.dumps(issue_data),
    headers=headers
)

response = conn.getresponse()
response_body = response.read().decode()

def upload_attachment(issue_key, file_path):
    conn = http.client.HTTPSConnection(parsed_url.netloc)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode() + file_data + f"\r\n--{boundary}--\r\n".encode()

    attachment_headers = {
        "Authorization": f"Basic {auth_bytes}",
        "X-Atlassian-Token": "no-check",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }

    conn.request(
        "POST",
        f"/rest/api/3/issue/{issue_key}/attachments",
        body=body,
        headers=attachment_headers
    )
    resp = conn.getresponse()
    print(f"📎 Attachment upload status: {resp.status}")
    print(resp.read().decode())

if response.status == 201:
    issue_key = json.loads(response_body).get("key")
    print(f"✅ Jira ticket created successfully: {issue_key}")
    upload_attachment(issue_key, log_filename)
else:
    print(f"❌ Failed to create Jira ticket: {response.status}")
    print(response_body)
