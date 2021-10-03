from web3 import Web3, contract
from os import getenv
from dotenv import load_dotenv

load_dotenv()

PROVIDER = "https://rpc.xdaichain.com/"
PRIVATE = getenv("PRIVATE")
DEV = "0xB67D4dd9F0E25760dC0f373d79588Bd0169b2335"
FAH_CONTRACT = "0x8EA52113AF2a2ebbAb823037aFa6cc903B2BBbC8"
ABI = '[{"type":"constructor","stateMutability":"nonpayable","inputs":[{"type":"address","name":"_cheemscoin","internalType":"contract IERC20"}]},{"type":"function","stateMutability":"view","outputs":[{"type":"address","name":"","internalType":"address"}],"name":"dev","inputs":[]},{"type":"function","stateMutability":"nonpayable","outputs":[],"name":"distribute","inputs":[{"type":"uint256","name":"_total","internalType":"uint256"},{"type":"tuple[]","name":"_users","internalType":"struct User[]","components":[{"type":"address","name":"account","internalType":"address"},{"type":"uint256","name":"amount","internalType":"uint256"}]}]}]'

w3 = Web3(Web3.HTTPProvider(PROVIDER))
if not w3.isConnected():
    raise Exception("Connection to xDai Chain failed")

fah: contract.Contract = w3.eth.contract(FAH_CONTRACT, abi=ABI)


def distribute_cheems(total: int, users: "list[dict]") -> str:
    formatted_amounts = [[user["address"], w3.toWei(user["cheems"], "ether")] for user in users]
    nonce = w3.eth.get_transaction_count(DEV)
    builtTx = fah.functions.distribute(
        w3.toWei(total, "ether"), formatted_amounts
    ).buildTransaction({"nonce": nonce, "gas": 1_000_000, "gasPrice": w3.toWei("1", "gwei")})
    signedTx = w3.eth.account.sign_transaction(builtTx, private_key=PRIVATE)
    # ! This is what actually sends the Cheemscoin
    return w3.toHex(w3.eth.send_raw_transaction(signedTx.rawTransaction))


def format_address(address: str):
    try:
        return w3.toChecksumAddress(address[:42])
    except ValueError:
        return None
