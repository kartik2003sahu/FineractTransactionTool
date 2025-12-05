"""
Transaction management logic for undo and replay operations
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
from fineract_client import FineractClient
from data_storage import DataStorage, DateTimeEncoder
import re


class TransactionManager:
    """Manage transaction undo and replay operations"""
    
    def __init__(self):
        self.client = FineractClient()
        self.storage = DataStorage()
    
    def parse_date_string(self, date_str: str) -> datetime:
        """
        Parse date string from Fineract API format
        
        Args:
            date_str: Date string (e.g., "04 December 2025 15:37:46" or array format)
            
        Returns:
            datetime object
        """
        if isinstance(date_str, list):
            # Handle array format [year, month, day, hour, minute, second]
            return datetime(*date_str[:6])
        elif isinstance(date_str, str):
            # Handle string format
            try:
                return datetime.strptime(date_str, "%d %B %Y %H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%d %B %Y")
                except ValueError:
                    # Try other common formats
                    for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"]:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                    raise ValueError(f"Unable to parse date: {date_str}")
        else:
            raise ValueError(f"Unexpected date format: {type(date_str)}")
    
    def format_date_for_api(self, dt: datetime) -> str:
        """
        Format datetime object for Fineract API
        
        Args:
            dt: datetime object
            
        Returns:
            Formatted date string
        """
        return dt.strftime("%d %B %Y %H:%M:%S")
    
    def undo_transactions_by_date(
        self,
        loan_id: int,
        cutoff_date: str
    ) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        Undo transactions by identifying target IDs first, then undoing them iteratively
        
        CRITICAL LOGIC:
        1. Create a session folder for this operation
        2. Fetch loan ONCE and identify which transaction IDs to undo (based on cutoff date)
        3. Iteratively undo transactions by tracking IDs, not dates
        4. Dates may change after each undo (Fineract recalculates), but IDs remain stable
        
        Args:
            loan_id: The loan ID
            cutoff_date: Cutoff date - identify transactions >= this date to undo
            
        Returns:
            Tuple of (undone_transactions, success_count, failure_count)
        """
        # Create a unique session folder for this operation
        from datetime import datetime
        import os
        
        session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_folder = os.path.join(
            os.path.dirname(self.storage.file_path),
            f"session_{session_timestamp}_loan_{loan_id}"
        )
        os.makedirs(session_folder, exist_ok=True)
        
        # Update storage path to use session folder
        session_storage = DataStorage(os.path.join(session_folder, 'transactions.json'))
        
        print(f"\n{'='*60}")
        print(f"NEW SESSION CREATED: {session_folder}")
        print(f"{'='*60}\n")
        
        # Parse cutoff date
        try:
            cutoff_dt = self.parse_date_string(cutoff_date)
        except Exception as e:
            raise Exception(f"Failed to parse cutoff date '{cutoff_date}': {e}")
        
        print(f"DEBUG: Cutoff date: {cutoff_dt}")
        
        # STEP 1: Fetch loan details ONCE and identify target transaction IDs
        try:
            loan_details = self.client.get_loan_details(loan_id)
        except Exception as e:
            raise Exception(f"Failed to fetch loan: {e}")
        
        transactions = loan_details.get('transactions', [])
        print(f"DEBUG: Found {len(transactions)} total transactions")
        
        # Identify which transaction IDs need to be undone
        target_txn_ids = []
        
        for txn in transactions:
            # Check type
            txn_type = txn.get('type', {})
            type_code = txn_type.get('code', '') if isinstance(txn_type, dict) else ''
            type_value = txn_type.get('value', '') if isinstance(txn_type, dict) else ''
            
            if type_code != 'loanTransactionType.repayment' or type_value != 'Repayment':
                continue
            
            # Check not already reversed
            if txn.get('manuallyReversed', False):
                continue
            
            # Parse date
            txn_date_raw = txn.get('date')
            if not txn_date_raw:
                continue
                
            try:
                txn_date = self.parse_date_string(txn_date_raw)
            except:
                continue
            
            # Include if >= cutoff date
            # Compare only date parts to ensure transactions ON the cutoff date are included
            # regardless of time component
            if txn_date.date() >= cutoff_dt.date():
                target_txn_ids.append(txn.get('id'))
                print(f"DEBUG: Transaction {txn.get('id')} will be undone (date: {txn_date.date()})")
        
        print(f"DEBUG: Identified {len(target_txn_ids)} transaction IDs to undo")
        print(f"DEBUG: Target IDs: {target_txn_ids}")
        
        # STEP 2: Iteratively undo each target transaction
        undone_transactions = []
        success_count = 0
        failure_count = 0
        remaining_ids = set(target_txn_ids)
        
        while remaining_ids:
            iteration = len(target_txn_ids) - len(remaining_ids) + 1
            print(f"\n--- Iteration {iteration}/{len(target_txn_ids)} ---")
            print(f"DEBUG: Remaining IDs to undo: {remaining_ids}")
            
            # Re-fetch to get current state (dates may have changed!)
            try:
                loan_details = self.client.get_loan_details(loan_id)
            except Exception as e:
                print(f"ERROR: Failed to fetch loan: {e}")
                break
            
            transactions = loan_details.get('transactions', [])
            
            # Find the LATEST transaction that's in our remaining_ids set
            latest_target_txn = None
            latest_date = None
            
            for txn in transactions:
                txn_id = txn.get('id')
                
                # Skip if not in our target list
                if txn_id not in remaining_ids:
                    continue
                
                # Parse date
                txn_date_raw = txn.get('date')
                if not txn_date_raw:
                    continue
                    
                try:
                    txn_date = self.parse_date_string(txn_date_raw)
                except:
                    continue
                
                # Update if this is the latest so far
                if latest_target_txn is None:
                    latest_target_txn = txn
                    latest_date = txn_date
                elif txn_date > latest_date:
                    latest_target_txn = txn
                    latest_date = txn_date
                elif txn_date == latest_date and txn_id > latest_target_txn.get('id'):
                    latest_target_txn = txn
            
            # If we can't find any remaining target transaction, something's wrong
            if latest_target_txn is None:
                print(f"ERROR: Could not find any remaining target transactions!")
                break
            
            # Undo this transaction
            txn_id = latest_target_txn['id']
            txn_amount = latest_target_txn.get('amount', 0)
            txn_date = latest_date
            
            print(f"DEBUG: Undoing transaction {txn_id} (current date: {txn_date})")
            
            try:
                # Undo it
                self.client.undo_transaction(
                    loan_id=loan_id,
                    transaction_id=txn_id,
                    transaction_amount=txn_amount,
                    transaction_date=self.format_date_for_api(txn_date)
                )
                
                # Store details
                undone_txn = {
                    'loan_id': loan_id,
                    'transaction_id': txn_id,
                    'transaction_date': self.format_date_for_api(txn_date),
                    'transaction_amount': txn_amount,
                    'payment_type_id': latest_target_txn.get('paymentDetailData', {}).get('paymentType', {}).get('id', 0),
                    'channel_type_id': latest_target_txn.get('paymentDetailData', {}).get('channelType', {}).get('id', 0),
                    'status': 'undone'
                }
                
                undone_transactions.append(undone_txn)
                success_count += 1
                remaining_ids.remove(txn_id)
                
                print(f"✅ Successfully undone transaction {txn_id} ({len(remaining_ids)} remaining)")
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Failed to undo transaction {txn_id}: {error_msg}")
                
                # Store failure
                failed_txn = {
                    'loan_id': loan_id,
                    'transaction_id': txn_id,
                    'transaction_date': self.format_date_for_api(txn_date),
                    'transaction_amount': txn_amount,
                    'payment_type_id': latest_target_txn.get('paymentDetailData', {}).get('paymentType', {}).get('id', 0),
                    'channel_type_id': latest_target_txn.get('paymentDetailData', {}).get('channelType', {}).get('id', 0),
                    'status': 'failed',
                    'error': error_msg
                }
                
                undone_transactions.append(failed_txn)
                failure_count += 1
                remaining_ids.remove(txn_id)
                
                # Continue trying other transactions even if one fails
                print(f"DEBUG: Continuing with remaining {len(remaining_ids)} transactions")
        
        print(f"\n=== UNDO COMPLETE ===")
        print(f"Success: {success_count} | Failed: {failure_count}")
        print(f"Session folder: {session_folder}")
        
        # Save to session storage
        session_storage.save_transactions(undone_transactions)
        
        return undone_transactions, success_count, failure_count
    
    def replay_transactions(self, transactions: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Replay transactions sorted by date
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Tuple of (success_count, failure_count)
        """
        # Create session folder for replay
        from datetime import datetime
        import os
        
        # Try to use the most recent session folder, or create a new one
        base_dir = os.path.dirname(self.storage.file_path)
        session_folders = [f for f in os.listdir(base_dir) if f.startswith('session_') and os.path.isdir(os.path.join(base_dir, f))]
        
        if session_folders:
            # Use the most recent session folder
            session_folders.sort(reverse=True)
            session_folder = os.path.join(base_dir, session_folders[0])
            print(f"\nUsing existing session folder: {session_folder}")
        else:
            # Create new session folder
            session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_folder = os.path.join(base_dir, f"session_{session_timestamp}_replay")
            os.makedirs(session_folder, exist_ok=True)
            print(f"\nCreated new session folder: {session_folder}")
        
        # Sort transactions by date
        sorted_transactions = sorted(
            transactions,
            key=lambda x: self.parse_date_string(x['transaction_date'])
        )
        
        print(f"\nDEBUG: Starting replay of {len(sorted_transactions)} transactions")
        
        success_count = 0
        failure_count = 0
        replayed_transactions = []
        
        for i, txn in enumerate(sorted_transactions, 1):
            try:
                print(f"\nDEBUG: Replaying {i}/{len(sorted_transactions)}: Transaction {txn.get('transaction_id')}, Date: {txn.get('transaction_date')}, Amount: {txn.get('transaction_amount')}")
                
                response = self.client.create_repayment(
                    loan_id=int(txn['loan_id']),
                    transaction_amount=float(txn['transaction_amount']),
                    transaction_date=txn['transaction_date'],
                    payment_type_id=int(txn['payment_type_id']),
                    channel_type_id=int(txn['channel_type_id'])
                )
                
                # Save successful replay
                replayed_txn = txn.copy()
                replayed_txn['replay_status'] = 'success'
                replayed_txn['new_transaction_id'] = response.get('resourceId')
                replayed_transactions.append(replayed_txn)
                
                success_count += 1
                print(f"✅ Successfully replayed transaction {txn.get('transaction_id')}")
                
            except Exception as e:
                # Save failed replay with error
                replayed_txn = txn.copy()
                replayed_txn['replay_status'] = 'failed'
                replayed_txn['replay_error'] = str(e)
                replayed_transactions.append(replayed_txn)
                
                failure_count += 1
                print(f"❌ REPLAY FAILED for transaction {txn.get('transaction_id')}: {str(e)}")
        
        print(f"\n=== REPLAY COMPLETE ===")
        print(f"Success: {success_count} | Failed: {failure_count}")
        
        # Save replay results to a SEPARATE JSON file to preserve undo history
        from datetime import datetime
        replay_data = {
            "timestamp": datetime.now().isoformat(),
            "replay_results": replayed_transactions,
            "summary": {
                "total": len(replayed_transactions),
                "successful": success_count,
                "failed": failure_count
            }
        }
        
        # Save to replay_results.json instead of overwriting transactions.json
        import os
        replay_file = os.path.join(session_folder, 'replay_results.json')
        
        import json
        with open(replay_file, 'w', encoding='utf-8') as f:
            json.dump(replay_data, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)
        
        print(f"Replay results saved to: {replay_file}")
        print(f"Session folder: {session_folder}")
        
        return success_count, failure_count
