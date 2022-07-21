import binascii
from tokenize import Hexnumber

from erdpy.accounts import Account
from erdpy.proxy import ElrondProxy
from erdpy.transactions import Transaction

import argparse

import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


# ---------------------------------------------------------------- #
#                         INPUTS
# ---------------------------------------------------------------- #
parser = argparse.ArgumentParser()
parser.add_argument("--filename", help="CSV file with two cols : Address and Count", required=True)
parser.add_argument("--amount_airdrop", help="The total amount of ESDT ot be airdropped", required=True)
parser.add_argument("--id", help="The token id of the ESDT", required=True)
parser.add_argument("--pem", help="The wallet that sends txs (needs to hold the LKMEX)", required=True)
parser.add_argument("--decimals", help="The number of decimals (default 18)", required=False, default=18)
parser.add_argument("--weighted", help="Flag (true for an airdrop weighted by the quantity of NFTs hold for each address.)", required=False, default=False)


args = parser.parse_args()

# Read the input file
data_df = pd.read_csv(args.filename)

# If not done already, remove SC addresses
eligible_holders = data_df[data_df.Address.apply(lambda x: "qqqqqq" not in x)]

# Compute the total of token per address (not taking into account the number of NFT hold)
# TMP FIX : Remove 0.0001 token per holder to avoid "insufficient funds" (due to Python's loss of precision)
airdrop_per_holder = float(args.amount_airdrop) / ( eligible_holders.shape[0]) - 0.0001  

# Compute the weighted airdrop if set to true as an argument
if args.weighted : 
    airdrop_per_NFT = float(args.amount_airdrop) / ( eligible_holders.Count.sum() ) - 0.0001      
    eligible_holders["Airdrop"] = airdrop_per_NFT*data_df.Count



# ---------------------------------------------------------------- #
#                         CONSTANTS
# ---------------------------------------------------------------- #
TOKEN_DECIMALS = 10**args.decimals # default : 10^18  
TOKEN_ID = args.id 


# ---------------------------------------------------------------- #
#                         HELPER FUNCTIONS
# ---------------------------------------------------------------- #
def text_to_hex(text) :
    return binascii.hexlify(text.encode()).decode()


# Sometimes need to add a 0 (if it's even, to be sure that is grouped by bytes)
def num_to_hex(num) : 
    hexa = format(num, "x")
    if len(hexa)%2==1 :  
        return "0" + hexa
    return hexa


def int_to_BigInt(num) : 
    return int(f"{num*TOKEN_DECIMALS:.1f}".split(".")[0])         
    


# ---------------------------------------------------------------- #
#                   MAIN ESDT FONCTION
# ---------------------------------------------------------------- #
def sendESDT(owner, receiver, amount):  

    payload = "ESDTTransfer@" + "@".join([text_to_hex(TOKEN_ID),
                                          num_to_hex(int_to_BigInt(amount))])

    tx = Transaction()
    tx.nonce = owner.nonce
    tx.value = "0"
    tx.sender = owner.address.bech32()
    tx.receiver = receiver.address.bech32()
    tx.gasPrice = gas_price
    tx.gasLimit = 500000
    tx.data = payload
    tx.chainID = chain
    tx.version = tx_version

    tx.sign(owner)
    tx_hash = tx.send(proxy)
    owner.nonce+=1
    return tx_hash   




         
# ---------------------------------------------------------------- #
#                  SETTING MAINNET PARAMS
# ---------------------------------------------------------------- #
proxy_address = "https://gateway.elrond.com"
proxy = ElrondProxy(proxy_address)
network = proxy.get_network_config()
chain = network.chain_id
gas_price = network.min_gas_price
tx_version = network.min_tx_version



# The owner of the tokens, that will send them
owner = Account(pem_file=args.pem)
owner.sync_nonce(proxy)


# ---------------------------------------------------------------- #
#                     AIRDROP LOOP
# ---------------------------------------------------------------- #
for _, row in eligible_holders.iterrows():

    address = row["Address"] 
    quantity = row["Airdrop"] if args.weighted else airdrop_per_holder

    
    try :
        sendESDT(owner, Account(address), quantity)
    except :
        # Keep those addresses aside for debugging, and re-sending after 
        print(address)

