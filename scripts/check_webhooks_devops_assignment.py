import argparse
import os
import re
import sys
import tempfile
from functools import partial
from time import sleep

import pygit2
import requests
from bs4 import BeautifulSoup

CONFIG = {
    "check_event_timeout": 30,
    "wait_automatic_update": 5,
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

def check_event_update_site(app_url: str, repo_url: str, repo_branch: str) -> bool:
    date_before = extract_date(requests.get(app_url).text)

    push_ci_commit(repo_url, repo_branch)

    sleep_time = CONFIG["check_event_timeout"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

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
        author = pygit2.Signature(CONFIG["sa_login"], CONFIG["sa_mail"])
        committer = pygit2.Signature(CONFIG["sa_login"], CONFIG["sa_mail"])
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
    soup = BeautifulSoup(body, "html.parser")
    meta_tag = soup.find("meta", attrs={"name": "deploydate"})
    if meta_tag:
        return meta_tag.get("content")
    else:
        raise ValueError("Meta tag with 'deploydate' name not found on page")

def main():
    parser = argparse.ArgumentParser(description="Check webhooks DevOps assignment.")
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

    args = parser.parse_args()

    CONFIG["sa_login"] = args.sa_login
    CONFIG["sa_mail"] = args.sa_mail

    print(f"Checking assignment for repository: {args.repo_url}")

    tests = []

    app_url = f"http://app.{args.id}.{args.proxy}"
    tests.append(partial(check_app_is_alive, app_url))
    tests.append(partial(check_no_automatic_site_update, app_url))
    print(args)
    tests.append(partial(check_event_update_site, app_url, args.repo_url, 'main'))


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
