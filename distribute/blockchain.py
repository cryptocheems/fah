from web3 import Web3, contract
from os import getenv
from dotenv import load_dotenv

load_dotenv()

PROVIDER = "https://xdai.1hive.org/"
PRIVATE = getenv("PRIVATE")
DEV = "0xB67D4dd9F0E25760dC0f373d79588Bd0169b2335"

w3 = Web3(Web3.HTTPProvider(PROVIDER))


def format_address(address: str):
    try:
        return w3.toChecksumAddress(address)
    except:
        return None
