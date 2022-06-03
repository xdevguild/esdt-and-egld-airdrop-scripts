# ESDT and LKMEX AIRDROP
Python scripts that performs an airdrop of classical ESDT tokens or LKMEX to NFT holders. 

There are two different scripts : 
<ol>
  <li>"LKMEXSender.py" performs an airdrop of LKMEX tokens
</li>
  <li>"ESDTSender.py" performs an airdrop classical ESDT tokens </li>
</ol>


## Requirements

[Erdpy](https://docs.elrond.com/sdk-and-tools/erdpy/installing-erdpy/) needs to be installed.  <br>
Pandas as well.  <br>  <br>
Both libraries versions are in the requirements file, and they can be installed with pip. However I would recommend visiting Elrond's doc on Erdpy in order to be sure to install all necessary libraries.

## CLI

In a terminal the command should look like :

```python3 LKMEXSender.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amount_airdrop TOTAL_LKMEX_QUANTITY --id LKMEX_ID --pem PATH_TO.pem```

or 

```python3 ESDTSender.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amount_airdrop TOTAL_ESDT_QUANTITY --id ESDT_ID --pem PATH_TO.pem```


The CSV file should have two columns: "Address" and "Count" (for the number of NFTs hold). <br>
An additionnal argument can be used `--weighted`. If set to true, the amount of tokens airdropped is function of the NFTs hold for each address. If
set to false (default), then the amount is the same for every address. <br>

Note also that there is argument `--decimals` that is default to 18 for classical ESDT tokens, but can be changed if this is not the case.


## Improvements

Note that there is a somewhat not accurate filter for smart contract addresses (supposedly filtering out marketplaces), by checking if the address has a minimum of 6 "q". However if you have an accurate list of marketplaces addresses, or for whatever reasons some of the holders have many "q" in the address you might need to update the code. So far the current version has always worked.
