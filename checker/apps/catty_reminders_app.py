import requests
import uuid

from bs4 import BeautifulSoup

# Global session object to maintain the session across function calls
_session = None

# Credentials
USERNAME = "tester"
PASSWORD = "foobar123"

def _login(base_url: str):
    """
    Logs in to the application and initializes the global session object.
    This function should be called before any other API requests.
    """
    global _session
    if _session:
        return

    print("--- Attempting to log in ---")
    session = requests.Session()
    login_url = f"{base_url}/login"
    credentials = {
        "username": USERNAME,
        "password": PASSWORD,
    }

    try:
        response = session.post(login_url, data=credentials, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Check if login was successful (e.g., by checking cookies or response)
        if session.cookies:
            _session = session
            print("Login successful. Session created.")
        else:
            print("Login failed: No session cookies received.")
            raise ConnectionError("Login failed, no cookies set.")

    except requests.exceptions.RequestException as e:
        print(f"Login failed: An error occurred during the request: {e}")
        raise ConnectionError(f"Login request failed: {e}") from e


def get_data(base_url: str) -> list[dict]:
    """
    Fetches the list of reminders from the API.
    """
    if not _session:
        _login(base_url)

    api_url = f"{base_url}/api/reminders"
    print(f"--- Getting data from {api_url} ---")
    try:
        response = _session.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Successfully fetched {len(data)} reminders.")
        return data
    except requests.exceptions.RequestException as e:
        print(f"Failed to get data: An error occurred: {e}")
        return []
    except ValueError: # Catches JSON decoding errors
        print(f"Failed to get data: Could not decode JSON from response.")
        return []


def generate_random_data(base_url: str) -> dict | None:
    """
    Creates a new reminder with a random name.
    """
    if not _session:
        _login(base_url)

    api_url = f"{base_url}/api/reminders"
    random_name = f"test-reminder-{uuid.uuid4()}"
    new_reminder_data = {"name": random_name}

    print(f"--- Creating a new reminder with name: {random_name} at {api_url} ---")
    try:
        response = _session.post(api_url, json=new_reminder_data, timeout=10)
        response.raise_for_status()
        
        # The API returns the created object, including its ID.
        created_data = response.json()
        print(f"Successfully created reminder: {created_data}")
        return created_data # Return the full object created by the API
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to create data: An error occurred: {e}")
        return None
    except ValueError:
        print(f"Failed to create data: Could not decode JSON from response.")
        return None

def is_alive(base_url: str) -> bool:
    """
    Checks if the application is alive by attempting to fetch data, which requires authentication.
    """
    try:
        # Reset session to ensure a fresh login attempt for the health check
        global _session
        _session = None
        
        get_data(base_url)
        return True
    except ConnectionError:
        return False

def extract_deploy_ref(app_url: str) -> str:
    body = requests.get(app_url).text
    soup = BeautifulSoup(body, "html.parser")
    meta_tag = soup.find("meta", attrs={"name": "deployref"})
    if meta_tag:
        return meta_tag.get("content")
    else:
        raise ValueError("Meta tag with 'deployref' name not found on page")