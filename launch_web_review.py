#!/usr/bin/env python3
"""
Launch web-based review interface for modern browser-based transaction review
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import webbrowser
import tempfile
import sqlite3

def create_web_interface():
    """Create a modern web interface for transaction review."""
    
    # Load the manual review data
    try:
        manual_df = pd.read_csv("output/gold_standard/manual_review_required.csv")
    except:
        print("❌ No manual review data found")
        return
    
    # Create HTML interface
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Reconciliation Review</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #1976D2;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #1976D2;
            margin-bottom: 10px;
        }
        
        .transactions-container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .transaction-card {
            border-bottom: 1px solid #eee;
            padding: 25px;
            transition: background 0.2s;
        }
        
        .transaction-card:hover {
            background: #f8f9fa;
        }
        
        .transaction-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .transaction-date {
            font-weight: bold;
            color: #1976D2;
        }
        
        .transaction-amount {
            font-size: 1.5em;
            font-weight: bold;
            color: #e53e3e;
        }
        
        .transaction-description {
            font-size: 1.1em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .transaction-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .detail-item {
            display: flex;
            flex-direction: column;
        }
        
        .detail-label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        
        .detail-value {
            font-weight: 500;
        }
        
        .review-section {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        .review-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 2fr;
            gap: 20px;
            align-items: start;
        }
        
        .form-group {
            display: flex;
            flex-direction: column;
        }
        
        .form-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        .form-group select,
        .form-group input,
        .form-group textarea {
            padding: 12px;
            border: 2px solid #e2e8f0;
            border-radius: 6px;
            font-size: 1em;
            transition: border-color 0.2s;
        }
        
        .form-group select:focus,
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #1976D2;
        }
        
        .category-buttons {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .category-btn {
            padding: 10px 20px;
            border: 2px solid #e2e8f0;
            background: white;
            border-radius: 25px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        
        .category-btn:hover {
            background: #f1f5f9;
        }
        
        .category-btn.active {
            background: #1976D2;
            color: white;
            border-color: #1976D2;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #1976D2;
            color: white;
        }
        
        .btn-primary:hover {
            background: #1565C0;
        }
        
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #5a6268;
        }
        
        .progress-bar {
            background: #e2e8f0;
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .progress-fill {
            background: #1976D2;
            height: 100%;
            transition: width 0.3s;
        }
        
        .export-section {
            text-align: center;
            margin-top: 30px;
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        @media (max-width: 768px) {
            .review-grid {
                grid-template-columns: 1fr;
            }
            
            .transaction-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Financial Reconciliation Review</h1>
            <p>Review and approve transactions requiring manual attention</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="total-transactions">""" + str(len(manual_df)) + """</div>
                <div>Total Transactions</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="reviewed-count">0</div>
                <div>Reviewed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="remaining-count">""" + str(len(manual_df)) + """</div>
                <div>Remaining</div>
            </div>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
        </div>
        
        <div class="transactions-container" id="transactions-container">
"""
    
    # Add transactions
    for idx, row in manual_df.iterrows():
        amount = row.get('amount', 0)
        amount_str = f"${abs(float(amount)):,.2f}" if pd.notna(amount) else "Amount Missing"
        
        html_content += f"""
            <div class="transaction-card" data-index="{idx}">
                <div class="transaction-header">
                    <div class="transaction-date">📅 {row.get('date', 'Unknown Date')}</div>
                    <div class="transaction-amount">{amount_str}</div>
                </div>
                
                <div class="transaction-description">
                    {row.get('description', 'No description')}
                </div>
                
                <div class="transaction-details">
                    <div class="detail-item">
                        <div class="detail-label">Payer</div>
                        <div class="detail-value">{row.get('payer', 'Unknown')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Source</div>
                        <div class="detail-value">{row.get('source', 'Unknown')}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Suggested Category</div>
                        <div class="detail-value">{row.get('suggested_category', 'None')}</div>
                    </div>
                </div>
                
                <div class="review-section">
                    <div class="review-grid">
                        <div class="form-group">
                            <label>Category</label>
                            <div class="category-buttons">
                                <div class="category-btn" data-category="expense">Expense</div>
                                <div class="category-btn" data-category="rent">Rent</div>
                                <div class="category-btn" data-category="settlement">Settlement</div>
                                <div class="category-btn" data-category="personal">Personal</div>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Allowed Amount</label>
                            <input type="number" step="0.01" value="{abs(float(amount)) if pd.notna(amount) else 0}" class="allowed-amount">
                            <div style="margin-top: 10px;">
                                <button class="btn btn-secondary" onclick="setAmount(this, 'full')">Full</button>
                                <button class="btn btn-secondary" onclick="setAmount(this, 'half')">Half</button>
                                <button class="btn btn-secondary" onclick="setAmount(this, 'zero')">Zero</button>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label>Notes</label>
                            <textarea rows="3" placeholder="Add any notes about this transaction..." class="notes"></textarea>
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <button class="btn btn-primary" onclick="saveTransaction(this)">✅ Save & Next</button>
                        <button class="btn btn-secondary" onclick="skipTransaction(this)">⏭️ Skip</button>
                    </div>
                </div>
            </div>
        """
    
    html_content += """
        </div>
        
        <div class="export-section">
            <h3>📊 Export Your Decisions</h3>
            <p>When you're done reviewing, export your decisions to continue the reconciliation process.</p>
            <button class="btn btn-primary" onclick="exportDecisions()">📄 Export to CSV</button>
            <button class="btn btn-secondary" onclick="exportToExcel()">📊 Export to Excel</button>
        </div>
    </div>
    
    <script>
        let reviewedCount = 0;
        let totalTransactions = """ + str(len(manual_df)) + """;
        let decisions = {};
        
        // Category button handling
        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('category-btn')) {
                // Remove active class from siblings
                e.target.parentNode.querySelectorAll('.category-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                // Add active class to clicked button
                e.target.classList.add('active');
            }
        });
        
        function setAmount(button, type) {
            const card = button.closest('.transaction-card');
            const amountInput = card.querySelector('.allowed-amount');
            const originalAmount = parseFloat(amountInput.getAttribute('data-original') || amountInput.value);
            
            switch(type) {
                case 'full':
                    amountInput.value = originalAmount.toFixed(2);
                    break;
                case 'half':
                    amountInput.value = (originalAmount / 2).toFixed(2);
                    break;
                case 'zero':
                    amountInput.value = '0.00';
                    break;
            }
        }
        
        function saveTransaction(button) {
            const card = button.closest('.transaction-card');
            const index = card.getAttribute('data-index');
            
            // Get selected category
            const selectedCategory = card.querySelector('.category-btn.active');
            if (!selectedCategory) {
                alert('Please select a category');
                return;
            }
            
            // Get values
            const category = selectedCategory.getAttribute('data-category');
            const allowedAmount = parseFloat(card.querySelector('.allowed-amount').value);
            const notes = card.querySelector('.notes').value;
            
            // Store decision
            decisions[index] = {
                category: category,
                allowed_amount: allowedAmount,
                notes: notes,
                decision: 'APPROVED',
                reviewed_at: new Date().toISOString()
            };
            
            // Mark as reviewed
            card.style.opacity = '0.6';
            card.style.background = '#e8f5e8';
            button.textContent = '✅ Saved';
            button.disabled = true;
            
            reviewedCount++;
            updateProgress();
            
            // Auto-scroll to next transaction
            const nextCard = card.nextElementSibling;
            if (nextCard) {
                nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        function skipTransaction(button) {
            const card = button.closest('.transaction-card');
            card.style.opacity = '0.4';
            card.style.background = '#f5f5f5';
            
            // Auto-scroll to next transaction
            const nextCard = card.nextElementSibling;
            if (nextCard) {
                nextCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
        
        function updateProgress() {
            document.getElementById('reviewed-count').textContent = reviewedCount;
            document.getElementById('remaining-count').textContent = totalTransactions - reviewedCount;
            
            const progress = (reviewedCount / totalTransactions) * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
        }
        
        function exportDecisions() {
            if (Object.keys(decisions).length === 0) {
                alert('No decisions to export. Please review some transactions first.');
                return;
            }
            
            // Convert to CSV
            let csv = 'index,category,allowed_amount,notes,decision,reviewed_at\\n';
            for (const [index, decision] of Object.entries(decisions)) {
                csv += `${index},"${decision.category}",${decision.allowed_amount},"${decision.notes.replace(/"/g, '""')}","${decision.decision}","${decision.reviewed_at}"\\n`;
            }
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `review_decisions_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            alert(`Exported ${Object.keys(decisions).length} decisions to CSV!`);
        }
        
        function exportToExcel() {
            alert('Excel export feature coming soon! For now, use CSV export and open in Excel.');
        }
        
        // Initialize original amounts
        document.querySelectorAll('.allowed-amount').forEach(input => {
            input.setAttribute('data-original', input.value);
        });
        
        // Auto-focus first transaction
        if (document.querySelector('.transaction-card')) {
            document.querySelector('.transaction-card').scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    </script>
</body>
</html>
    """
    
    # Write to temporary file and open
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
    temp_file.write(html_content)
    temp_file.close()
    
    print(f"🌐 Web interface created: {temp_file.name}")
    print("📱 Opening in your default browser...")
    
    # Open in browser
    webbrowser.open(f"file://{temp_file.name}")
    
    return temp_file.name

if __name__ == "__main__":
    create_web_interface()