import argparse
import sys
import re
import json
from functools import partial

from checker.checks import check_app_is_alive, check_event_update_site, check_workflow_run_success, check_required_workflow_files, check_release_updates_site, check_deploy_ref_matches_commit, check_docker_image_exists, CONFIG
from checker.utils import CICommit

def push_and_check_workflow(ci_commit: CICommit, repo_name: str, commit_sha: str, github_token: str) -> bool:
    """
    Pushes a commit and then checks for the success of the triggered workflow.
    """
    print("--- Pushing commit to trigger workflow ---")
    ci_commit.push()
    print("--- Commit pushed, now checking for workflow run ---")
    return check_workflow_run_success(repo_name, commit_sha, github_token)

def main():
    parser = argparse.ArgumentParser(description="Check a new assignment.")
    parser.add_argument("--repo_url", type=str, required=True,
                        help="URL of the student's repository.")
    parser.add_argument("--id", type=str, required=True,
                        help="The ID for the URL.")
    parser.add_argument("--proxy", type=str, required=True,
                        help="The PROXY for the URL.")
    parser.add_argument("--login", type=str, required=True,
                        help="The GitHub user/organization name for the Docker image.")
    parser.add_argument("--app", type=str, required=True,
                        help="The application name for the Docker image.")
    parser.add_argument("--sa_login", type=str, required=True,
                        help="GitHub service account login")
    parser.add_argument("--sa_mail", type=str, required=True,
                        help="GitHub service account login")
    parser.add_argument("--github_token", type=str, required=True,
                        help="GitHub token for API requests.")
    parser.add_argument("--timeout", type=int, required=True,
                        help="Timeout for checks")
    parser.add_argument("--poll_interval", type=int, required=True,
                        help="Poll interval for checks")

    args = parser.parse_args()

    image_name = f"{args.login}/{args.app}"

    CONFIG["sa_login"] = args.sa_login
    CONFIG["sa_mail"] = args.sa_mail
    CONFIG["timeout"] = args.timeout
    CONFIG["poll_interval"] = args.poll_interval

    print(f"Checking assignment for repository: {args.repo_url}")

    tests = []

    app_url = f"http://app.{args.id}.{args.proxy}"

    tests.append(partial(check_app_is_alive, app_url))
    
    ci_commit = CICommit(args.repo_url, 'docker_devops_assignment', CONFIG)

    # Extract owner/repo from the repo_url
    match = re.search(r'git@github.com:(.*)\.git', args.repo_url)
    if not match:
        print("Could not extract repository name from repo_url.")
        sys.exit(1)
    repo_name = match.group(1)

    tests.append(partial(push_and_check_workflow, ci_commit, repo_name, str(ci_commit.commit_sha), args.github_token))
    tests.append(partial(check_docker_image_exists, image_name, str(ci_commit.commit_sha), args.github_token))

    required_workflow_files = [".github/workflows/ci.yaml", ".github/workflows/deploy.yaml"]
    tests.append(partial(check_required_workflow_files, args.repo_url, 'docker_devops_assignment', required_workflow_files))

    tests.append(partial(check_release_updates_site, app_url, repo_name, args.github_token, str(ci_commit.commit_sha)))
    tests.append(partial(check_deploy_ref_matches_commit, app_url, str(ci_commit.commit_sha)))

    failed_tests = 0
    for test in tests:
        try:
            print(f"[{test.func.__name__}] Start test")
            if test():
                print(f"[{test.func.__name__}] Test successfully passed")
            else:
                print(f"[{test.func.__name__}] Test failed")
                failed_tests += 1
        except Exception as e:
            print(f"[{test.func.__name__}] Test failed with exception:\n{str(e)}")
            failed_tests += 1

    if failed_tests != 0:
        print(f"\n{failed_tests} out of {len(tests)} checks FAILED.")
        sys.exit(1)
    else:
        print("\nAll test PASSED.")
        sys.exit(0)

if __name__ == "__main__":
    main()
