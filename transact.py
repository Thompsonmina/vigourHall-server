import os, json

from dotenv import load_dotenv
from eth_account import Account
from web3 import Web3
from web3.middleware import geth_poa_middleware

load_dotenv()

scroll_sepolia_url = "https://sepolia-rpc.scroll.io/"
w3 = Web3(Web3.HTTPProvider(scroll_sepolia_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Load the private key
private_key = os.getenv("PRIVATE_KEY")
account = Account.from_key(private_key)




def submit_completed_challenges(abi, contract_address, username, challengetype, newCompletionsnum, continueStreak, streaknumber, data_url=""):

    vigour_contract = w3.eth.contract(address=contract_address, abi=abi)

    args = [username, challengetype, newCompletionsnum, continueStreak, streaknumber, data_url]
    txn = vigour_contract.functions.updateUserChallengesState(*args).build_transaction({
        "chainId": 534351,
        "gas": 70000,
        "gasPrice": w3.to_wei("1", "gwei"),
        "nonce": w3.eth.get_transaction_count(account.address),
    })

    txn["gas"] = vigour_contract.functions.updateUserChallengesState(*args).estimate_gas({"from": account.address})
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)

    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(txn_hash)
    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

    print(txn_receipt)
    return txn_receipt

abi = json.load(open("contract_abi.json"))
print(abi[0])

submit_completed_challenges(abi,
    "0x7992DA49ab6Ed2617458c851fAcde877B85D44D4",
    "tom",
    3,
    2,
    True,
    2,)
