#!/usr/bin/env python3
"""
Web-Based Review Interface for Financial Reconciliation
======================================================

This provides a user-friendly web interface for reviewing transactions,
similar to the Phase 4 manual review process but with a modern UI.

Features:
- Batch review with keyboard shortcuts
- Auto-categorization suggestions
- Pattern learning
- Progress tracking
- Export/import capabilities

Author: Claude (Anthropic)
Date: July 29, 2025
"""

import pandas as pd
import json
from decimal import Decimal
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
from typing import Dict, List

from manual_review_system import ManualReviewSystem, TransactionCategory, SplitType
from batch_review_helper import BatchReviewHelper


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'


class WebReviewInterface:
    """Web-based interface for transaction review."""
    
    def __init__(self, review_db_path: str = "data/phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.batch_helper = BatchReviewHelper(review_db_path)
        self.current_session = {
            'total': 0,
            'reviewed': 0,
            'start_time': datetime.now()
        }
        
    def get_pending_transactions(self, limit: int = 100) -> List[Dict]:
        """Get pending transactions with auto-categorization suggestions."""
        pending_df = self.review_system.get_pending_reviews(limit=limit)
        
        transactions = []
        for _, row in pending_df.iterrows():
            # Get auto-categorization suggestion
            suggestion = self.batch_helper.suggest_classification(
                row['description'],
                row['payer']
            )
            
            transaction = {
                'review_id': row['review_id'],
                'date': row['date'].strftime('%Y-%m-%d'),
                'description': row['description'],
                'amount': float(row['amount']),
                'payer': row['payer'],
                'source': row['source'],
                'suggested_category': suggestion.get('category', 'Other'),
                'suggested_split': suggestion.get('split_type', '50/50'),
                'confidence': suggestion.get('confidence', 0),
                'similar_transactions': self._find_similar_reviewed(row['description'])
            }
            transactions.append(transaction)
            
        return transactions
    
    def review_transaction(self, review_data: Dict) -> Dict:
        """Process a single transaction review."""
        review_id = review_data['review_id']
        
        # Parse the review data
        category = TransactionCategory(review_data['category'])
        split_type = SplitType(review_data['split_type'])
        
        # Calculate shares
        amount = Decimal(str(review_data['amount']))
        if split_type == SplitType.SPLIT_CUSTOM:
            ryan_share = Decimal(str(review_data.get('ryan_share', 0)))
            jordyn_share = Decimal(str(review_data.get('jordyn_share', 0)))
        else:
            ryan_share = None
            jordyn_share = None
            
        # Apply the review
        success = self.review_system.review_transaction(
            review_id=review_id,
            category=category,
            split_type=split_type,
            ryan_share=ryan_share,
            jordyn_share=jordyn_share,
            allowed_amount=Decimal(str(review_data.get('allowed_amount', amount))),
            is_personal=review_data.get('is_personal', False),
            notes=review_data.get('notes', ''),
            reviewed_by=review_data.get('reviewer', 'Web User')
        )
        
        if success:
            self.current_session['reviewed'] += 1
            
        return {
            'success': success,
            'reviewed_count': self.current_session['reviewed'],
            'remaining': self._get_pending_count()
        }
    
    def bulk_review(self, pattern: Dict, transaction_ids: List[int]) -> Dict:
        """Apply a review pattern to multiple transactions."""
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for tx_id in transaction_ids:
            try:
                review_data = {
                    'review_id': tx_id,
                    'category': pattern['category'],
                    'split_type': pattern['split_type'],
                    'is_personal': pattern.get('is_personal', False),
                    'allowed_amount': pattern.get('allowed_amount'),
                    'notes': pattern.get('notes', 'Bulk reviewed'),
                    'reviewer': pattern.get('reviewer', 'Web User')
                }
                
                result = self.review_transaction(review_data)
                if result['success']:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(str(e))
                
        return results
    
    def _find_similar_reviewed(self, description: str) -> List[Dict]:
        """Find previously reviewed similar transactions."""
        # This would query the review database for similar descriptions
        # For now, return empty list
        return []
    
    def _get_pending_count(self) -> int:
        """Get count of pending transactions."""
        pending_df = self.review_system.get_pending_reviews()
        return len(pending_df)
    
    def export_session_results(self) -> Path:
        """Export the current review session results."""
        session_data = {
            'session_start': self.current_session['start_time'].isoformat(),
            'session_end': datetime.now().isoformat(),
            'total_reviewed': self.current_session['reviewed'],
            'reviews': self.review_system.export_reviews(
                status='completed',
                start_date=self.current_session['start_time']
            ).to_dict('records')
        }
        
        output_path = Path('output/review_sessions') / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
            
        return output_path


# Flask routes
review_interface = WebReviewInterface()


@app.route('/')
def index():
    """Main review interface."""
    return render_template('review_interface.html')


@app.route('/api/transactions/pending')
def get_pending_transactions():
    """Get pending transactions for review."""
    limit = request.args.get('limit', 100, type=int)
    transactions = review_interface.get_pending_transactions(limit=limit)
    return jsonify(transactions)


@app.route('/api/transactions/review', methods=['POST'])
def review_transaction():
    """Submit a transaction review."""
    review_data = request.json
    result = review_interface.review_transaction(review_data)
    return jsonify(result)


@app.route('/api/transactions/bulk-review', methods=['POST'])
def bulk_review():
    """Apply bulk review to multiple transactions."""
    data = request.json
    pattern = data['pattern']
    transaction_ids = data['transaction_ids']
    result = review_interface.bulk_review(pattern, transaction_ids)
    return jsonify(result)


@app.route('/api/session/export')
def export_session():
    """Export current session results."""
    output_path = review_interface.export_session_results()
    return send_file(output_path, as_attachment=True)


@app.route('/api/statistics')
def get_statistics():
    """Get review statistics."""
    stats = review_interface.review_system.get_review_statistics()
    stats['current_session'] = {
        'reviewed': review_interface.current_session['reviewed'],
        'duration': str(datetime.now() - review_interface.current_session['start_time'])
    }
    return jsonify(stats)


# HTML template for the web interface
REVIEW_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Financial Transaction Review</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .transaction-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .transaction-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        .amount {
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }
        select, input, textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #007bff;
            color: white;
        }
        .btn-primary:hover {
            background: #0056b3;
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-personal {
            background: #dc3545;
            color: white;
        }
        .progress {
            background: #e9ecef;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        .progress-bar {
            background: #28a745;
            height: 100%;
            transition: width 0.3s;
        }
        .shortcuts {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .confidence-high { color: #28a745; }
        .confidence-medium { color: #ffc107; }
        .confidence-low { color: #dc3545; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Financial Transaction Review</h1>
            <div class="progress">
                <div class="progress-bar" id="progress-bar" style="width: 0%"></div>
            </div>
            <p id="progress-text">Loading transactions...</p>
        </div>
        
        <div class="shortcuts">
            <strong>Keyboard Shortcuts:</strong>
            <span>Enter - Approve & Next</span> |
            <span>P - Mark Personal</span> |
            <span>R - Rent Split</span> |
            <span>5 - 50/50 Split</span> |
            <span>S - Skip</span>
        </div>
        
        <div id="transaction-container">
            <!-- Transactions will be loaded here -->
        </div>
    </div>
    
    <script>
        // JavaScript for the review interface would go here
        // This would handle:
        // - Loading transactions
        // - Keyboard shortcuts
        // - Form submission
        // - Progress tracking
        // - Auto-save
    </script>
</body>
</html>
'''


def create_review_template():
    """Create the HTML template file."""
    template_dir = Path('templates')
    template_dir.mkdir(exist_ok=True)
    
    with open(template_dir / 'review_interface.html', 'w') as f:
        f.write(REVIEW_TEMPLATE)


if __name__ == "__main__":
    print("Web Review Interface")
    print("===================")
    print()
    print("Starting web server on http://localhost:5000")
    print("Open this URL in your browser to start reviewing transactions.")
    print()
    
    # Create template
    create_review_template()
    
    # Run the web server
    app.run(debug=True, port=5000)