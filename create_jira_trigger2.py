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
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print(f"❌ File '{file_path}' does not exist or is empty.")
        return

    conn = http.client.HTTPSConnection(parsed_url.netloc)
    with open(file_path, 'rb') as file:
        file_data = file.read()

    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    crlf = "\r\n"
    file_name = os.path.basename(file_path)

    # Construct multipart body
    body = (
        f"--{boundary}{crlf}"
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"{crlf}'
        f"Content-Type: application/octet-stream{crlf}{crlf}"
    ).encode() + file_data + f"{crlf}--{boundary}--{crlf}".encode()

    headers = {
        "Authorization": f"Basic {auth_bytes}",
        "X-Atlassian-Token": "no-check",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Content-Length": str(len(body))
    }

    conn.request(
        "POST",
        f"/rest/api/3/issue/{issue_key}/attachments",
        body=body,
        headers=headers
    )
    response = conn.getresponse()
    print(f"📎 Attachment upload status: {response.status}")
    print(response.read().decode())

