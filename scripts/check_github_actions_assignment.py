import argparse
import sys
import re
from functools import partial

# Import existing checks from the checker.checks module
from checker.checks import check_app_is_alive, check_no_automatic_site_update, check_event_update_site, check_workflow_run_success, CONFIG
from checker.utils import CICommit

def main():
    parser = argparse.ArgumentParser(description="Check a new assignment.")
    parser.add_argument("--repo_url", type=str, required=True,
                        help="URL of the student's repository.")
    parser.add_argument("--id", type=str, required=True,
                        help="The ID for the URL.")
    parser.add_argument("--proxy", type=str, required=True,
                        help="The PROXY for the URL.")
    parser.add_argument("--sa_login", type=str, required=True,
                        help="GitHub service account login")
    parser.add_argument("--sa_mail", type=str, required=True,
                        help="GitHub service account login")
    parser.add_argument("--github_token", type=str, required=True,
                        help="GitHub token for API requests.")

    args = parser.parse_args()

    CONFIG["sa_login"] = args.sa_login
    CONFIG["sa_mail"] = args.sa_mail

    print(f"Checking assignment for repository: {args.repo_url}")

    tests = []

    app_url = f"http://app.{args.id}.{args.proxy}"

    tests.append(partial(check_app_is_alive, app_url))
    tests.append(partial(check_no_automatic_site_update, app_url))
    
    ci_commit = CICommit(args.repo_url, 'github_actions_assignment', CONFIG)
    tests.append(partial(check_event_update_site, app_url, ci_commit))

    # Extract owner/repo from the repo_url
    match = re.search(r'git@github.com:(.*)\.git', args.repo_url)
    if not match:
        print("Could not extract repository name from repo_url.")
        sys.exit(1)
    repo_name = match.group(1)

    tests.append(partial(check_workflow_run_success, repo_name, str(ci_commit.commit_sha), args.github_token))

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
