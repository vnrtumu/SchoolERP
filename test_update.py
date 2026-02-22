import urllib.request
import json
import urllib.error
import sys

# 1. Login
try:
    login_req = urllib.request.Request(
        "http://localhost:8000/api/v1/super-admin/login",
        data=b'{"username": "superadmin1", "password": "testpassword123"}',
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(login_req) as response:
        token_data = json.loads(response.read().decode())
        token = token_data['access_token']
        print(f"Token acquired. Length: {len(token)}")
except Exception as e:
    print(f"Login failed: {e}")
    sys.exit(1)

# 2. Update Profile with data similar to the UI screenshot
payload = {
    "full_name": "Venkata Narayana reddy",
    "phone": "9182387725",
    "position": "Super Admin",
    "facebook_url": "https://github.com/vnrtumu",
    "twitter_url": "https://github.com/vnrtumu",
    "github_url": "https://github.com/vnrtumu",
    "dribbble_url": "https://github.com/vnrtumu",
    "location": "",
    "state": "",
    "pin": "",
    "zip": "",
    "tax_no": ""
}
put_req = urllib.request.Request(
    "http://localhost:8000/api/v1/super-admin/me",
    data=json.dumps(payload).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "accept": "application/json"
    },
    method="PUT"
)
try:
    with urllib.request.urlopen(put_req) as response:
        print(f"Status: {response.status}")
        print(f"Response: {response.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Error Body: {e.read().decode()}")
except Exception as e:
    print(f"Unexpected error: {e}")
