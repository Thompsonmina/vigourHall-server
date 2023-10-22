import os,datetime
from collections import defaultdict

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
web3_storage_token = os.getenv("WEB3_STORAGE_TOKEN")    

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Hello World!'})

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


@app.route("/store_fitness_data/<username>", methods=["POST"])
def store_fitness_data(username):
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    headers = {
        'Authorization': f'Bearer {web3_storage_token}',
        'X-NAME':  f"{username}.json" # Optional, encode
    }

    # Upload the file
    response = requests.post('https://api.web3.storage/upload', headers=headers, files={'file': file})

    print(response.json())
    if response.status_code == 200:
        return jsonify({"message": "File uploaded successfully", "cid": response.json()["cid"]})
    else:
        return jsonify({"error": f"Failed to upload. Status code: {response.status_code}, Message: {response.text}"}), 400


@app.route("/get_fitness_data/<c_id>", methods=["GET"])
def get_fitness_data(c_id):
    pass

@app.route("/store_new_cid/<username>", methods=["POST"])
def store_new_cid(username):
    c_id = request.json['cid']
    print(c_id)
    return jsonify({"message": "Success"}), 200

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
    fitness_data = defaultdict(dict)
    for challenge in enrolled_challenges:
        tier = challenge["tier"]
        type_int = int(CHALLENGE_MAPPING[challenge["type"]])

        verification_tiervalue = verification_values[type_int]["tier" + str(tier)]
        # print(tiervalue)
        # exit()
        timestamp = int(datetime.datetime.now().timestamp() * 1000)
        print(timestamp, "timestamp")
        if challenge["type"] == "sleep":
            try:
                response, success = get_sleep(access_token, challenge["start_duration"], challenge["end_duration"])
                if not success:
                    print(response)
                    return jsonify({"message": "Encountered a problem fetching sleep data, had to do with the request"}), 400
                sleep_data = response
                print(sleep_data)
            except Exception as e:
                print(e)
                return jsonify({"message": "Encountered a problem fetching sleep data"}), 400
            
            
            completions, streaks = get_completed_challenge_entries_and_streaks(sleep_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)

            for k in sleep_data:
                fitness_data[k]["sleep (in minutes)"] = sleep_data[k]

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

            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)

            for k in water_data:
                fitness_data[k]["water consumed (in millilitres)"] = water_data[k]


        elif challenge["type"] == "bodyfat":
            try:
                response, success = get_body_fat(access_token, challenge["start_duration"], challenge["end_duration"])
                if not success:
                    print(response)
                    return jsonify({"message": "Encountered a problem fetching body fat data, had to do with the request"}), 400
                
                body_fat_data = response
                print(body_fat_data)
            except Exception as e:
                print(e)
                return jsonify({"message": "Encountered a problem fetching body fat data"}), 400
            
            completions, streaks = get_completed_challenge_entries_and_streaks(body_fat_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)

            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)

            for k in body_fat_data:
                fitness_data[k]["body fat (in percentage)"] = body_fat_data[k]


        elif challenge["type"] == "steps":
            
            try:
                response, success = get_steps(access_token, challenge["start_duration"], challenge["end_duration"])
                print(response, "most likely")
                if not success:
                    print(response)
                    return jsonify({"message": "Encountered a problem fetching steps data, had to do with the request"}), 400  

                steps_data = response
                print(steps_data, "steps data")           
           
            except Exception as e:
                print(e)
                return jsonify({"message": "Encountered a problem fetching steps data"}), 400   
            
            completions, streaks = get_completed_challenge_entries_and_streaks(steps_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)
            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)

            for k in steps_data:
                fitness_data[k]["steps"] = steps_data[k]

        elif challenge["type"] == "activity":
            try:
                response, success = get_activeness(access_token, challenge["start_duration"], challenge["end_duration"])
                if not success:
                    print(response)
                    return jsonify({"message": "Encountered a problem fetching activeness data, had to do with the request"}), 400
                
                activeness_data = response
                print(activeness_data)
            except Exception as e:
                print(e)
                return jsonify({"message": "Encountered a problem fetching activeness data"}), 400
            
            completions, streaks = get_completed_challenge_entries_and_streaks(activeness_data, verification_tiervalue, challenge["start_duration"], challenge["end_duration"])
            print(completions, streaks)
            receipt = submit_completed_challenges(abi, contract_address, username, type_int, completions, streaks, timestamp, completions == streaks)
            print(receipt)

            for k in activeness_data:
                fitness_data[k]["activeness (in minutes)"] = activeness_data[k]

    return jsonify({"message": "Success", "fitness_data": fitness_data}), 200


if __name__ == '__main__':
    app.run(debug=True)
