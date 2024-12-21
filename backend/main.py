import click
from web3 import Web3
from create import create_sub_contract, get_token_contract
from listen import listen
from withdraw import withdraw
from threading import Thread
from server import start_server

@click.command()
@click.argument("token_address", type=str, required=True)
@click.argument("public_key", type=str, required=True)
@click.argument("private_key", type=str, required=True)
@click.argument("provider_url", type=str, required=True)
@click.argument("subscription_cost", type=int, required=True)
@click.argument("subscription_frequency", type=int, required=True)
def process_subscription(token_address, public_key, private_key, provider_url, subscription_cost, subscription_frequency):
    w3 = Web3(Web3.HTTPProvider(provider_url))

    if not w3.is_connected():
        raise ConnectionError("can't connect to node provider")

    sub = create_sub_contract(w3, public_key, private_key, token_address, subscription_cost, subscription_frequency)
    token = get_token_contract(w3, token_address)
    Thread(target=listen, args=(w3, token, sub)).start()
    Thread(target=withdraw, args=(w3, sub, public_key, private_key)).start()
    start_server()


if __name__ == "__main__":
    process_subscription()
