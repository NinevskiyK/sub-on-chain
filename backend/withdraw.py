import os
import json
from shared_state import subs, subs_candidates
from listen import allowance

import web3

STATE_FILE = "withdraw.json"

def save_state(last_got):
    with open(STATE_FILE, "w", encoding='utf-8') as f:
        json.dump(last_got, f)

def get_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding='utf-8') as f:
            js = json.load(f)
            return js
    else:
        return {}


def withdraw(w3: web3.HTTPProvider, subscription: web3.eth.Contract, address, pk):
    last_got = get_state()
    for k, _ in last_got.items():
        subs_candidates.add(k)
    freq = subscription.functions.subPeriodSec().call()
    cost = subscription.functions.cost().call()

    while True:
        for sub in subs_candidates:
            last_got_sub = last_got.get(sub, 0)
            if last_got_sub + freq <= w3.eth.get_block('latest')['timestamp']:
                if allowance[sub] < cost:
                    if sub in subs:
                        subs.remove(sub)
                try:
                    transaction = subscription.functions.withdrawMoney(sub).build_transaction({
                    "from": address,
                    "nonce": w3.eth.get_transaction_count(address),
                    "gasPrice": w3.eth.gas_price * 2
                    })

                    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=pk)
                    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

                    txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
                    if txn_receipt['status'] != 0:
                        last_got[sub] = w3.eth.get_block(txn_receipt['blockNumber'])['timestamp']
                        print(f"withdraw {cost} from {sub} at {last_got[sub]}")
                        subs.add(sub)
                        allowance[sub] -= cost
                    elif sub in subs:
                        subs.remove(sub)
                except:
                    if sub in subs:
                        subs.remove(sub)

        save_state(last_got)
