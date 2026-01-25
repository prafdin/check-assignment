import time
from time import sleep
import requests
from github import Github
from .utils import extract_deploy_ref, CICommit
import os
import shutil
import pygit2 # New import

CONFIG = {
    "check_event_timeout": 60,
    "wait_automatic_update": 5,
    "workflow_timeout": 120,  # 2 minutes
    "workflow_poll_interval": 10, # default poll interval
    "release_timeout": 120, # 2 minutes
    "release_poll_interval": 15, # 15 seconds
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
    ref_before = extract_deploy_ref(requests.get(url).text)

    sleep_time = CONFIG["wait_automatic_update"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

    ref_after = extract_deploy_ref(requests.get(url).text)

    return ref_before == ref_after

def check_event_update_site(app_url: str, commit: CICommit) -> bool:
    ref_before = extract_deploy_ref(requests.get(app_url).text)

    commit.push()

    sleep_time = CONFIG["check_event_timeout"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

    ref_after = extract_deploy_ref(requests.get(app_url).text)

    return ref_before != ref_after

def _wait_for_workflow_run(repo, find_run_func) -> bool:
    """
    Waits for a specific workflow run to complete.

    :param repo: The repository object from PyGithub.
    :param find_run_func: A function that returns the specific workflow run to wait for, or None if not found.
    :return: True if the workflow run is found and completes successfully, False otherwise.
    """
    try:
        # Poll to find the run
        workflow_run = None
        for _ in range(5):
            run = find_run_func()
            if run:
                workflow_run = run
                break
            sleep(CONFIG["workflow_poll_interval"])
        
        if not workflow_run:
            print("Test FAILED: No workflow run found.")
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
        print(f"Test FAILED: An error occurred while waiting for the workflow run: {e}")
        return False

def check_workflow_run_success(repo_name: str, commit_sha: str, github_token: str) -> bool:
    print(f"--- Running Test: Check workflow run for commit {commit_sha} in repo {repo_name} ---")
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    
    def find_run_by_commit():
        runs = repo.get_workflow_runs(head_sha=commit_sha)
        return runs[0] if runs.totalCount > 0 else None

    return _wait_for_workflow_run(repo, find_run_by_commit)


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
        callbacks = pygit2.RemoteCallbacks(
            credentials=pygit2.KeypairFromAgent("git")
        )
        repo = pygit2.clone_repository(repo_url, temp_dir, checkout_branch=branch_name, callbacks=callbacks)

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


def check_release_updates_site(app_url: str, repo_name: str, github_token: str, commit_sha: str) -> bool:
    print(f"--- Running Test: Check if a new release triggers a site update for repo {repo_name} ---")
    try:
        # 1. Get the deploy ref before the release
        print(f"Getting initial deploy ref from {app_url}...")
        ref_before = extract_deploy_ref(requests.get(app_url).text)
        print(f"Initial deploy ref: {ref_before}")

        # 2. Create a git tag and release
        g = Github(github_token)
        repo = g.get_repo(repo_name)

        tag_name = time.strftime("ci-%Y%m%d-%H%M%S")
        print(f"Using commit SHA for release: {commit_sha}")
        print(f"Creating git ref 'refs/tags/{tag_name}'...")
        repo.create_git_ref(ref=f'refs/tags/{tag_name}', sha=commit_sha)

        print(f"Creating GitHub release '{tag_name}'...")
        repo.create_git_release(tag=tag_name, name=f"Release {tag_name}", message="Automated release for testing deployment.")
        print("GitHub release created successfully.")

        # 3. Wait for the release-triggered workflow to complete
        print("--- Checking for CD workflow triggered by release ---")
        
        def find_run_by_release_tag():
            runs = repo.get_workflow_runs(event='release')
            for run in runs:
                # For release events, the branch is the tag name
                if run.head_branch == tag_name:
                    return run
            return None

        if not _wait_for_workflow_run(repo, find_run_by_release_tag):
            print("Test FAILED: The release did not trigger a successful CD workflow.")
            return False
        
        print("CD workflow completed successfully. Now checking for site update...")

        # 4. Wait for deployment by polling
        timeout = CONFIG["release_timeout"]
        poll_interval = CONFIG["release_poll_interval"]
        start_time = time.time()
        
        print(f"Waiting for up to {timeout} seconds for deployment...")
        while time.time() - start_time < timeout:
            print(f"Checking for update... (elapsed: {int(time.time() - start_time)}s)")
            ref_after = extract_deploy_ref(requests.get(app_url).text)
            if ref_before != ref_after:
                print(f"Test PASSED: Deploy ref changed from '{ref_before}' to '{ref_after}'.")
                return True
            sleep(poll_interval)

        # 5. If loop finishes, timeout was reached
        print(f"Test FAILED: Deploy ref '{ref_before}' did not change after {timeout} seconds.")
        return False

    except Exception as e:
        print(f"Test FAILED: An error occurred: {e}")
        return False


def check_deploy_ref_matches_commit(app_url: str, expected_commit_sha: str) -> bool:
    print(f"--- Running Test: Check if deploy ref on page matches commit SHA {expected_commit_sha} ---")

    deployed_ref = extract_deploy_ref(requests.get(app_url).text)
    if deployed_ref == expected_commit_sha:
        print(f"Test PASSED: Deployed ref '{deployed_ref}' matches expected SHA.")
        return True
    else:
        print(f"Test FAILED: Deploy ref did not match expected SHA '{expected_commit_sha}'")
        return False

