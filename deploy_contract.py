from web3 import Web3, HTTPProvider
import json
import solcx
import os
import toml

def main():
    # Install solc 0.8.11
    print("Installing solc compiler...")
    solcx.install_solc('0.8.11')
    solcx.set_solc_version('0.8.11')
    
    # Compile the contract
    print("Compiling contract...")
    with open('CertificateVerification.sol', 'r') as file:
        contract_source_code = file.read()
    
    compiled_sol = solcx.compile_source(
        contract_source_code,
        output_values=['abi', 'bin']
    )

    contract_id, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    
    # Save the ABI to a file for later use
    with open('CertificateVerification.json', 'w') as file:
        json.dump({"abi": abi, "bytecode": bytecode}, file)
    
    # Connect to Ganache
    print("Connecting to Ganache...")
    rpc_url = 'http://127.0.0.1:7545'  # Default Ganache URL
    w3 = Web3(HTTPProvider(rpc_url))
    
    # Check connection - compatible with older Web3.py versions
    try:
        w3.eth.blockNumber  # This will raise an exception if not connected
        print("Connected to Ganache successfully")
    except Exception as e:
        print(f"Failed to connect to Ganache: {str(e)}")
        return
    
    # Set the default account
    account_index = 0
    w3.eth.defaultAccount = w3.eth.accounts[account_index]
    
    # Deploy the contract
    print("Deploying contract...")
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = Contract.constructor().transact()
    
    # Wait for the transaction to be mined
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    
    # Get the contract address
    contract_address = tx_receipt.contractAddress
    
    print(f"Contract deployed at address: {contract_address}")
    
    # Update secrets.toml file with the new contract address
    try:
        # Create .streamlit directory if it doesn't exist
        os.makedirs('.streamlit', exist_ok=True)
        
        # Try to load existing secrets if available
        secrets_path = '.streamlit/secrets.toml'
        secrets = {}
        
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = toml.load(f)
        
        # Ensure blockchain section exists
        if 'blockchain' not in secrets:
            secrets['blockchain'] = {}
        
        # Update contract address
        secrets['blockchain']['RPC_URL'] = rpc_url
        secrets['blockchain']['CONTRACT_ADDRESS'] = contract_address
        secrets['blockchain']['CONTRACT_PATH'] = 'CertificateVerification.json'
        secrets['blockchain']['ACCOUNT_INDEX'] = account_index
        
        # Write updated secrets back to file
        with open(secrets_path, 'w') as f:
            toml.dump(secrets, f)
        
        print(f"Updated {secrets_path} with new contract address")
    except Exception as e:
        print(f"Failed to update secrets.toml: {str(e)}")
        print("Please manually update the contract address in .streamlit/secrets.toml")
    
    print("\nNext Steps:")
    print("1. Ensure Ganache keeps running")
    print("2. Run the application: streamlit run streamlit_app.py")
    
    return contract_address

if __name__ == "__main__":
    main() 