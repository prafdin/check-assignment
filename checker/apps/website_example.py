import requests
import uuid
from bs4 import BeautifulSoup

def get_data(app_url: str) -> dict:
    """
    Fetches comments from the application.
    """
    print(f"--- Getting comments from {app_url}/api/posts ---")
    try:
        response = requests.get(f"{app_url}/api/posts")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get data: {e}")
        return {}

def add_data(app_url: str, data: dict) -> bool:
    """
    Adds a comment to the application.
    """
    print(f"--- Adding comment to {app_url}/api/post ---")
    try:
        response = requests.post(f"{app_url}/api/post", json=data)
        response.raise_for_status()
        print(f"Successfully added data: {data}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to add data: {e}")
        return False

def generate_random_data(app_url: str) -> dict:
    """
    Generates a random comment and adds it to the application.
    """
    u_id = uuid.uuid4()
    new_comment = {
        "name": f"Stub name with id: {u_id}",
        "message": f"Stub message with id: {u_id}",
        "email": f"Stub email with id: {u_id}"
    }
    if add_data(app_url, new_comment):
        return new_comment
    return None

def is_alive(base_url: str) -> bool:
    """
    Checks if the application is alive by making a GET request to the base URL.
    """
    print(f"--- Running Test: GET request to {base_url} ---")
    try:
        response = requests.get(base_url, timeout=10)
        return str(response.status_code).startswith("2")
    except requests.exceptions.RequestException:
        return False

def extract_deploy_ref(app_url: str) -> str:
    body = requests.get(app_url).text
    soup = BeautifulSoup(body, "html.parser")
    meta_tag = soup.find("meta", attrs={"name": "deployref"})
    if meta_tag:
        return meta_tag.get("content")
    else:
        raise ValueError("Meta tag with 'deployref' name not found on page")
