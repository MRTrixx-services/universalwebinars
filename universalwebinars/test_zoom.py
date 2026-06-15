import requests
import base64

account_id = "ygAbpj7xT_-djmkaSpbrHQ"
client_id = "5PuUizhCRZGSFAyrhl77JQ"
client_secret = "OH4dwnaYjBHhxppl98bmhneVVBPiZyep"

url = "https://zoom.us/oauth/token"

auth = f"{client_id}:{client_secret}"
auth_encoded = base64.b64encode(auth.encode()).decode()

headers = {
    "Authorization": f"Basic {auth_encoded}"
}

data = {
    "grant_type": "account_credentials",
    "account_id": account_id
}

response = requests.post(url, headers=headers, data=data)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)