import argparse
import os
import re
import sys
import tempfile
from time import sleep

import pygit2
import requests

CONFIG = {
    "check_event_timeout": 30,
    "wait_automatic_update": 5,
    "sa_name": "Name Example",
    "sa_email": "e@mail.com"
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

    sleep(CONFIG["wait_automatic_update"])

    date_after = extract_date(requests.get(url).text)

    return date_before == date_after

def check_event_update_site(app_url: str, repo_url: str, repo_branch: str) -> bool:
    date_before = extract_date(requests.get(app_url).text)

    push_ci_commit(repo_url, repo_branch)

    sleep(CONFIG["check_event_timeout"])

    date_after = extract_date(requests.get(app_url).text)

    return date_before != date_after

def push_ci_commit(repo_ssh_url, branch):
    assert repo_ssh_url.startswith("git") is True
    callbacks = pygit2.RemoteCallbacks(
        credentials=pygit2.KeypairFromAgent("git")
    )
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo = pygit2.clone_repository(repo_ssh_url, tmpdirname, callbacks=callbacks)
        branch_ref = f"refs/heads/{branch}"
        repo.checkout(branch_ref)
        author = pygit2.Signature(CONFIG["sa_name"], CONFIG["sa_email"])
        committer = pygit2.Signature(CONFIG["sa_name"], CONFIG["sa_email"])
        tree = repo.index.write_tree()
        parent = repo.head.target
        commit_message = "ci"
        repo.create_commit(
            branch_ref,
            author,
            committer,
            commit_message,
            tree,
            [parent]
        )
        remote = repo.remotes["origin"]
        remote.push([branch_ref], callbacks=callbacks)

def extract_date(body) -> str:
    match = re.search(r"<deploy-date>(.*?)</deploy-date>", body, re.DOTALL)
    if not match:
        raise ValueError("Tag <deploy-date> not found in body")
    return match.group(1).strip()

def main():
    parser = argparse.ArgumentParser(description="Check webhooks DevOps assignment.")
    parser.add_argument("--repo_url", type=str, required=True,
                        help="URL of the student's repository.")
    parser.add_argument("--id", type=str, required=True,
                        help="The ID for the URL.")
    parser.add_argument("--proxy", type=str, required=True,
                        help="The PROXY for the URL.")

    args = parser.parse_args()

    print(f"Checking assignment for repository: {args.repo_url}")

    tests = []

    app_url = f"http://app.{args.id}.{args.proxy}"
    tests.append(check_app_is_alive(app_url))
    
    if all(tests):
        print("\nAll checks PASSED.")
        sys.exit(0)
    else:
        print(f"\n{tests.count(False)} out of {len(tests)} checks FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
