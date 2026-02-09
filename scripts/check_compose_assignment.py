import argparse
import importlib
import re
import sys
from functools import partial

from checker.checks import CONFIG, check_release_updates_data, push_and_check_workflow, check_tests_passed, \
    check_docker_image_exists, check_deploy_ref_matches_commit
from checker.utils import CICommit


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
    parser.add_argument("--branch_name", type=str, required=True,
                        help="Branch name for CI commit")

    args = parser.parse_args()

    image_name = f"{args.login}/{args.app}"

    CONFIG["sa_login"] = args.sa_login
    CONFIG["sa_mail"] = args.sa_mail
    CONFIG["timeout"] = args.timeout
    CONFIG["poll_interval"] = args.poll_interval

    print(f"Checking assignment for repository: {args.repo_url}")

    try:
        snake_case_app_name = args.app.replace('-', '_')
        app_api = importlib.import_module(f"checker.apps.{snake_case_app_name}")
    except ImportError:
        print(f"Could not import app API for {args.app}")
        sys.exit(1)

    app_url = f"http://app.{args.id}.{args.proxy}"
    ci_commit = CICommit(args.repo_url, args.branch_name, CONFIG)
    match = re.search(r'git@github.com:(.*)\.git', args.repo_url)
    if not match:
        print("Could not extract repository name from repo_url.")
        sys.exit(1)
    repo_name = match.group(1)

    tests = []
    tests.append(partial(push_and_check_workflow, ci_commit, repo_name, str(ci_commit.commit_sha), args.github_token))
    tests.append(partial(check_tests_passed, repo_name, str(ci_commit.commit_sha), args.github_token))
    tests.append(partial(check_docker_image_exists, image_name, str(ci_commit.commit_sha), args.github_token))
    tests.append(partial(check_release_updates_data, app_api, app_url, repo_name, args.github_token, str(ci_commit.commit_sha)))
    tests.append(partial(check_deploy_ref_matches_commit, app_api, app_url, str(ci_commit.commit_sha)))

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
