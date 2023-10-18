import os

from verifier import generate_code_verifier, generate_code_challenge, generate_state

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

if __name__ == '__main__':
    app.run(debug=True)
