import secrets
import hashlib
import base64
import requests
from collections import defaultdict
from datetime import datetime, timedelta


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

    return {k["date"]: k["fat"] for k in response.json()["fat"] }

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

    return {k["dateTime"]: k["value"] for k in response.json()["foods-log-water"] }


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

    return {k["endTime"].split("T")[0]: k["minutesAsleep"] for k in response.json()["sleep"]}

def get_steps(access_token, startdate, enddate):
    resource_url = f"{fitbit_base_url}/activities/steps/date/{startdate}/{enddate}.json"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(resource_url, headers=headers)
    response.raise_for_status()

    return {k["dateTime"]: k["value"] for k in response.json()["activities-steps"] }


def get_activeness(access_token, startdate, enddate):
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    activeness = {"minutesLightlyActive": 0, "minutesFairlyActive": 0, "minutesVeryActive": 0}

    for active_type in activeness:
        resource_url = f"{fitbit_base_url}/activities/{active_type}/date/{startdate}/{enddate}.json"
        response = requests.get(resource_url, headers=headers)
        response.raise_for_status()
        activeness[active_type] = response.json()


    sum_entry = defaultdict(int)
    for active_type, lst in activeness.items():
        for entry in activeness[active_type]["activities-" + active_type]:
            sum_entry[entry["dateTime"]] = int(entry["value"]) + sum_entry[entry["dateTime"]]

    return sum_entry

def generate_date_range(start_date_str, end_date_str):
    # Convert the date strings to datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Check if start_date is after end_date
    if start_date > end_date:
        raise ValueError("Start date should be before or the same as the end date.")

    # Generate the list of dates
    date_list = []
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)  # Move to the next day

    return date_list

def get_completed_challenge_entries_and_streaks(activity_data, verification_value, start_date, end_date):
    completed_num = 0
    streak_num = 0
    for _date in generate_date_range(start_date, end_date):
        if activity_data.get(_date, 0) >= verification_value:
            completed_num += 1
            streak_num += 1
        else:
            streak_num = 0

    return completed_num, streak_num


if __name__ == "__main__":

    # print(generate_date_range("2023-09-25", "2023-10-19"))
    # exit()

    # access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1I4WkwiLCJzdWIiOiJCUVZIWDMiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNjk3NzgzODkwLCJpYXQiOjE2OTc3NTUwOTB9.SbTF7TzHehWG4WsyqW6wViOg4zFPjkGL-Z7PCgwm9-o"
    # result = get_sleep(access_token, '2023-10-01', '2023-10-19')
    # # result = get_water_consumption(access_token, '2023-10-01', '2023-10-19')
    # print(result)

    # # result = get_steps(access_token, '2023-10-01', '2023-10-19')
    # # print(result)

    # # result = get_water_consumption(access_token, '2023-10-01', '2023-10-19')
    # # print(result)
    pass


