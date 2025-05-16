import os
import sys
import requests
from requests.auth import HTTPBasicAuth

# Read console log from stdin
console_log = sys.stdin.read()

# Environment variables from Jenkins
jira_user = os.environ['JIRA_USER']
jira_token = os.environ['JIRA_API_TOKEN']
jira_url = os.environ['JIRA_URL']
project_key = os.environ['JIRA_PROJECT_KEY']

# Prepare the Jira issue payload
issue_data = {
    "fields": {
        "project": {
            "key": project_key
        },
        "summary": f"Jenkins build failed: {os.environ.get('JOB_NAME')} #{os.environ.get('BUILD_NUMBER')}",
        "description": f"The Jenkins build failed. Console output:\n\n{console_log[:1000]}...",  # Truncate log
        "issuetype": {
            "name": "Task"
        }
    }
}

# Create the issue via Jira REST API
response = requests.post(
    f"{jira_url}/rest/api/3/issue",
    json=issue_data,
    auth=HTTPBasicAuth(jira_user, jira_token),
    headers={"Content-Type": "application/json"}
)

if response.status_code == 201:
    issue_key = response.json().get("key")
    print(f"✅ Jira ticket created successfully: {issue_key}")
else:
    print(f"❌ Failed to create Jira ticket: {response.status_code}")
    print(response.text)
