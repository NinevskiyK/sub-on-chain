import time
from web3 import Web3
from solcx import compile_standard, install_solc


def get_token_contract(w3: Web3.HTTPProvider, erc20_address):
    with open("contracts/openzeppelin-contracts/contracts/token/ERC20/IERC20.sol", "r", encoding='utf-8') as f:
        solidity_code = f.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IERC20.sol": {"content": solidity_code}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi"]
                }
            }
        },
    }, solc_version="0.8.28",
    )

    abi = compiled_sol["contracts"]["IERC20.sol"]["IERC20"]["abi"]

    contract = w3.eth.contract(address=erc20_address, abi=abi)
    return contract

def create_sub_contract(w3: Web3.HTTPProvider, address, pk, erc20_address, cost, sub_period_sec):
    with open("contracts/sub.sol", "r", encoding='utf-8') as f:
        solidity_code = f.read()

    install_solc("0.8.28")
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {"MyContract.sol": {"content": solidity_code}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.deployedBytecode", "evm.methodIdentifiers"]}
            }
        }
    }, allow_paths=".", solc_version="0.8.28")

    bytecode = compiled_sol['contracts']['MyContract.sol']['Subscription']['evm']['bytecode']['object']
    abi = compiled_sol['contracts']['MyContract.sol']['Subscription']['abi']

    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    constructor_args = (erc20_address, cost, sub_period_sec)
    print(w3.eth.gas_price)
    transaction = Contract.constructor(*constructor_args).build_transaction({
        'from': address,
        'nonce': w3.eth.get_transaction_count(address),
        'gasPrice': w3.eth.gas_price * 2,
    })

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    while True:
        try:
            tx_receipt = w3.eth.get_transaction_receipt(tx_hash)
            break
        except:
            print('.', end='', flush=True)
            time.sleep(5)
    print('Transaction created! address: ', tx_receipt.contractAddress)

    contract = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
    return contract
