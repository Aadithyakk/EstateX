# xrpl_client_testnet.py

from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import Payment
from xrpl.transaction import send_transaction
from xrpl.utils import xrp_to_drops

# -------------------------------
# 1. Connect to the XRPL Testnet
# -------------------------------
JSON_RPC_URL = "https://s.altnet.rippletest.net:51234/"
client = JsonRpcClient(JSON_RPC_URL)

# -------------------------------
# 2. Create a new wallet
# -------------------------------
wallet = Wallet.create()
print("Wallet created!")
print("Seed:", wallet.seed)
print("Classic Address:", wallet.classic_address)

# -------------------------------
# 3. Build a payment transaction
# -------------------------------
# Replace with a valid Testnet destination address
destination_address = "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe"  

payment_tx = Payment(
    account=wallet.classic_address,
    amount=xrp_to_drops(10),  # 10 XRP
    destination=destination_address
)

# -------------------------------
# 4. Sign and submit the transaction
# -------------------------------
try:
    tx_response = send_transaction(payment_tx, wallet, client)
    print("Transaction submitted successfully!")
    print(tx_response.result)  # Print full transaction response
except Exception as e:
    print("Error submitting transaction:", e)