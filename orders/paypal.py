import requests
import base64
from django.conf import settings


def get_access_token():

    url = f"{settings.PAYPAL_BASE}/v1/oauth2/token"

    auth = base64.b64encode(
        f"{settings.PAYPAL_CLIENT_ID}:{settings.PAYPAL_SECRET}".encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {auth}"
    }

    data = {"grant_type": "client_credentials"}

    res = requests.post(url, headers=headers, data=data)

    return res.json()["access_token"]