from web3 import Web3
import json

contract_address = "0x6873fac90CB70553F802F3E78b3d42e1dEC84a7d"
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
# user_id = "123"
# user_name = "Alice"
# document_hash = "0x123456789abcdef"
# document_path = "/path/to/document"

sc = contract.functions
#sc.setUserDetails("13","Alic","0x123asdf6789abcdef","/path/to/p2").transact()
#sc.getDocHashByUserId(user_id).call()
