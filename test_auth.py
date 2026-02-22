import subprocess
import json

# Login
login_cmd = [
    "curl", "-s", "-X", "POST", "http://localhost:8000/api/v1/super-admin/login",
    "-H", "Content-Type: application/json",
    "-d", '{"username": "superadmin1", "password": "testpassword123"}'
]
login_res = subprocess.run(login_cmd, capture_output=True, text=True)
try:
    token = json.loads(login_res.stdout).get("access_token")
    if not token:
        print(f"Failed to get token. Response: {login_res.stdout}")
        exit(1)
    
    print(f"Got token! {token[:10]}...")
    
    # Put
    put_cmd = [
        "curl", "-s", "-X", "PUT", "http://localhost:8000/api/v1/super-admin/me",
        "-H", "accept: application/json",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", '{"full_name": "Test User From Python", "phone": "1231231234"}'
    ]
    put_res = subprocess.run(put_cmd, capture_output=True, text=True)
    print(f"Update response: {put_res.stdout}")
    
except Exception as e:
    print(f"Error: {e}")
