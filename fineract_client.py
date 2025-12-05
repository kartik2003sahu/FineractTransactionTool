"""
Fineract API Client for transaction operations
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import Config
import urllib3
import time

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def retry_on_network_error(max_retries=5, initial_delay=2, max_delay=30):
    """
    Decorator to retry API calls on network errors with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException) as e:
                    last_exception = e
                    
                    # Check if it's a network-related error
                    error_str = str(e).lower()
                    is_network_error = any(keyword in error_str for keyword in [
                        'connection', 'timeout', 'network', 'unreachable', 
                        'failed to establish', 'connection reset'
                    ])
                    
                    # Don't retry on HTTP errors (400, 403, 500, etc.) - those are server-side
                    if hasattr(e, 'response') and e.response is not None:
                        # This is an HTTP error, not a network error - don't retry
                        raise
                    
                    if is_network_error and attempt < max_retries:
                        print(f"\n⚠️  Network error detected (attempt {attempt + 1}/{max_retries + 1})")
                        print(f"   Error: {str(e)}")
                        print(f"   Waiting {delay} seconds before retry...")
                        time.sleep(delay)
                        
                        # Exponential backoff
                        delay = min(delay * 2, max_delay)
                    else:
                        # Not a network error or max retries reached
                        raise
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


class FineractClient:
    """Client for interacting with Fineract API"""
    
    def __init__(self):
        self.base_url = Config.FINERACT_BASE_URL
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': Config.FINERACT_AUTH_TOKEN,
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json;charset=UTF-8',
            'Expires': '0',
            'Fineract-Platform-TenantId': Config.FINERACT_TENANT_ID,
            'If-Modified-Since': '0',
            'Pragma': 'no-cache'
        }
    
    @retry_on_network_error(max_retries=5, initial_delay=2, max_delay=30)
    def get_loan_details(self, loan_id: int) -> Dict[str, Any]:
        """
        Fetch loan details including all transactions
        
        Args:
            loan_id: The loan ID to fetch
            
        Returns:
            Dict containing loan details and transactions
        """
        # Add associations parameter to fetch transactions
        url = f"{self.base_url}/loans/{loan_id}?associations=all"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                verify=False,  # Disable SSL verification for development
                timeout=30
            )
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            else:
                # Try to get error details from response
                try:
                    error_detail = response.json()
                    error_msg = error_detail.get('defaultUserMessage', response.text)
                except:
                    error_msg = response.text
                
                raise Exception(f"API Error (Status {response.status_code}): {error_msg}")
                
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Connection failed to {url}. Check if Fineract server is running and accessible: {str(e)}")
        except requests.exceptions.Timeout as e:
            raise Exception(f"Request timeout for loan {loan_id}. Server took too long to respond: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch loan details for loan {loan_id}: {str(e)}")
    
    @retry_on_network_error(max_retries=5, initial_delay=2, max_delay=30)
    def undo_transaction(
        self,
        loan_id: int,
        transaction_id: int,
        transaction_amount: float,
        transaction_date: str
    ) -> Dict[str, Any]:
        """
        Undo a specific transaction
        
        Args:
            loan_id: The loan ID
            transaction_id: The transaction ID to undo
            transaction_amount: Amount of the transaction
            transaction_date: Date of the transaction
            
        Returns:
            API response
        """
        url = f"{self.base_url}/loans/{loan_id}/transactions/{transaction_id}?command=undo"
        
        # CRITICAL: Match exactly what Fineract UI sends
        # transactionAmount MUST be 0 to prevent creating reversal transactions
        # timeFormat is required even though we don't use time component
        payload = {
            "transactionDate": transaction_date,
            "transactionAmount": 0,  # Must be 0! Not the actual amount
            "dateFormat": Config.DATE_FORMAT,
            "timeFormat": Config.TIME_FORMAT,
            "locale": Config.LOCALE
        }
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=False,
                timeout=30
            )
            
            # Check for errors and extract actual error message
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('defaultUserMessage', error_data.get('developerMessage', response.text))
                except:
                    error_msg = response.text
                    
                raise Exception(
                    f"Failed to undo transaction {transaction_id}: HTTP {response.status_code} - {error_msg}"
                )
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Failed to undo transaction {transaction_id} for loan {loan_id}: {str(e)}"
            )
    
    @retry_on_network_error(max_retries=5, initial_delay=2, max_delay=30)
    def create_repayment(
        self,
        loan_id: int,
        transaction_amount: float,
        transaction_date: str,
        payment_type_id: int,
        channel_type_id: int,
        npa_amount: float = 0
    ) -> Dict[str, Any]:
        """
        Create a repayment transaction
        
        Args:
            loan_id: The loan ID
            transaction_amount: Amount to repay
            transaction_date: Date of repayment
            payment_type_id: Payment type ID
            channel_type_id: Channel type ID
            npa_amount: NPA amount (default 0)
            
        Returns:
            API response
        """
        url = f"{self.base_url}/loans/{loan_id}/transactions?command=repayment"
        
        payload = {
            "isUseHoldAmount": False,
            "transactionAmount": transaction_amount,
            "npaAmount": npa_amount,
            "transactionDate": transaction_date,
            "dateFormat": Config.DATE_FORMAT,
            "timeFormat": Config.TIME_FORMAT,
            "locale": Config.LOCALE
        }
        
        # Use valid defaults based on UI behavior
        # PaymentTypeId: Use stored value, but default to 8 if 0 or invalid
        # ChannelTypeId: Use stored value, but default to 1 if 0 or invalid
        
        valid_payment_type_id = payment_type_id if payment_type_id and payment_type_id != 0 else 8
        valid_channel_type_id = channel_type_id if channel_type_id and channel_type_id != 0 else 1
        
        payload["paymentTypeId"] = valid_payment_type_id
        payload["channelTypeId"] = valid_channel_type_id
        
        print(f"DEBUG: Using paymentTypeId={valid_payment_type_id}, channelTypeId={valid_channel_type_id}")
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                verify=False,
                timeout=30
            )
            
            # Enhanced error handling like undo
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('defaultUserMessage', error_data.get('developerMessage', response.text))
                except:
                    error_msg = response.text
                    
                raise Exception(
                    f"Failed to create repayment: HTTP {response.status_code} - {error_msg}"
                )
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(
                f"Failed to create repayment for loan {loan_id}: {str(e)}"
            )
