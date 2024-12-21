import os
import time
import web3
import web3.eth
import json
from shared_state import subs_candidates

STATE_FILE = "state.json"

def save_state(block_number, state):
    with open(STATE_FILE, "w", encoding='utf-8') as f:
        json.dump({"block": block_number, "allowance": state}, f)

def get_state(w3):
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding='utf-8') as f:
            js = json.load(f)
            return js['block'], js['allowance']
    else:
        block = w3.eth.block_number
        return block, {}

allowance = {}
def listen(w3: web3.HTTPProvider, token: web3.eth.Contract, subscription: web3.eth.Contract):
    global allowance
    last_processed_block, allowance_ = get_state(w3)

    while True:
        current_block = w3.eth.get_block('latest')['number']

        if current_block > last_processed_block:
            events = token.events.Approval.create_filter(
                from_block=last_processed_block + 1, to_block=current_block
            ).get_all_entries()

            for event in events:
                owner = event.args.owner
                spender = event.args.spender
                value = event.args.value
                if spender == subscription.address:
                    allowance[owner] = value
                    print(f"Мне одобрил: {owner} {value} токенов (контракт {spender})")
                    subs_candidates.add(owner)

            last_processed_block = current_block
            print("processed until: ", last_processed_block)
            save_state(current_block, allowance)

        time.sleep(1)
