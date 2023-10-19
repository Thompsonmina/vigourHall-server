import secrets
import hashlib
import base64
import requests


fitbit_base_url = "https://api.fitbit.com/1/user/-/";

def generate_code_verifier() -> str:
    token = secrets.token_urlsafe(96)  # Generates a random URL-safe text string
    while len(token) < 43:
        token += secrets.token_urlsafe(len(token))
    
    return token[:128]  # Truncate to 128 characters if longer

def generate_code_challenge(code_verifier: str) -> str:
    # Create a SHA-256 hash of the code_verifier
    sha256_hash = hashlib.sha256(code_verifier.encode())
    # Get the digest as bytes
    digest_bytes = sha256_hash.digest()
    # Base64 encode the bytes
    challenge = base64.urlsafe_b64encode(digest_bytes).decode().replace("=", "")
    return challenge

def generate_state() -> str:
    return secrets.token_urlsafe(16)  # Generates a 16-byte long URL-safe text string


# def is_valid_bodyfat_completion(value, tier, tier_completion_value):
#     if tier 

def get_body_fat(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/body/log/fat/date/{startdate}/{enddate}.json/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)

    # Ensure the response is successful before decoding JSON
    response.raise_for_status()

    return response.json()

def get_water_consumption(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/foods/log/water/date/{startdate}/{enddate}.json/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)

    # Ensure the response is successful before decoding JSON
    response.raise_for_status()

    return response.json()


def get_sleep(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/sleep/date/{startdate}/{enddate}.json/"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)

    # Ensure the response is successful before decoding JSON
    response.raise_for_status()

    return response.json()

def get_steps(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/activities/steps/date/{startdate}/{enddate}.json"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)
    response.raise_for_status()

    return response.json()


def activeness(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/activities/minutesSedentary/date/{startdate}/{enddate}.json"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)
    response.raise_for_status()

    return response.json()


access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1I4WkwiLCJzdWIiOiJCUVZIWDMiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNjk3NzM3NDAyLCJpYXQiOjE2OTc3MDg2MDJ9.xzrAN7cn0rpDrFnZlpxVN7y5vtR_2-vVSmsM-URYOQU"
result = get_body_fat(access_token, '2023-10-01', '2023-10-19')
result = get_water_consumption(access_token, '2023-10-01', '2023-10-19')
print(result)

result = get_steps(access_token, '2023-10-01', '2023-10-19')
print(result)

