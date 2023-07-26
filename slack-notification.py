import slack
import os
import requests
from pathlib import Path
from dotenv import load_dotenv


class Emoji:
    LIGHT = ":rotating_light:"
    WARNING = ":warning:"
    TADA = ":tada:"
    FIRE = ":fire:"
    ONE_HUNDRED = ":100:"

    def __init__(self) -> None:
        raise NotImplementedError

def push_message_to_slack() -> None:
    text = "Yo! Check it out, we got the code coverage for the Integrations Team's projects here:\n\n"
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)

    client = slack.WebClient(token=os.environ['SLACK_TOKEN'])
    project_list = os.environ['PROJECT_LIST']
    sonarcloud_token = os.environ['SONARCLOUD_TOKEN']

    for project in project_list.split(','):
        key, value = project.split(':')
        coverage = get_sonarcloud_coverage(key, sonarcloud_token)
        # if coverage is not None:
        #     print(f"Coverage metric for project '{project_key}': {coverage}%")
        emoji = generate_status_emoji(coverage)
        text += f"{value}: *{coverage}*% {emoji}\n"

    client.chat_postMessage(channel='#slackbot-test', text=text)

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
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            prs = response.json()
            return prs
        else:
            print(f"Failed to retrieve pull requests. Status code: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error occurred: {e}")
        return []
    
def push_outstanding_prs_to_slack():
    github_token = "YOUR_GITHUB_TOKEN"
    repo_owner = "YOUR_REPO_OWNER"
    repo_name = "YOUR_REPO_NAME"

    outstanding_prs = get_outstanding_prs(repo_owner, repo_name, github_token)

    if outstanding_prs:
        print("Outstanding Pull Requests:")
        for pr in outstanding_prs:
            print(f"- PR #{pr['number']}: {pr['title']} ({pr['user']['login']})")
    else:
        print("No outstanding Pull Requests.")

def main() -> None:
    push_message_to_slack()
    #push_outstanding_prs_to_slack()

if __name__ == "__main__":
    main()
