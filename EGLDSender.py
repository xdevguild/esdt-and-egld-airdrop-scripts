from multiversx_sdk_wallet import UserSigner, UserPEM
from multiversx_sdk_core import Address, TokenPayment
from multiversx_sdk_core.transaction_builders import DefaultTransactionBuildersConfiguration
from multiversx_sdk_core.transaction_builders import EGLDTransferBuilder
from multiversx_sdk_network_providers import ProxyNetworkProvider

from pathlib import Path

import argparse

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

# ---------------------------------------------------------------- #
#                         INPUTS
# ---------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument("--filename", help="CSV file with two cols : Address and Count", required=True)
parser.add_argument("--amount_airdrop", help="The total amount of EGLD to be airdropped", required=True)
parser.add_argument("--data", help="Message to send", nargs='+', type=str, default=[])
parser.add_argument("--pem", help="The wallet that sends txs (needs to hold the EGLD)", required=True)
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
airdrop_per_holder = float(args.amount_airdrop) / (eligible_holders.shape[0]) - 0.0001

# Compute the weighted airdrop if set to true as an argument
if args.weighted:
    airdrop_per_NFT = float(args.amount_airdrop) / (eligible_holders.Count.sum()) - 0.0001
    eligible_holders["Airdrop"] = airdrop_per_NFT * data_df.Count

# Get the data message
data = " ".join([str(item) for item in args.data])

# ---------------------------------------------------------------- #
#                   MAIN EGLD FUNCTION
# ---------------------------------------------------------------- #
def sendEGLD(owner, owner_on_network, receiver, amount, signer):

    payment = TokenPayment.egld_from_amount(amount)
    config = DefaultTransactionBuildersConfiguration(chain_id="1")

    builder = EGLDTransferBuilder(
        config=config,
        sender=owner,
        receiver=receiver,
        payment=payment,
        data=data,
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
# The signer of the EGLDs, that will send them
signer = UserSigner.from_pem_file(Path(f"./{args.pem}"))

# The wallet of the owner of the EGLDs
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
    quantity = row["Airdrop"] if args.weighted else airdrop_per_holder

    try:
        sendEGLD(owner, owner_on_network, address, quantity, signer)
    except:
        # Keep those addresses aside for debugging, and re-sending after
        print(address)
