import os
import requests
from requests.auth import HTTPBasicAuth

# === Configuration ===
jira_base_url = "https://yourcompany.atlassian.net"  # Replace with your Jira base URL

# These should be injected as environment variables from Jenkins
jira_user = os.getenv("JIRA_USER")
jira_token = os.getenv("JIRA_API_TOKEN")  # API token or password
jira_project_key = os.getenv("JIRA_PROJECT_KEY")

# === Jenkins Environment Variables ===
build_number = os.getenv("BUILD_NUMBER", "Unknown")
job_name = os.getenv("JOB_NAME", "Unknown")
build_url = os.getenv("BUILD_URL", "Unknown")

# === Issue Summary & Description ===
summary = f" Build Failed - {job_name} #{build_number}"
description = (
    f"*Build Failure Notification*\n\n"
    f"* Job: {job_name}\n"
    f"* Build Number: {build_number}\n"
    f"* Build URL: {build_url}\n"
)

# === Jira API Endpoint ===
url = f"{jira_base_url}/rest/api/2/issue"

# === Jira Issue Payload ===
payload = {
    "fields": {
        "project": {
            "key": jira_project_key
        },
        "summary": summary,
        "description": description,
        "issuetype": {
            "name": "Bug"
        }
    }
}

# === Make the Request ===
response = requests.post(
    url,
    json=payload,
    auth=HTTPBasicAuth(jira_user, jira_token),
    headers={"Content-Type": "application/json"}
)

# === Response Handling ===
if response.status_code == 201:
    issue_key = response.json().get("key", "UNKNOWN")
    print(f" Jira ticket created successfully: {issue_key}")
else:
    print(" Failed to create Jira ticket")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
