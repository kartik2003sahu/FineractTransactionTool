"""
FastAPI application for transaction management
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import shutil
from datetime import datetime

from transaction_manager import TransactionManager
from excel_handler import ExcelHandler
from data_storage import DataStorage
from config import Config
from auth_manager import AuthManager

app = FastAPI(title="Transaction Management Tool", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize managers
transaction_manager = TransactionManager()
excel_handler = ExcelHandler()
data_storage = DataStorage()


# Helper function to get latest session folder
def get_latest_session_folder():
    """Get the most recent session folder path"""
    base_dir = os.path.dirname(Config.JSON_STORAGE_PATH)
    
    if not os.path.exists(base_dir):
        return None
    
    session_folders = [
        f for f in os.listdir(base_dir) 
        if f.startswith('session_') and os.path.isdir(os.path.join(base_dir, f))
    ]
    
    if not session_folders:
        return None
    
    # Sort by name (which includes timestamp) to get latest
    session_folders.sort(reverse=True)
    return os.path.join(base_dir, session_folders[0])


# Pydantic models
class LoginRequest(BaseModel):
    server_url: str
    tenant_id: str
    username: str
    password: str


class UndoRequest(BaseModel):
    loan_id: int
    cutoff_date: str


class ReplayRequest(BaseModel):
    pass  # No body needed, will read from uploaded file


# Routes
# Authentication endpoints
@app.post("/api/login")
async def login(request: LoginRequest):
    """
    Authenticate user with Fineract and save credentials
    
    Args:
        request: LoginRequest with server, tenant, username, password
        
    Returns:
        Login success/failure status
    """
    try:
        # Authenticate with Fineract
        success, message, user_data = AuthManager.authenticate(
            request.server_url,
            request.tenant_id,
            request.username,
            request.password
        )
        
        if success:
            # Save credentials to .env
            AuthManager.save_credentials(
                request.server_url,
                request.tenant_id,
                request.username,
                request.password
            )
            
            return {
                "success": True,
                "message": "Login successful! Redirecting to dashboard...",
                "user": user_data.get("username", request.username),
                "tenant": request.tenant_id
            }
        else:
            return {
                "success": False,
                "message": message
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/logout")
async def logout():
    """
    Clear saved credentials (logout)
    
    Returns:
        Logout success
    """
    try:
        AuthManager.clear_credentials()
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/auth-status")
async def get_auth_status():
    """
    Check if user is authenticated
    
    Returns:
        Authentication status
    """
    try:
        is_auth = AuthManager.is_authenticated()
        return {
            "authenticated": is_auth
        }
    except Exception as e:
        return {
            "authenticated": False
        }


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML"""
    html_path = os.path.join("static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Frontend not found. Please create static/index.html</h1>")


@app.post("/api/undo-transactions")
async def undo_transactions(request: UndoRequest):
    """
    Undo transactions for a specific loan up to a cutoff date
    
    Args:
        request: UndoRequest with loan_id and cutoff_date
        
    Returns:
        Summary of undone transactions
    """
    try:
        undone_txns, success_count, failure_count = transaction_manager.undo_transactions_by_date(
            loan_id=request.loan_id,
            cutoff_date=request.cutoff_date
        )
        
        return {
            "success": True,
            "message": f"Processed {len(undone_txns)} transactions",
            "success_count": success_count,
            "failure_count": failure_count,
            "transactions": undone_txns
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export-excel")
async def export_excel():
    """
    Export stored transactions from latest session to Excel file
    
    Returns:
        Excel file download
    """
    try:
        # Get latest session folder
        session_folder = get_latest_session_folder()
        if not session_folder:
            raise HTTPException(status_code=404, detail="No session found. Please run undo operation first.")
        
        # Load transactions from session folder
        session_storage = DataStorage(os.path.join(session_folder, 'transactions.json'))
        transactions = session_storage.load_transactions()
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found to export")
        
        # Export to Excel in session folder
        excel_path = os.path.join(session_folder, 'transactions.xlsx')
        excel_handler.export_to_excel(transactions, excel_path)
        
        print(f"✅ Excel exported to session: {excel_path}")
        
        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=f"transactions_{os.path.basename(session_folder)}.xlsx"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/import-excel")
async def import_excel(file: UploadFile = File(...)):
    """
    Import Excel file with corrected transaction data into latest session
    
    Args:
        file: Uploaded Excel file
        
    Returns:
        Summary of imported data
    """
    try:
        # Get latest session folder
        session_folder = get_latest_session_folder()
        if not session_folder:
            raise HTTPException(status_code=404, detail="No session found. Please run undo operation first.")
        
        # Save uploaded file to session folder (as corrected version)
        excel_path = os.path.join(session_folder, 'transactions_corrected.xlsx')
        
        with open(excel_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Corrected Excel saved to session: {excel_path}")
        
        # Import transactions from corrected Excel
        transactions = excel_handler.import_from_excel(excel_path)
        
        # Validate transactions
        valid_count = sum(1 for txn in transactions if excel_handler.validate_transaction_data(txn))
        
        # Store in session folder for replay
        session_storage = DataStorage(os.path.join(session_folder, 'transactions.json'))
        session_storage.save_transactions(transactions)
        
        return {
            "success": True,
            "message": f"Imported {len(transactions)} transactions to session",
            "total_count": len(transactions),
            "valid_count": valid_count,
            "invalid_count": len(transactions) - valid_count,
            "session_folder": session_folder
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/replay-transactions")
async def replay_transactions():
    """
    Replay transactions from imported Excel file (sorted by date)
    
    Returns:
        Summary of replayed transactions
    """
    try:
        # Get latest session folder
        session_folder = get_latest_session_folder()
        if not session_folder:
            raise HTTPException(status_code=404, detail="No session found. Please run undo operation first.")
        
        # Load transactions from session folder
        session_storage = DataStorage(os.path.join(session_folder, 'transactions.json'))
        transactions = session_storage.load_transactions()
        
        if not transactions:
            raise HTTPException(status_code=404, detail="No transactions found to replay")
        
        # Filter valid transactions
        valid_transactions = [
            txn for txn in transactions 
            if excel_handler.validate_transaction_data(txn)
        ]
        
        if not valid_transactions:
            raise HTTPException(status_code=400, detail="No valid transactions to replay")
        
        # Replay transactions
        success_count, failure_count = transaction_manager.replay_transactions(valid_transactions)
        
        return {
            "success": True,
            "message": f"Replayed {len(valid_transactions)} transactions",
            "success_count": success_count,
            "failure_count": failure_count,
            "total_count": len(valid_transactions)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """
    Get current status of stored transactions
    
    Returns:
        Status information
    """
    try:
        transactions = data_storage.load_transactions()
        
        return {
            "success": True,
            "transaction_count": len(transactions),
            "has_transactions": len(transactions) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)
