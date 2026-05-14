import requests
import os

url = "http://litellm.100.80.0.55.nip.io/v1/models"
key = os.environ.get("LITELLM_MASTER_KEY")
headers = {"Authorization": f"Bearer {key}"}

response = requests.get(url, headers=headers)
print(response.json())
