from web3 import Web3
import json

contract_address = "0xE5cc534E5C1CCAd32c406821819009d3922a7C36"
contract_path = 'F:/major project/build/contracts/UserDataStorage.json'
rpc_endpoint = "http://127.0.0.1:7545"

with open(contract_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

# Connect to the Ethereum node
w3 = Web3(Web3.HTTPProvider(rpc_endpoint))
# Check if the connection is successful
if not w3.is_connected():
    print("Failed to connect to Ethereum node.")
else:
    print("Connected to Ethereum node.")

# Set the default account (replace with your Ganache account)
w3.eth.default_account = w3.eth.accounts[0]
contract = w3.eth.contract(address=contract_address, abi=contract_abi)


# Example: Call the setUserDetails function
# user_id = "112"
# user_name = "Alice"
# document_hash = "0x123456789abcdef"
# document_path = "/path/to/document"


sc = contract.functions
# sc.setUserDetails("13211","Alic2d","0x1232a11sdf6789abcdef","/path/to/p122",1231244).transact()

#sc.getDocHashByUserId(user_id).call()


