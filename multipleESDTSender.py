from multiversx_sdk_wallet import UserSigner, UserPEM
from multiversx_sdk_core import Address, TokenPayment
from multiversx_sdk_core.transaction_builders import DefaultTransactionBuildersConfiguration, \
    MultiESDTNFTTransferBuilder
from multiversx_sdk_cli.accounts import Account
from multiversx_sdk_network_providers import ProxyNetworkProvider

from pathlib import Path

import json
import argparse
import requests
import sys

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

# ---------------------------------------------------------------- #
#                         INPUTS
# ---------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument("--filename", help="CSV file with two cols : Address and Count", required=True)
parser.add_argument("--ids", help="List of token id of the ESDTs", nargs='+', required=True)
parser.add_argument('--amounts_airdrop', help="List of respective amount to send", nargs='+', type=int, required=True)
parser.add_argument('--decimals', help="List of respective decimals (default 18)", nargs='+', type=int, default=[])
parser.add_argument("--pem", help="The wallet that sends txs (needs to hold the ESDT)", required=True)
parser.add_argument("--weighted",
                    help="Flag (true for an airdrop weighted by the quantity of NFTs hold for each address.)",
                    required=False, default=False)

args = parser.parse_args()

# Read the input file
data_df = pd.read_csv(args.filename)

# If not done already, remove SC addresses
eligible_holders = data_df[data_df.Address.apply(lambda x: "qqqqqq" not in x)]

# Compute the total of token per address (not taking into account the number of NFT hold)
# TMP FIX : Remove 0.0001 token per holder to avoid "insufficient funds" (due to Python's loss of precision)
airdrops_per_holder = []
for amount_airdrop in args.amounts_airdrop:
    airdrop_per_holder = float(amount_airdrop) / (eligible_holders.shape[0]) - 0.0001
    airdrops_per_holder.append(airdrop_per_holder)

# Compute the weighted airdrop if set to true as an argument
if args.weighted:
    for index, amount_airdrop in enumerate(args.amounts_airdrop):
        airdrop_per_NFT = float(amount_airdrop) / (eligible_holders.Count.sum()) - 0.0001
        eligible_holders["Airdrop_" + str(index)] = airdrop_per_NFT * data_df.Count

# ---------------------------------------------------------------- #
#                         CONSTANTS
# ---------------------------------------------------------------- #

config_network = {
    "mainnet": {"chainID": "1", "proxy": ""},
    "devnet": {"chainID": "D", "proxy": "devnet-"},
    "testnet": {"chainID": "T", "proxy": "testnet-"}
}

CHAIN = "mainnet"
CHAIN_ID = config_network[CHAIN]["chainID"]
PROXY = config_network[CHAIN]["proxy"]

TOKEN_DECIMALS = []
TOKEN_IDs = []

wallet = Account(pem_file=Path(f"./{args.pem}")).address

for index, id in enumerate(args.ids):
    try:
        response = requests.get(f'https://{PROXY}api.multiversx.com/tokens/{id}')
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: Token {id} does not exist")
        sys.exit()

    try:
        response = requests.get(f'https://{PROXY}api.multiversx.com/accounts/{wallet}/tokens/{id}')
        response.raise_for_status()

        if index < len(args.decimals):
            TOKEN_DECIMALS.append(args.decimals[index])
        else:
            TOKEN_DECIMALS.append(18)  # default : 18

        balance = response.json()['balance']
        amount_to_drop = float(args.amounts_airdrop[index]) * pow(10, int(TOKEN_DECIMALS[index]))
        if float(balance) < amount_to_drop:
            print(f"ERROR: You don't have enough {id}")
            sys.exit()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: You don't own any {id}")
        sys.exit()
    TOKEN_IDs.append(id)


# ---------------------------------------------------------------- #
#                   MAIN Multiple ESDT FUNCTION
# ---------------------------------------------------------------- #
def sendMultipleESDT(owner, owner_on_network, receiver, amounts, signer):
    payments = []
    for index, amount_to_send in enumerate(amounts):
        payment = TokenPayment.fungible_from_amount(TOKEN_IDs[index], amount_to_send, TOKEN_DECIMALS[index])
        payments.append(payment)

    config = DefaultTransactionBuildersConfiguration(chain_id=CHAIN_ID)

    builder = MultiESDTNFTTransferBuilder(
        config=config,
        sender=owner,
        destination=receiver,
        payments=payments,
        nonce=owner_on_network.nonce
    )
    tx = builder.build()

    tx.signature = signer.sign(tx)
    hashes = provider.send_transaction(tx)
    owner_on_network.nonce += 1

    return hashes


# ---------------------------------------------------------------- #
#                  SETTING MAINNET PARAMS
# ---------------------------------------------------------------- #
# The signer of the tokens, that will send them
signer = UserSigner.from_pem_file(Path(f"./{args.pem}"))
pem = UserPEM.from_file(Path(f"./{args.pem}"))
pubkey = bytes.fromhex(pem.public_key.hex())
owner = Address(pubkey, "erd")

provider = ProxyNetworkProvider(f"https://{PROXY}gateway.multiversx.com")
owner_on_network = provider.get_account(owner)

# ---------------------------------------------------------------- #
#                     AIRDROP LOOP
# ---------------------------------------------------------------- #
for _, row in eligible_holders.iterrows():

    address = Address.from_bech32(row["Address"])
    quantities = []
    for index, amount in enumerate(args.amounts_airdrop):
        quantity = row["Airdrop_" + str(index)] if args.weighted else airdrops_per_holder[index]
        quantities.append(quantity)

    try:
        sendMultipleESDT(owner, owner_on_network, address, quantities, signer)
    except:
        # Keep those addresses aside for debugging, and re-sending after
        print(address)
