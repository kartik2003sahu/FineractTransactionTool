"""
JSON data storage handler for transactions
"""
import json
import os
from typing import List, Dict, Any
from datetime import datetime
from config import Config


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%d %B %Y %H:%M:%S")
        return super().default(obj)


class DataStorage:
    """Handle JSON file operations for transaction data"""
    
    def __init__(self, file_path: str = None):
        self.file_path = file_path or Config.JSON_STORAGE_PATH
        self._ensure_directory()
    
    def _ensure_directory(self):
        """Ensure the data directory exists"""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
    
    def save_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """
        Save transactions to JSON file
        
        Args:
            transactions: List of transaction dictionaries
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "transactions": transactions
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
    
    def load_transactions(self) -> List[Dict[str, Any]]:
        """
        Load transactions from JSON file
        
        Returns:
            List of transaction dictionaries
        """
        if not os.path.exists(self.file_path):
            return []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('transactions', [])
        except json.JSONDecodeError:
            return []
    
    def clear_transactions(self) -> None:
        """Clear all stored transactions"""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
    
    def append_transaction(self, transaction: Dict[str, Any]) -> None:
        """
        Append a single transaction to existing data
        
        Args:
            transaction: Transaction dictionary
        """
        transactions = self.load_transactions()
        transactions.append(transaction)
        self.save_transactions(transactions)
    
    def get_transaction_count(self) -> int:
        """
        Get the number of stored transactions
        
        Returns:
            Count of transactions
        """
        return len(self.load_transactions())
