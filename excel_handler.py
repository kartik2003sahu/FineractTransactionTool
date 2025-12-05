"""
Excel file handling for transaction import/export
"""
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from config import Config
import os


class ExcelHandler:
    """Handle Excel import and export operations"""
    
    @staticmethod
    def export_to_excel(transactions: List[Dict[str, Any]], file_path: str = None) -> str:
        """
        Export transactions to Excel file
        
        Args:
            transactions: List of transaction dictionaries
            file_path: Optional output file path
            
        Returns:
            Path to the created Excel file
        """
        if not file_path:
            file_path = Config.EXCEL_EXPORT_PATH
        
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Ensure required columns exist and are in the correct order
        columns = [
            'loan_id',
            'transaction_id',
            'transaction_date',
            'transaction_amount',
            'payment_type_id',
            'channel_type_id'
        ]
        
        # Reorder columns
        df = df[columns]
        
        # Rename columns for better readability
        df.columns = [
            'Loan ID',
            'Transaction ID',
            'Transaction Date',
            'Transaction Amount',
            'Payment Type ID',
            'Channel Type ID'
        ]
        
        # Export to Excel
        df.to_excel(file_path, index=False, engine='openpyxl')
        
        return file_path
    
    @staticmethod
    def import_from_excel(file_path: str) -> List[Dict[str, Any]]:
        """
        Import transactions from Excel file
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            List of transaction dictionaries
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        # Read Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Normalize column names (handle both original and readable names)
        column_mapping = {
            'Loan ID': 'loan_id',
            'Transaction ID': 'transaction_id',
            'Transaction Date': 'transaction_date',
            'Transaction Amount': 'transaction_amount',
            'Payment Type ID': 'payment_type_id',
            'Channel Type ID': 'channel_type_id'
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Validate required columns
        required_columns = [
            'loan_id',
            'transaction_date',
            'transaction_amount',
            'payment_type_id',
            'channel_type_id'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Convert to list of dictionaries
        transactions = df.to_dict('records')
        
        # Clean up NaN values
        for transaction in transactions:
            for key, value in transaction.items():
                if pd.isna(value):
                    transaction[key] = None
        
        return transactions
    
    @staticmethod
    def validate_transaction_data(transaction: Dict[str, Any]) -> bool:
        """
        Validate a single transaction record
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = [
            'loan_id',
            'transaction_date',
            'transaction_amount',
            'payment_type_id',
            'channel_type_id'
        ]
        
        for field in required_fields:
            if field not in transaction or transaction[field] is None:
                return False
        
        # Validate data types
        try:
            int(transaction['loan_id'])
            int(transaction['payment_type_id'])
            int(transaction['channel_type_id'])
            float(transaction['transaction_amount'])
        except (ValueError, TypeError):
            return False
        
        return True
