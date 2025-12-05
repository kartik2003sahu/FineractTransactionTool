# Fineract Transaction Management Tool

A powerful web-based tool for managing Fineract loan transactions with undo and replay capabilities.

## ✨ Features

- 🔄 **Undo Transactions**: Reverse multiple transactions from a loan
- 📊 **Excel Export/Import**: Edit transaction data in Excel
- 💰 **Make Repayments**: Replay corrected transactions automatically
- 📁 **Session Management**: Automatic organization with complete audit trail
- 🌐 **Network Resilience**: Auto-retry on network failures
- 🎯 **User-Friendly**: Modern web interface

## 📋 Prerequisites

- **Python 3.8+** (Download from [python.org](https://www.python.org/downloads/))
- **Windows/Linux/Mac** (Instructions for Windows included)
- **Fineract Server Access** (API URL and credentials)

## 🚀 Quick Start

### 1. Download the Tool

Download or clone this repository to your computer:
```bash
# Option 1: Download ZIP and extract
# Option 2: Clone with git
git clone <repository-url>
cd TransactionTool
```

### 2. Install Python Dependencies

Open Command Prompt/Terminal in the `TransactionTool` folder and run:

```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- fastapi - Web framework
- uvicorn - Web server
- python-dotenv - Environment variable management
- requests - HTTP client
- pandas - Excel handling
- openpyxl - Excel file format support
- python-multipart - File upload support

### 3. Configure Your Settings

1. Copy `.env.template` to `.env`:
   ```bash
   copy .env.template .env
   ```

2. Edit `.env` with your Fineract server details:
   ```ini
   FINERACT_BASE_URL=https://your-server:8443/fineract-provider/api/v1
   FINERACT_AUTH_TOKEN=Basic your_auth_token_here
   FINERACT_TENANT_ID=your_tenant_id
   ```

### 4. Run the Tool

```bash
python main.py
```

The tool will start at: **http://localhost:8000**

## 📖 How to Use

### Complete Workflow

1. **Undo Transactions**
   - Enter Loan ID and cutoff date
   - Click "Undo Transactions"
   - Transactions are reversed and saved

2. **Export to Excel**
   - Click "Export Excel"
   - File downloads automatically

3. **Edit Excel**
   - Open the downloaded Excel file
   - Make corrections to dates/amounts
   - Save the file

4. **Import Corrected Excel**
   - Click "Choose Excel file"
   - Select your corrected file
   - Click "Import Excel"

5. **Make Repayments**
   - Click "Make Repayments"
   - Corrected transactions are created in Fineract

## 📁 Session Management

Each undo operation creates a session folder:
```
desktop/
└── session_20251205_100000_loan_19130/
    ├── transactions.json              # Original undo data
    ├── transactions.xlsx              # Exported Excel
    ├── transactions_corrected.xlsx    # Your corrections
    └── replay_results.json            # Replay results
```

All files for one operation are kept together!

## 🔧 Configuration Options

Edit `.env` file to customize:

```ini
# Fineract Connection
FINERACT_BASE_URL=https://your-server:8443/fineract-provider/api/v1
FINERACT_AUTH_TOKEN=Basic <your_token>
FINERACT_TENANT_ID=default

# Date Formats
DATE_FORMAT=dd MMMM yyyy
TIME_FORMAT=dd MMMM yyyy HH:mm:ss
LOCALE=en

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🐛 Troubleshooting

### Tool won't start
- Check Python is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

### Can't connect to Fineract
- Verify `FINERACT_BASE_URL` in `.env`
- Check auth token is correct
- Test with: `python test_api.py`

### Import fails
- Ensure Excel file has correct columns
- Check date format matches Fineract

### Replay fails
- Verify transactions were imported successfully
- Check Fineract server logs for detailed errors

## 📚 Additional Documentation

- `session_flow_explanation.md` - How session folders work
- `file_organization_summary.md` - Project structure
- `test_api.py` - Test Fineract connection

## 🆘 Support

For issues:
1. Check the troubleshooting section
2. Review Fineract server logs
3. Test connection with `python test_api.py`

## 📜 License

[Your License Here]

## 👨‍💻 Version

**Version 1.0.0** - Production Ready
