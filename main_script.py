
import zipfile
from deepdiff import DeepDiff
import requests
import yaml
import io


BASE_URL = 'http://127.0.0.1:8088'
EXPLORE = f'{BASE_URL}/api/v1/assets/export/'
LOCAL_INSTANCES_FILE = 'local_instances.yaml'
LOCAL_INSTANCES_FILE_B = 'local_instancesB.yaml'


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

  all_data = []
  for filename in zip_content.namelist():
      if filename.endswith('.yaml'):
          with zip_content.open(filename, 'r') as yaml_file:
              yaml_data = yaml.safe_load(yaml_file)
              all_data.append(yaml_data)

  with open(LOCAL_INSTANCES_FILE, 'w') as f:
      yaml.dump(all_data[-1], f, default_flow_style=False)
      print(f"Saved all instances to: {LOCAL_INSTANCES_FILE}")


def main():
    response = make_request(EXPLORE, HEADERS, "GET")
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_content:
        process_zip_content(zip_content)


def synchronize_yaml_files(file_a, file_b):

    with open(file_a, 'r') as f:
        data_a = yaml.safe_load(f)

    with open(file_b, 'r') as f:
        data_b = yaml.safe_load(f)

    diff = DeepDiff(data_a, data_b, ignore_order=True)

    if diff:
        data_b = data_a.copy()

        with open(file_b, 'w') as f:
            yaml.dump(data_b, f)
        print("File B updated")
    else:
        print("no updates")

synchronize_yaml_files(LOCAL_INSTANCES_FILE,LOCAL_INSTANCES_FILE_B)