from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests


def get_identity(user):
    base_url = "https://kinideas-profile.calmgrass-743c6f7f.francecentral.azurecontainerapps.io/firebaseUser"
    url = base_url + "/" + user
    headers = {"Content-type": "application/json", "Accept": "application/json"}

    retry_strategy = Retry(
        total=10,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    try:
        response = http.get(url, headers=headers)
    except Exception as e:
        return str(e)
    return response.json()
