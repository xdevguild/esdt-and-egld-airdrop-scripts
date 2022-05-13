# ELROND-LKMEX-AIRDROP
Python script that performs an airdrop of LKMEX to NFT holders. 

There are two different scripts : 
<ol>
  <li>"LKMEXSender_SameForEveryHolder.py" performs an equal airdrop for all addresses, not accounting for the number of NFTs hold.
</li>
  <li>"LKMEXSender_WeightedByNFTHold.py" performs an airdrop weighted by the NFT hold for each address</li>
</ol>


## Requirements

[Erdpy](https://docs.elrond.com/sdk-and-tools/erdpy/installing-erdpy/) needs to be installed.  <br>
Pandas as well.  <br>  <br>
Both libraries versions are in the requirements file, and they can be installed with pip. However I would recommend visiting Elrond's doc on Erdpy in order to be sure to install all necessary libraries.

## CLI

In a terminal the command should look like :

```python3 LKMEXSender_WeightedByNFTHold.py --filename LIST_OF_HOLDER_ADDRESSES.csv --amount_airdrop TOTAL_LKMEX_QUANTITY --id LKMEX_ID --pem PATH_TO.pem```

The CSV file should have two columns: "Address" and "Count" (for the number of NFTs hold). 


## Improvements

Note that there is a somewhat not accurate filter for smart contract addresses (supposedly filtering out marketplaces), by checking if the address has a minimum of 5 "q". However if you have an accurate list of marketplaces addresses, or for whatever reasons some of the holders have many "q" in the address you might need to update the code. So far the current version has always worked.
