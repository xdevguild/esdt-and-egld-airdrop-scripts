from multiversx_sdk_wallet import UserSigner, UserPEM
from multiversx_sdk_core import Address, TokenPayment
from multiversx_sdk_core.transaction_builders import DefaultTransactionBuildersConfiguration, \
    MultiESDTNFTTransferBuilder
from multiversx_sdk_network_providers import ProxyNetworkProvider

from pathlib import Path

import json
import argparse

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'

# ---------------------------------------------------------------- #
#                         INPUTS
# ---------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument("--filename", help="CSV file with two cols : Address and Count", required=True)
parser.add_argument("--ids", help="List of token id of the ESDTs", nargs='+', required=True)
parser.add_argument('--amounts_airdrop', help="List of respective amount to send", nargs='+', type=int, required=True)
parser.add_argument("--pem", help="The wallet that sends txs (needs to hold the LKMEX)", required=True)
parser.add_argument("--decimals", help="The number of decimals (default 18)", required=False, default=18)
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
    i = 1
    for amount_airdrop in args.amounts_airdrop:
        airdrop_per_NFT = float(amount_airdrop) / (eligible_holders.Count.sum()) - 0.0001
        eligible_holders["Airdrop_" + str(i)] = airdrop_per_NFT * data_df.Count
        i += 1

# ---------------------------------------------------------------- #
#                         CONSTANTS
# ---------------------------------------------------------------- #
TOKEN_DECIMALS = args.decimals  # default : 18
TOKEN_IDs = []
for id in args.ids:
    TOKEN_IDs.append(id)


# ---------------------------------------------------------------- #
#                   MAIN ESDT FUNCTION
# ---------------------------------------------------------------- #
def sendMultipleESDT(owner, owner_on_network, receiver, amounts, signer):
    payments = []
    j = 1
    for amount_to_send in amounts:
        payment = TokenPayment.fungible_from_amount(TOKEN_IDs[j - 1], amount_to_send, TOKEN_DECIMALS)
        payments.append(payment)
        j += 1

    config = DefaultTransactionBuildersConfiguration(chain_id="1")

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

provider = ProxyNetworkProvider("https://gateway.multiversx.com")
owner_on_network = provider.get_account(owner)

# ---------------------------------------------------------------- #
#                     AIRDROP LOOP
# ---------------------------------------------------------------- #
for _, row in eligible_holders.iterrows():

    address = Address.from_bech32(row["Address"])
    k = 1
    quantities = []
    for amount in args.amounts_airdrop:
        quantity = row["Airdrop_" + str(k)] if args.weighted else airdrops_per_holder[k - 1]
        quantities.append(quantity)
        k += 1

    try:
        sendMultipleESDT(owner, owner_on_network, address, quantities, signer)
    except:
        # Keep those addresses aside for debugging, and re-sending after
        print(address)
