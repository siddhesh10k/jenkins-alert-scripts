import os
import sys
import json
import base64
import http.client
from urllib.parse import urlparse

# Jenkins environment variables
jira_user = os.environ['JIRA_USER']
jira_token = os.environ['JIRA_API_TOKEN']
jira_url = os.environ['JIRA_URL']
project_key = os.environ['JIRA_PROJECT_KEY']
job_name = os.environ.get('JOB_NAME')
build_number = os.environ.get('BUILD_NUMBER')
log_filename = f"console_output_{build_number}.txt"

# Read console log from file (NOT stdin)
if os.path.exists(log_filename):
    with open(log_filename, 'r') as f:
        console_log = f.read()
else:
    console_log = "⚠️ Console log file not found."

# Summary and description
summary = f"Jenkins build failed: {job_name} #{build_number}"
description = "Jenkins build failed.\nPlease see the attached log file for details."

# Jira issue payload (using Atlassian Document Format)
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
                        {
                            "type": "text",
                            "text": description
                        }
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

# Parse Jira URL and create connection
parsed_url = urlparse(jira_url)
conn = http.client.HTTPSConnection(parsed_url.netloc)

# Send POST request to create Jira issue
conn.request(
    "POST",
    "/rest/api/3/issue",
    body=json.dumps(issue_data),
    headers=headers
)

response = conn.getresponse()
response_body = response.read().decode()

# Upload attachment function
def upload_attachment(issue_key, file_path):
    print(f"🚀 Starting upload_attachment for issue: {issue_key}, file: {file_path}")

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"⚠️ File '{file_path}' is empty or not found.")
        return

    with open(file_path, 'rb') as file:
        file_data = file.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    crlf = "\r\n"
    file_name = os.path.basename(file_path)

    body_pre = (
        f"--{boundary}{crlf}"
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"{crlf}'
        f"Content-Type: application/octet-stream{crlf}{crlf}"
    ).encode()

    body_post = f"{crlf}--{boundary}--{crlf}".encode()
    body = body_pre + file_data + body_post

    attachment_headers = {
        "Authorization": f"Basic {auth_bytes}",
        "X-Atlassian-Token": "no-check",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body))
    }

    conn = http.client.HTTPSConnection(parsed_url.netloc)
    conn.request(
        "POST",
        f"/rest/api/3/issue/{issue_key}/attachments",
        body=body,
        headers=attachment_headers
    )
    resp = conn.getresponse()
    print(f"📎 Attachment upload status: {resp.status}")
    print(resp.read().decode())

# Final response handling
if response.status == 201:
    issue_key = json.loads(response_body).get("key")
    print(f"✅ Jira ticket created successfully: {issue_key}")
    upload_attachment(issue_key, log_filename)
else:
    print(f"❌ Failed to create Jira ticket: {response.status}")
    print(response_body)
