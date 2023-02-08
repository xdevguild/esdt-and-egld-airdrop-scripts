# ESDT and EGLD AIRDROP
Python scripts that performs an airdrop of classical ESDT tokens or EGLD to NFT holders. 

There are two different scripts : 
<ol>
  <li>"EGLDSender.py" performs an airdrop of EGLD tokens </li>
  <li>"ESDTSender.py" performs an airdrop of ESDT tokens </li>
  <li>"multipleEGLDSender.py" performs an airdrop of multiple ESDT tokens </li>
</ol>


## Requirements

[multiversx-sdk-core](https://pypi.org/project/multiversx-sdk-core/) needs to be installed.  <br>
[multiversx-sdk-wallet](https://pypi.org/project/multiversx-sdk-wallet/) needs to be installed.  <br>
[multiversx-sdk-network-providers](https://pypi.org/project/multiversx-sdk-network-providers/) needs to be installed.  <br>
Pandas as well.  <br>  <br>
All libraries versions are in the requirements file, and they can be installed with pip. However I would recommend visiting MultiversX's doc on Erdpy in order to be sure to install all necessary libraries.

You need also need a [walletKey.pem](https://docs.multiversx.com/sdk-and-tools/sdk-py/deriving-the-wallet-pem-file/#__docusaurus/)

## Devnet

In order to use the Devnet you need to: <br><br>
Change this line: 
```provider = ProxyNetworkProvider("https://gateway.multiversx.com")```
and use this gateway: ```https://devnet-gateway.multiversx.com```

Change this line: ```config = DefaultTransactionBuildersConfiguration(chain_id="1")```
use ```chain_id="D"```

## CLI

In a terminal the command should look like :

```python3 EGLDSender.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amount_airdrop EGLD_QUANTITY --pem PATH_TO.pem```

or

```python3 ESDTSender.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amount_airdrop ESDT_QUANTITY --id ESDT_ID --pem PATH_TO.pem```

or 

```python3 multipleESDTSender.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amounts_airdrop ESDT_QUANTITY_1 ESDT_QUANTITY_N --ids ESDT_ID_1 ESDT_ID_N --decimals DECIMALS_1 DECIMALS_N --pem PATH_TO.pem```


The CSV file should have two columns: "Address" and "Count" (for the number of NFTs hold). You can use [multiversX-nft-holders](https://github.com/xdevguild/multiversX-nft-holders) to get the CSV file for NFT collections. <br>
An additional argument can be used `--weighted`. If set to true, the amount of tokens airdropped is function of the NFTs hold for each address. If
set to false (default), then the amount is the same for every address. <br>

Note also that there is argument `--decimals` that is default to 18 for classical ESDT tokens, but can be changed if this is not the case.


## Improvements

There is a somewhat not accurate filter for smart contract addresses (supposedly filtering out marketplaces), by checking if the address has a minimum of 6 "q". However if you have an accurate list of marketplaces addresses, or for whatever reasons some of the holders have many "q" in the address you might need to update the code. So far the current version has always worked.
