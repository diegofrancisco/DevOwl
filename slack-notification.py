import slack
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

class Emoji:
    LIGHT = ":rotating_light:"
    WARNING = ":warning:"
    TADA = ":tada:"
    FIRE = ":fire:"
    ONE_HUNDRED = ":100:"

    def __init__(self) -> None:
        raise NotImplementedError

def generate_coverage_message() -> str:
    project_list = os.environ['PROJECT_LIST']
    sonarcloud_token = os.environ['SONARCLOUD_TOKEN']
    text = ''

    for project in project_list.split(','):
        key, value = project.split(':')
        coverage = get_sonarcloud_coverage(key, sonarcloud_token)
        # if coverage is not None:
        #     print(f"Coverage metric for project '{project_key}': {coverage}%")
        emoji = generate_status_emoji(coverage)
        text += f"{value}: *{coverage}*% {emoji}\n"

    return text

def generate_status_emoji(code_coverage: float) -> str:
    status = ":sweat:"

    if code_coverage > 0 and code_coverage < 35:
        status = Emoji.LIGHT
    elif code_coverage >= 35 and code_coverage < 60:
        status = Emoji.WARNING
    elif code_coverage >= 60 and code_coverage < 80:
        status = Emoji.TADA
    elif code_coverage >= 80 and code_coverage < 100:
        status = Emoji.FIRE
    elif code_coverage >= 100:
        status = Emoji.ONE_HUNDRED

    return status

def get_sonarcloud_coverage(project_key, sonarcloud_token):
    base_url = "https://sonarcloud.io/api/measures/component"
    
    # API endpoint to fetch coverage metric
    api_endpoint = f"{base_url}?component={project_key}&metricKeys=coverage"
    
    # Headers with authentication token
    headers = {"Authorization": f"Bearer {sonarcloud_token}"}
    
    try:
        # Make the API request
        response = requests.get(api_endpoint, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            if "component" in response_json:
                # Extract the coverage metric from the response
                coverage_metric = response_json["component"]["measures"][0]["value"]
                return float(coverage_metric)
        
        print("Failed to retrieve coverage metric. Check your project key and authentication token.")
        return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
import requests

def get_outstanding_prs(repo_owner, repo_name, github_token):
    headers = {
        "Authorization": f"Bearer {github_token}"
    }

    # GitHub API endpoint to get open pull requests
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"

    try:
        params = {
            "state": "open",
            "sort": "created",
            "direction": "desc",
            "since": (datetime.utcnow() - timedelta(weeks=1)).isoformat()
        }

        response = requests.get(api_url, headers=headers, params=params)
        if response.status_code == 200:
            prs = response.json()
            return prs
        else:
            print(f"Failed to retrieve pull requests. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred: {e}")
        return []
    
def generate_outstanding_prs_message():
    github_token = os.environ['GITHUB_TOKEN']
    repo_owner = os.environ['REPO_OWNER']
    repo_name = os.environ['REPO_NAME']
    text = ''

    outstanding_prs = get_outstanding_prs(repo_owner, repo_name, github_token)

    if outstanding_prs:
        text += f"Outstanding Pull Requests for *{repo_name}*:\n"
        for index, pr in enumerate(outstanding_prs):
            if index >= 5:
                break
            text += f"- <{pr['html_url']}|PR #{pr['number']}>: {pr['title']} ({pr['user']['login']})\n"
    else:
        print("No outstanding Pull Requests.")

    return text

def main() -> None:
    # Loading .env values
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    text = "Hoot! Hoot! Check it out, we got the code coverage for the Integrations Team's projects here:\n\n"
    text += generate_coverage_message()
    text += "\nAlso take a peak in the outstanding PR's from the team:\n\n"
    text += generate_outstanding_prs_message()

    client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
    client.chat_postMessage(channel='#slackbot-test', text=text)

if __name__ == "__main__":
    main()
