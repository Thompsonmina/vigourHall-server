import os,datetime

from fitbit import (generate_code_verifier, generate_code_challenge, generate_state,
                     get_sleep, get_water_consumption, get_body_fat, get_steps, get_activeness,
                     get_completed_challenge_entries_and_streaks
)

from vigour_contract_interactions import (get_challenge_verification_values, 
                                          submit_completed_challenges, CHALLENGE_MAPPING
)

import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

load_dotenv()
oauth_client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")

@app.route('/get-challenge', methods=['GET'])
def get_challenge():

    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)
    state = generate_state()
    return jsonify({'code_verifier': code_verifier, 
                    "state": state,
                    'code_challenge': code_challenge}
                )

@app.route('/get-tokens', methods=['POST'])
def get_tokens():
    code_verifier = request.json['code_verifier']
    code = request.json['code']

    url = "https://api.fitbit.com/oauth2/token"

    # Define the headers for the request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    auth = HTTPBasicAuth(oauth_client_id, client_secret)
    print(code, code_verifier)

    # Define the payload (form data)
    payload = {
        'client_id': oauth_client_id,
        'grant_type': 'authorization_code',
        'code': code,
        'code_verifier': code_verifier
    }

    # Make the POST request
    response = requests.post(url, headers=headers, auth=auth, data=payload)
    print(response.text)
    
    # Check the response
    if response.status_code == 200:
        print("Success:", response.json())
        return jsonify(response.json())
    else:
        print("Failed:", response.status_code, response.json())
        return jsonify({'error': response.json()}), response.status_code




@app.route("/fetch_and_submit_to_contract", methods=["POST"])
def fetch_and_submit_to_contract():

    
    scopes = request.json['scopes']
    enrolled_challenges = request.json['enrolled_challenges']
    username = request.json['username']
    access_token = request.json['access_token']
    contract_address = request.json['contract_address']
    abi = request.json['abi']

    print(enrolled_challenges)
    
    
    if not enrolled_challenges:
        return jsonify({"message": "No challenges enrolled, No action performed"}), 200
    
    enrolled_challenges_int = [CHALLENGE_MAPPING[challenge["type"]] for challenge in enrolled_challenges]
    print(enrolled_challenges_int)   
    verification_values = get_challenge_verification_values(enrolled_challenges_int, contract_address, abi)
    print(verification_values)
    
    # exit()
    for challenge in enrolled_challenges:
        tier = challenge["tier"]
        type_int = int(CHALLENGE_MAPPING[challenge["type"]])

        verification_tiervalue = verification_values[type_int]["tier" + str(tier)]
        # print(tiervalue)
        # exit()
        if challenge["type"] == "sleep":
            try:
                sleep_data = get_sleep(access_token, challenge["start_duration"], challenge["end_duration"])
                print(sleep_data)
            except:
                return jsonify({"message": "Encountered a problem fetching sleep data"}), 400

            completions, streaks = get_completed_challenge_entries_and_streaks(sleep_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

        elif challenge["type"] == "water":
            print("huh")
            try:
                response, success = get_water_consumption(access_token, challenge["start_duration"], challenge["end_duration"])
                if not success:
                    print(response)
                    return jsonify({"message": "Encountered a problem fetching water data, had to do with the request"}), 400
                
                water_data = response
                print(water_data)
            except Exception as e:
                print(e)
                return jsonify({"message": "Encountered a problem fetching water data something else"}), 400
            
            completions, streaks = get_completed_challenge_entries_and_streaks(water_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

            timestamp = int(datetime.datetime.now().timestamp() * 1000)
            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)


        elif challenge["type"] == "bodyfat":
            try:
                body_fat_data = get_body_fat(access_token, challenge["start_duration"], challenge["end_duration"])
                print(body_fat_data)
            except:
                return jsonify({"message": "Encountered a problem fetching body fat data"}), 400
            
            completions, streaks = get_completed_challenge_entries_and_streaks(body_fat_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

        elif challenge["type"] == "steps":
            try:    
                steps_data = get_steps(access_token, challenge["start_duration"], challenge["end_duration"])
                print(steps_data)
            except:
                return jsonify({"message": "Encountered a problem fetching steps data"}), 400
            
            completions, streaks = get_completed_challenge_entries_and_streaks(steps_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

        elif challenge["type"] == "activity":
            try:
                activeness_data = get_activeness(access_token, challenge["start_duration"], challenge["end_duration"])
                print(activeness_data)
            except:
                return jsonify({"message": "Encountered a problem fetching activeness data"}), 400  
            
            completions, streaks = get_completed_challenge_entries_and_streaks(activeness_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

        return jsonify({"message": "Success"}), 200


if __name__ == '__main__':
    app.run(debug=True)
