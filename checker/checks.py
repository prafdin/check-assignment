import time
from time import sleep
import requests
from github import Github
from .utils import extract_date, CICommit
import os
import shutil
import pygit2 # New import

CONFIG = {
    "check_event_timeout": 60,
    "wait_automatic_update": 5,
    "workflow_timeout": 120,  # 2 minutes
    "workflow_poll_interval": 10, # default poll interval
    "sa_login": "Name Example",
    "sa_mail": "e@mail.com"
}


def check_app_is_alive(url: str) -> bool:
    print(f"--- Running Test: GET request to {url} ---")
    try:
        response = requests.get(url, timeout=10)
        if str(response.status_code).startswith("2"):
            print("Test PASSED: Received status code 2xx.")
            return True
        else:
            print(f"Test FAILED: Received status code {response.status_code}.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Test FAILED: An error occurred during the GET request: {e}")
        return False

def check_no_automatic_site_update(url) -> bool:
    date_before = extract_date(requests.get(url).text)

    sleep_time = CONFIG["wait_automatic_update"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

    date_after = extract_date(requests.get(url).text)

    return date_before == date_after

def check_event_update_site(app_url: str, commit: CICommit) -> bool:
    date_before = extract_date(requests.get(app_url).text)

    commit.push()

    sleep_time = CONFIG["check_event_timeout"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

    date_after = extract_date(requests.get(app_url).text)

    return date_before != date_after

def check_workflow_run_success(repo_name: str, commit_sha: str, github_token: str) -> bool:
    print(f"--- Running Test: Check workflow run for commit {commit_sha} in repo {repo_name} ---")
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        
        # It might take a moment for the workflow run to be created after the push.
        # So we poll for a short time to find the run.
        workflow_run = None
        for _ in range(5):
            runs = repo.get_workflow_runs(head_sha=commit_sha)
            if runs.totalCount > 0:
                workflow_run = runs[0]
                break
            sleep(CONFIG["workflow_poll_interval"])
        
        if not workflow_run:
            print("Test FAILED: No workflow run found for the commit.")
            return False

        print(f"Found workflow run: {workflow_run.html_url}")

        # Wait for the workflow to complete
        timeout = CONFIG["workflow_timeout"]
        start_time = time.time()
        while workflow_run.status in ["queued", "in_progress"]:
            if time.time() - start_time > timeout:
                print("Test FAILED: Workflow run timed out.")
                return False
            print(f"Workflow status is '{workflow_run.status}'. Waiting...")
            sleep(CONFIG["workflow_poll_interval"])
            workflow_run = repo.get_workflow_run(workflow_run.id)

        print(f"Workflow finished with status '{workflow_run.status}' and conclusion '{workflow_run.conclusion}'.")
        if workflow_run.conclusion == "success":
            print("Test PASSED: Workflow run completed successfully.")
            return True
        else:
            print(f"Test FAILED: Workflow run conclusion is '{workflow_run.conclusion}'.")
            return False

    except Exception as e:
        print(f"Test FAILED: An error occurred while checking the workflow run: {e}")
        return False


def check_required_workflow_files(repo_url: str, branch_name: str, files: list[str]) -> bool:
    print(f"--- Running Test: Check for required workflow files in {repo_url} on branch {branch_name} ---")
    
    temp_dir = None
    try:
        # Create a temporary directory for cloning
        temp_dir = os.path.join('/tmp', f"repo_clone_{os.urandom(8).hex()}")
        os.makedirs(temp_dir)

        # Clone the repository
        # For SSH authentication, pygit2 will automatically use the SSH agent if configured.
        print(f"Cloning {repo_url} into {temp_dir}")
        repo = pygit2.clone_repository(repo_url, temp_dir, checkout_branch=branch_name)

        all_files_exist = True
        for file_path in files:
            full_path = os.path.join(temp_dir, file_path)
            if not os.path.exists(full_path):
                print(f"Test FAILED: Required file '{file_path}' does not exist.")
                all_files_exist = False
                break
            print(f"Found required file: '{file_path}'.")

        if all_files_exist:
            print("Test PASSED: All required workflow files exist.")
            return True
        else:
            return False

    except pygit2.GitError as e:
        print(f"Test FAILED: Git error during cloning or checkout: {e}")
        return False
    except Exception as e:
        print(f"Test FAILED: An unexpected error occurred: {e}")
        return False
    finally:
        if temp_dir and os.path.exists(temp_dir):
            print(f"Cleaning up temporary directory: {temp_dir}")
            shutil.rmtree(temp_dir)
