import os
import sys
import json
import base64
import http.client
from urllib.parse import urlparse

# Read console log from stdin
console_log = sys.stdin.read()

# Jenkins environment variables
jira_user = os.environ['JIRA_USER']
jira_token = os.environ['JIRA_API_TOKEN']
jira_url = os.environ['JIRA_URL']
project_key = os.environ['JIRA_PROJECT_KEY']
job_name = os.environ.get('JOB_NAME')
build_number = os.environ.get('BUILD_NUMBER')

# Jira issue payload
issue_data = {
    "fields": {
        "project": {"key": project_key},
        "summary": f"Jenkins build failed: {job_name} #{build_number}",
        "description": f"The Jenkins build failed. Console output:\n\n{console_log[:1000]}...",
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

# Parse URL
parsed_url = urlparse(jira_url)
conn = http.client.HTTPSConnection(parsed_url.netloc)

# Send POST request to Jira
conn.request(
    "POST",
    "/rest/api/3/issue",
    body=json.dumps(issue_data),
    headers=headers
)

response = conn.getresponse()
response_body = response.read().decode()

# Handle response
if response.status == 201:
    issue_key = json.loads(response_body).get("key")
    print(f"✅ Jira ticket created successfully: {issue_key}")
else:
    print(f"❌ Failed to create Jira ticket: {response.status}")
    print(response_body)
