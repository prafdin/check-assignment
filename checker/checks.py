from time import sleep
import requests
from .utils import extract_date, push_ci_commit

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

    push_ci_commit(repo_url, repo_branch, CONFIG)

    sleep_time = CONFIG["check_event_timeout"]
    print(f"Sleep {sleep_time} seconds")
    sleep(sleep_time)

    date_after = extract_date(requests.get(app_url).text)

    return date_before != date_after
