# from web3 import Web3




# Import necessary libraries
from web3 import Web3
import time

ganache_url = 'http://ganache:8545'
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Function to print the latest block using Web3
def print_latest_block():

    latest_block = web3.eth.block_number

    print(f"Latest block number: {latest_block}")



def print_stuff():
    print("THIS IS A PRINT FROM THE CONTAINER")
    return 8

def main():
    while True:
        print_latest_block()
        time.sleep(60)



if __name__ == "__main__":
    main()
