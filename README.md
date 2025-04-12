# Blockchain Certificate Generation and Verification System

This project enables organizations to generate, store, and verify certificates using blockchain and IPFS technology. The combination of blockchain and IPFS ensures that certificates are both tamper-proof and permanently accessible.

## Features

-   **Blockchain-based Certificate Verification**: Ensures certificates cannot be forged
-   **IPFS Storage via Pinata**: Certificate files are stored on IPFS for permanent, decentralized access
-   **Modern Streamlit UI**: User-friendly interface for all operations
-   **QR Code Generation**: Easy verification through QR codes
-   **Webcam QR Code Scanner**: Scan certificate QR codes directly with your device's camera
-   **Admin Dashboard**: Manage organizations and view all certificates
-   **User Dashboard**: Generate and view certificates for your organization

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Ganache (Local Blockchain)

-   Download and install Ganache from [Truffle Suite](https://trufflesuite.com/ganache/)
-   Start Ganache with port 8545
-   Note your first account address for the contract deployment

### 3. Deploy Smart Contract

```bash
python deploy_contract.py
```

-   Copy the contract address displayed after successful deployment

### 4. Configure the Application

-   Update the `.streamlit/secrets.toml` file with your configuration:

```toml
# Pinata API Keys - replace these with your actual keys
PINATA_API_KEY = "your_pinata_api_key"
PINATA_SECRET_API_KEY = "your_pinata_secret_api_key"

# Blockchain Configuration
[blockchain]
RPC_URL = "http://127.0.0.1:8545"  # Your Ganache or Ethereum node URL
CONTRACT_ADDRESS = "0xYourContractAddressHere"  # Address from step 3
CONTRACT_PATH = "CertificateVerification.json"
ACCOUNT_INDEX = 0  # Index of the account to use for transactions
```

### 5. Run the Application

```bash
streamlit run streamlit_app.py
```

## How It Works

1. **Certificate Generation**:

    - Organization creates a certificate with student details
    - Certificate is generated using the template
    - Certificate is uploaded to IPFS via Pinata
    - IPFS hash and certificate data are stored on the blockchain

2. **Certificate Verification**:
    - Upload a certificate file for verification, or
    - Scan a certificate QR code using your device's camera
    - System calculates the hash and checks it against the blockchain
    - If a match is found, certificate details and IPFS link are displayed

## Using the QR Code Scanner

1. Navigate to the "Scan QR Code" page from the sidebar
2. Allow camera access when prompted
3. Point your camera at a certificate QR code
4. The system will automatically detect and verify the certificate
5. Certificate details will be displayed if the QR code is valid

## Blockchain Integration

This project uses an Ethereum smart contract to store:

-   Organization details
-   Certificate hashes and metadata
-   IPFS URLs for permanent access

## IPFS Integration via Pinata

All certificate files are stored on IPFS through Pinata's pinning service:

-   Certificates are permanently accessible even if the original server is down
-   IPFS URLs are stored on the blockchain for verification
-   QR codes are also stored on IPFS

## Project Structure

-   `streamlit_app.py`: Main application code
-   `deploy_contract.py`: Script to deploy the smart contract
-   `CertificateVerification.sol`: Smart contract code
-   `CertificateVerification.json`: Compiled contract ABI and bytecode
-   `certificate_templates/`: Certificate template images
-   `static/`: Local storage for generated certificates and QR codes
-   `.streamlit/secrets.toml`: Configuration for API keys and blockchain settings

## License

MIT
