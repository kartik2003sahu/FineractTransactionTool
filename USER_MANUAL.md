# User Manual - Fineract Transaction Management Tool

## 📖 Table of Contents
1. [Getting Started](#getting-started)
2. [Understanding the Interface](#understanding-the-interface)
3. [Complete Walkthrough](#complete-walkthrough)
4. [Common Scenarios](#common-scenarios)
5. [Tips & Best Practices](#tips--best-practices)
6. [FAQ](#faq)

---

## Getting Started

### What This Tool Does
This tool helps you manage Fineract loan transactions by allowing you to:
- **Undo** multiple transactions at once
- **Export** transaction data to Excel for editing
- **Correct** wrong dates, amounts, or other details
- **Replay** the corrected transactions back to Fineract

### When to Use This Tool
- Wrong transaction dates were entered
- Multiple transactions need correction
- Payment amounts need adjustment
- You need to redo a series of transactions

---

## Understanding the Interface

The tool has 4 main sections (steps):

### Step 1: Undo Transactions
**Purpose:** Remove incorrect transactions from Fineract

**Inputs:**
- **Loan ID**: The Fineract loan account number
- **Cutoff Date**: Undo all transactions from this date forward

**Example:** If you enter `2024-02-15`, all transactions from Feb 15 onwards will be undone.

### Step 2: Export Excel
**Purpose:** Download transaction data for editing

**Action:** Click "Export Excel" button
**Result:** Downloads `transactions_session_xxx.xlsx` file

### Step 3: Import Corrected Excel
**Purpose:** Upload your corrected transaction data

**Action:** 
1. Click "Choose Excel file"
2. Select your edited file
3. Click "Import Excel"

### Step 4: Make Repayments
**Purpose:** Create the corrected transactions in Fineract

**Action:** Click "Make Repayments"
**Result:** All corrected transactions are created

---

## Complete Walkthrough

### Scenario: Fix Wrong Transaction Dates for Loan 19130

#### Step 1: Undo the Wrong Transactions

1. Open browser to `http://localhost:8000`
2. In **Step 1**, enter:
   - Loan ID: `19130`
   - Cutoff Date: `2024-02-15`
3. Click **Undo Transactions**
4. Wait for success message
   - Should show: "Processed X transactions - Success: X | Failed: 0"

**What happened:**
- Created folder: `desktop/session_20251205_100000_loan_19130/`
- All transactions after Feb 15 are now undone

#### Step 2: Export to Excel

1. Scroll to **Step 2**
2. Click **Export Excel**
3. File downloads automatically

**File location:** Your Downloads folder

#### Step 3: Edit in Excel

1. Open the downloaded Excel file
2. You'll see columns:
   - Loan ID
   - Transaction ID
   - Transaction Date
   - Transaction Amount
   - Payment Type ID
   - Channel Type ID

3. Edit the **Transaction Date** column:
   - Change from: `15 February 2024 00:00:00`
   - Change to: `16 February 2024 00:00:00`

4. Save the file (keep the same name)

#### Step 4: Import Corrected Excel

1. Return to browser
2. In **Step 3**, click **Choose Excel file**
3. Select your edited file
4. Click **Import Excel**
5. Wait for success message
   - Should show: "Imported X transactions to session"

#### Step 5: Make Repayments

1. Scroll to **Step 4**
2. Click **Make Repayments**
3. Watch the progress
4. Success message shows:
   - "Replayed X transactions"
   - "Success: X | Failed: 0"

**Done!** Transactions are now in Fineract with correct dates.

---

## Common Scenarios

### Scenario 1: Change Multiple Transaction Dates

**Use when:** All transactions for a loan have wrong dates

1. Undo all transactions (use oldest date as cutoff)
2. Export Excel
3. Edit ALL date entries
4. Import and replay

### Scenario 2: Fix One Specific Transaction

**Use when:** Only one transaction needs fixing

1. Undo from that transaction's date
2. Export Excel
3. Edit just that row
4. Import and replay

### Scenario 3: Adjust Payment Amounts

**Use when:** Wrong amounts were entered

1. Undo transactions
2. Export Excel
3. Edit **Transaction Amount** column
4. Import and replay

---

## Tips & Best Practices

### ✅ Do's

1. **Always verify dates** before importing
2. **Keep original Excel** as backup
3. **Check session folder** for complete audit trail
4. **Test with one loan** first if unsure
5. **Verify in Fineract UI** after replay

### ❌ Don'ts

1. **Don't skip export step** - always edit through Excel
2. **Don't change Loan ID** in Excel
3. **Don't delete rows** - Excel must have same number of transactions
4. **Don't run multiple undos** simultaneously
5. **Don't close browser** during operations

### 📝 Important Notes

- **Session Folders**: Each undo creates a new session
- **Date Format**: Keep format as `DD Month YYYY HH:MM:SS`
- **Backup**: Session folders keep all your work
- **Network**: Tool retries automatically if connection drops

---

## FAQ

### Q: Can I undo transactions for multiple loans at once?
**A:** No, process one loan at a time. Each gets its own session.

### Q: What happens if I make a mistake in Excel?
**A:** Just export again and start over. Original data is in the session folder.

### Q: Can I revert an undo operation?
**A:** Yes! The old transactions are saved in the session folder. You can use that data to replay them.

### Q: How do I know which session folder to use?
**A:** The tool automatically uses the latest session. Folder names include timestamps.

### Q: What if some repayments fail?
**A:** Check `replay_results.json` in the session folder for error details. You can import and retry just the failed ones.

### Q: Can I edit other fields besides date and amount?
**A:** Currently, the tool supports editing:
- Transaction Date
- Transaction Amount
- Payment Type ID
- Channel Type ID

### Q: Is my data safe?
**A:** Yes! All operations are saved in session folders. Nothing is permanently deleted.

### Q: Can I use this tool on a different computer?
**A:** Yes! Just copy the TransactionTool folder and set up .env with credentials.

---

## Getting Help

If you encounter issues:

1. **Check the README** - Setup instructions
2. **Test connection** - Run `python test_api.py`
3. **Review session folder** - Check for error details
4. **Check Fineract logs** - Server-side errors appear there

---

## Summary

**Remember the simple workflow:**
1. Undo → Export → Edit → Import → Replay
2. Each step builds on the previous one
3. Everything is saved in session folders
4. You can always go back and review your work

**Happy transaction managing!** 🎯
