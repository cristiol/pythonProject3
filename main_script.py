import zipfile

import requests
import yaml
import io

BASE_URL = 'http://127.0.0.1:8088'
EXPLORE = f'{BASE_URL}/api/v1/assets/export/'
LOCAL_INSTANCES_DIR = 'local_instances.yaml'  # Directory to store local instances


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


def make_request(url, headers, method,payload=None):
    return requests.request(method, url, data=payload, headers=headers)

response = make_request(EXPLORE, HEADERS, "GET")


def process_zip_content(zip_content):
    for filename in zip_content.namelist():
        if filename.endswith('.yaml'):
            with zip_content.open(filename, 'r') as yaml_file:
                yaml_data = yaml.safe_load(yaml_file)
                print(f"Filename: {filename}")
                print(yaml.dump(yaml_data, default_flow_style=False))
                print("-" * 80)

def main():
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_content:
        process_zip_content(zip_content)

if __name__ == "__main__":
    main()







