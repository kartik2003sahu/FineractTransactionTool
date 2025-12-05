// Transaction Management Tool - Frontend JavaScript

// Utility function to show loading state
function setLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const loader = button.querySelector('.loader');

    if (isLoading) {
        btnText.style.display = 'none';
        loader.style.display = 'block';
        button.disabled = true;
    } else {
        btnText.style.display = 'block';
        loader.style.display = 'none';
        button.disabled = false;
    }
}

// Utility function to show result message
function showResult(elementId, message, type = 'info') {
    const resultDiv = document.getElementById(elementId);
    resultDiv.innerHTML = message;
    resultDiv.className = `result ${type}`;
    resultDiv.style.display = 'block';

    // Auto-hide after 10 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            resultDiv.style.display = 'none';
        }, 10000);
    }
}

// Format date for API (converts from date input to Fineract format with end of day time)
function formatDateForAPI(dateInput) {
    const date = new Date(dateInput);
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];

    const day = String(date.getDate()).padStart(2, '0');
    const month = months[date.getMonth()];
    const year = date.getFullYear();

    // Set time to end of day (23:59:59) to include all transactions on that date
    const hours = '23';
    const minutes = '59';
    const seconds = '59';

    return `${day} ${month} ${year} ${hours}:${minutes}:${seconds}`;
}

// Update status display
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        const statusDisplay = document.getElementById('statusDisplay');

        if (data.has_transactions) {
            statusDisplay.innerHTML = `
                <p><strong>Transaction Count:</strong> ${data.transaction_count}</p>
                <p>✅ Transactions loaded and ready</p>
            `;
        } else {
            statusDisplay.innerHTML = `<p>No transactions loaded</p>`;
        }
    } catch (error) {
        console.error('Error updating status:', error);
    }
}

// Step 1: Undo Transactions
document.getElementById('undoForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const undoBtn = document.getElementById('undoBtn');
    const loanId = parseInt(document.getElementById('loanId').value);
    const cutoffDate = document.getElementById('cutoffDate').value;

    setLoading(undoBtn, true);

    try {
        const formattedDate = formatDateForAPI(cutoffDate);

        const response = await fetch('/api/undo-transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                loan_id: loanId,
                cutoff_date: formattedDate
            })
        });

        const data = await response.json();

        if (response.ok) {
            showResult('undoResult', `
                <strong>✅ Success!</strong><br>
                ${data.message}<br>
                Successful: ${data.success_count} | Failed: ${data.failure_count}
            `, 'success');

            // Update status
            await updateStatus();
        } else {
            showResult('undoResult', `
                <strong>❌ Error:</strong> ${data.detail || 'Unknown error'}
            `, 'error');
        }
    } catch (error) {
        showResult('undoResult', `
            <strong>❌ Error:</strong> ${error.message}
        `, 'error');
    } finally {
        setLoading(undoBtn, false);
    }
});

// Step 2: Export to Excel
document.getElementById('exportBtn').addEventListener('click', async () => {
    const exportBtn = document.getElementById('exportBtn');
    setLoading(exportBtn, true);

    try {
        const response = await fetch('/api/export-excel');

        if (response.ok) {
            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transactions.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            showResult('exportResult', `
                <strong>✅ Success!</strong> Excel file downloaded successfully
            `, 'success');
        } else {
            const data = await response.json();
            showResult('exportResult', `
                <strong>❌ Error:</strong> ${data.detail || 'Export failed'}
            `, 'error');
        }
    } catch (error) {
        showResult('exportResult', `
            <strong>❌ Error:</strong> ${error.message}
        `, 'error');
    } finally {
        setLoading(exportBtn, false);
    }
});

// File input display
document.getElementById('excelFile').addEventListener('change', (e) => {
    const fileName = e.target.files[0]?.name || 'Choose Excel file...';
    document.getElementById('fileName').textContent = fileName;
});

// Step 3: Import Excel
document.getElementById('importForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const importBtn = document.getElementById('importBtn');
    const fileInput = document.getElementById('excelFile');
    const file = fileInput.files[0];

    if (!file) {
        showResult('importResult', `
            <strong>⚠️ Warning:</strong> Please select an Excel file
        `, 'error');
        return;
    }

    setLoading(importBtn, true);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/import-excel', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showResult('importResult', `
                <strong>✅ Success!</strong><br>
                ${data.message}<br>
                Valid: ${data.valid_count} | Invalid: ${data.invalid_count}
            `, 'success');

            // Update status
            await updateStatus();
        } else {
            showResult('importResult', `
                <strong>❌ Error:</strong> ${data.detail || 'Import failed'}
            `, 'error');
        }
    } catch (error) {
        showResult('importResult', `
            <strong>❌ Error:</strong> ${error.message}
        `, 'error');
    } finally {
        setLoading(importBtn, false);
    }
});

// Step 4: Replay Transactions
document.getElementById('replayBtn').addEventListener('click', async () => {
    const replayBtn = document.getElementById('replayBtn');

    // Confirm before replaying
    if (!confirm('Are you sure you want to replay all transactions? This will create new transactions in the system.')) {
        return;
    }

    setLoading(replayBtn, true);

    try {
        const response = await fetch('/api/replay-transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (response.ok) {
            showResult('replayResult', `
                <strong>✅ Success!</strong><br>
                ${data.message}<br>
                Successful: ${data.success_count} | Failed: ${data.failure_count}
            `, 'success');
        } else {
            showResult('replayResult', `
                <strong>❌ Error:</strong> ${data.detail || 'Replay failed'}
            `, 'error');
        }
    } catch (error) {
        showResult('replayResult', `
            <strong>❌ Error:</strong> ${error.message}
        `, 'error');
    } finally {
        setLoading(replayBtn, false);
    }
});


// Check authentication status on page load
fetch('/api/auth-status')
    .then(res => res.json())
    .then(data => {
        if (!data.authenticated) {
            // Redirect to login page
            window.location.href = '/static/login.html';
        }
    })
    .catch(error => {
        console.error('Auth check failed:', error);
    });

// Logout function (globally accessible)
window.logout = function () {
    if (confirm('Are you sure you want to logout? You will need to login again to use the tool.')) {
        fetch('/api/logout', { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/static/login.html';
                }
            })
            .catch(error => {
                console.error('Logout failed:', error);
                alert('Logout failed. Please try again.');
            });
    }
};

// Initialize status on page load
updateStatus();
