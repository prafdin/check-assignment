import requests
import re
import json

def is_alive(base_url: str) -> bool:
    """
    Checks if the application is alive by making a GET request to the base URL.
    """
    print(f"--- Running Test: GET request to {base_url} ---")
    try:
        response = requests.get(f"{base_url}/swagger/v1/swagger.json", timeout=10)
        return str(response.status_code).startswith("2")
    except requests.exceptions.RequestException:
        return False

def extract_deploy_ref(app_url: str) -> str | None:
    """
    Extracts the deploy reference from the Swagger JSON's info.description field.
    """
    swagger_url = f"{app_url}/swagger/v1/swagger.json"
    print(f"--- Attempting to extract deploy ref from Swagger at {swagger_url} ---")
    try:
        response = requests.get(swagger_url, timeout=10)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        swagger_json = response.json()

        description = swagger_json.get('info', {}).get('description')
        if description:
            match = re.search(r"Deploy Ref: ([^)]+)", description)
            if match:
                deploy_ref = match.group(1).strip()
                print(f"Successfully extracted deploy ref: {deploy_ref}")
                return deploy_ref
            else:
                print("Deploy Ref pattern not found in Swagger description.")
        else:
            print("Swagger description not found.")

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch Swagger JSON: {e}")
    except json.JSONDecodeError:
        print("Failed to decode Swagger JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None

