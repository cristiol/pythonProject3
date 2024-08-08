import hashlib
import os
import zipfile

import requests
import yaml
import io


BASE_URL = 'http://127.0.0.1:8088'
EXPLORE = f'{BASE_URL}/api/v1/assets/export/'
LOCAL_INSTANCES_FILE = 'local_instances.yaml'  # File to save all instances

def get_token():
    url = f"{BASE_URL}/api/v1/security/login"

    payload = {
        "password": "admin",
        "provider": "db",
        "refresh": True,
        "username": "admin"
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "insomnia/9.3.3"
    }

    return requests.request("POST", url, json=payload, headers=headers).json()['access_token']

HEADERS = {
    "cookie": "session=eyJfZnJlc2giOmZhbHNlLCJsb2NhbGUiOiJlbiJ9.ZrMDTw.opKpf0-ZBQmmxoMmd318MFl7_0A",
    "Content-Type": "application/zip",
    "User-Agent": "insomnia/9.3.3",
    "Authorization": f"Bearer {get_token()}"
    }


def make_request(url, headers, method, payload=None):
    return requests.request(method, url, data=payload, headers=headers)

def process_zip_content(zip_content):
  """
  Processes the downloaded ZIP content and saves all YAML data to a single file.

  Args:
      zip_content (zipfile.ZipFile): The ZIP file object containing the downloaded instances.
  """
  all_data = []
  for filename in zip_content.namelist():
      if filename.endswith('.yaml'):
          with zip_content.open(filename, 'r') as yaml_file:
              yaml_data = yaml.safe_load(yaml_file)
              all_data.append(yaml_data)

  with open(LOCAL_INSTANCES_FILE, 'w') as f:
      yaml.dump(all_data, f, default_flow_style=False)
      print(f"Saved all instances to: {LOCAL_INSTANCES_FILE}")

def main():
    response = make_request(EXPLORE, HEADERS, "GET")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_content:
        process_zip_content(zip_content)


def get_local_instances():
    """
    Retrieves instance data from locally stored YAML files.

    Returns:
        dict: A dictionary containing instance data keyed by filenames.
    """
    local_instances = {}
    if not os.path.exists(LOCAL_INSTANCES_FILE):
        os.makedirs(LOCAL_INSTANCES_FILE)  # Create the directory if it doesn't exist

    for filename in os.listdir(LOCAL_INSTANCES_FILE):
        if filename.endswith('.yaml'):
            local_filename = os.path.join(LOCAL_INSTANCES_FILE, filename)
            with open(local_filename, 'r') as f:
                local_instances[filename] = yaml.safe_load(f)
    return local_instances


def synchronize_instances(remote_instances, local_instances):
    """
    Synchronizes local and remote instances based on changes.

    Args:
        remote_instances (dict): Dictionary containing remote instance data.
        local_instances (dict): Dictionary containing local instance data.
    """
    for filename, remote_data in remote_instances.items():
        if filename in local_instances:
            # Compare local and remote data using a unique identifier (e.g., hash)
            local_filename = os.path.join(LOCAL_INSTANCES_FILE, filename)
            with open(local_filename, 'rb') as f:
                local_hash = hashlib.sha256(f.read()).hexdigest()

            remote_hash = hashlib.sha256(yaml.dump(remote_data).encode()).hexdigest()

            if local_hash != remote_hash:
                # Update local file if content has changed
                with open(local_filename, 'w') as f:
                    yaml.dump(remote_data, f, default_flow_style=False)
