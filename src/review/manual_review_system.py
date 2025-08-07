#!/usr/bin/env python3
"""
Manual Review System for Financial Transactions
==============================================

This system provides a structured approach for manually reviewing and
classifying transactions that cannot be automatically categorized.

Key Features:
- Interactive review interface
- Persistent review database
- Review history and audit trail
- Bulk review capabilities
- Pattern learning for future automation

Author: Claude (Anthropic)
Date: July 29, 2025
Version: 1.0.0
"""

import sqlite3
import pandas as pd
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import hashlib
from enum import Enum


class ReviewStatus(Enum):
    """Status of manual review."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    DEFERRED = "deferred"


class TransactionCategory(Enum):
    """Standard transaction categories."""
    RENT = "rent"
    UTILITIES = "utilities"
    GROCERIES = "groceries"
    DINING = "dining"
    TRANSPORTATION = "transportation"
    ENTERTAINMENT = "entertainment"
    HEALTHCARE = "healthcare"
    SHOPPING = "shopping"
    PERSONAL_RYAN = "personal_ryan"
    PERSONAL_JORDYN = "personal_jordyn"
    INCOME_RYAN = "income_ryan"
    INCOME_JORDYN = "income_jordyn"
    SETTLEMENT = "settlement"
    OTHER = "other"


class SplitType(Enum):
    """How to split the expense."""
    SPLIT_50_50 = "split_50_50"
    SPLIT_CUSTOM = "split_custom"
    RYAN_FULL = "ryan_full"
    JORDYN_FULL = "jordyn_full"
    RENT_SPLIT = "rent_split"  # 47% Ryan, 53% Jordyn


class InteractiveReviewer:
    """Interactive command-line reviewer for transactions."""
    
    def __init__(self, review_system: 'ManualReviewSystem'):
        self.review_system = review_system
        self.current_index = 0
        self.pending_reviews = []
        
    def run(self):
        """Run the interactive review interface."""
        # For non-interactive environments, use spreadsheet export instead
        print("\nInteractive terminal review is not recommended for large datasets.")
        print("Instead, we'll export to a spreadsheet for efficient bulk review.")
        print()
        print("Options:")
        print("1. Export to spreadsheet for review")
        print("2. Use web interface (if available)")
        print("3. Skip review (use defaults)")
        print()
        
        # Auto-select option 3 for non-interactive environments
        if not self._is_interactive():
            print("Auto-selecting option 3: Skip review (use defaults)")
            self._apply_default_reviews()
            return
            
        choice = input("Select option (1-3): ").strip()
        
        if choice == "1":
            self._export_for_spreadsheet_review()
        elif choice == "2":
            self._launch_web_interface()
        else:
            self._apply_default_reviews()
    
    def _is_interactive(self):
        """Check if running in interactive mode."""
        import sys
        return sys.stdin.isatty()
    
    def _export_for_spreadsheet_review(self):
        """Export transactions for spreadsheet review."""
        from src.review.spreadsheet_review_system import SpreadsheetReviewSystem
        
        pending_df = self.review_system.get_pending_reviews()
        if pending_df.empty:
            print("No transactions to review!")
            return
            
        review_system = SpreadsheetReviewSystem()
        output_path = review_system.export_for_review(pending_df)
        
        print(f"\nExported {len(pending_df)} transactions to: {output_path}")
        print("\nNext steps:")
        print("1. Open the file in Excel or Google Sheets")
        print("2. Review and update the Allowed Amount, Category, etc.")
        print("3. Save the file")
        print("4. Run: python spreadsheet_review_system.py")
        print("   and select option 2 to import your reviews")
    
    def _launch_web_interface(self):
        """Launch the web-based review interface."""
        print("\nTo use the web interface:")
        print("1. Run: python web_review_interface.py")
        print("2. Open http://localhost:5000 in your browser")
        print("3. Review transactions with the user-friendly interface")
    
    def _apply_default_reviews(self):
        """Apply default 50/50 split to all pending transactions."""
        pending_df = self.review_system.get_pending_reviews()
        
        for _, row in pending_df.iterrows():
            self.review_system.review_transaction(
                review_id=row['review_id'],
                category=TransactionCategory.OTHER,
                split_type=SplitType.SPLIT_50_50,
                notes="Auto-reviewed with default 50/50 split",
                reviewed_by="System Default"
            )
        
        print(f"\nApplied default 50/50 split to {len(pending_df)} transactions")


class ManualReviewSystem:
    """
    System for managing manual review of financial transactions.
    """
    
    def __init__(self, db_path: str = "manual_reviews.db"):
        """Initialize the review system with database."""
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize the database schema."""
        import os
        # Ensure the database directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transaction_reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_hash TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                payer TEXT NOT NULL,
                source TEXT,
                
                -- Review fields
                status TEXT NOT NULL DEFAULT 'pending',
                category TEXT,
                split_type TEXT,
                ryan_share REAL,
                jordyn_share REAL,
                allowed_amount REAL,
                is_personal INTEGER DEFAULT 0,
                notes TEXT,
                
                -- Audit fields
                reviewed_by TEXT,
                reviewed_date TEXT,
                created_date TEXT NOT NULL,
                updated_date TEXT
            )
        """)
        
        # Review history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_history (
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                review_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                changed_by TEXT,
                changed_date TEXT NOT NULL,
                FOREIGN KEY (review_id) REFERENCES transaction_reviews(review_id)
            )
        """)
        
        # Pattern learning table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learned_patterns (
                pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_value TEXT NOT NULL,
                category TEXT NOT NULL,
                split_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                occurrence_count INTEGER DEFAULT 1,
                created_date TEXT NOT NULL,
                last_seen_date TEXT NOT NULL
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON transaction_reviews(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_date 
            ON transaction_reviews(date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_category 
            ON transaction_reviews(category)
        """)
        
        conn.commit()
        conn.close()
    
    def add_transaction_for_review(self, date: datetime, description: str,
                                   amount: Decimal, payer: str,
                                   source: Optional[str] = None) -> int:
        """Add a transaction for manual review."""
        # Generate unique hash for transaction
        tx_hash = self._generate_transaction_hash(date, description, amount, payer)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO transaction_reviews 
                (transaction_hash, date, description, amount, payer, source, 
                 status, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tx_hash,
                date.isoformat() if isinstance(date, datetime) else str(date),
                description,
                str(amount),  # Store as string to preserve Decimal precision
                payer,
                source,
                ReviewStatus.PENDING.value,
                datetime.now().isoformat()
            ))
            
            review_id = cursor.lastrowid
            conn.commit()
            
            return review_id
            
        except sqlite3.IntegrityError:
            # Transaction already exists
            cursor.execute("""
                SELECT review_id FROM transaction_reviews 
                WHERE transaction_hash = ?
            """, (tx_hash,))
            return cursor.fetchone()[0]
            
        finally:
            conn.close()
    
    def review_transaction(self, review_id: int, category: TransactionCategory,
                          split_type: SplitType, ryan_share: Optional[Decimal] = None,
                          jordyn_share: Optional[Decimal] = None,
                          allowed_amount: Optional[Decimal] = None,
                          is_personal: bool = False, notes: Optional[str] = None,
                          reviewed_by: str = "User") -> bool:
        """Review and classify a transaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current values for history
        cursor.execute("""
            SELECT * FROM transaction_reviews WHERE review_id = ?
        """, (review_id,))
        current = cursor.fetchone()
        
        if not current:
            conn.close()
            return False
        
        # Calculate shares based on split type
        amount = Decimal(str(current[5]))  # amount column
        
        if split_type == SplitType.SPLIT_50_50:
            ryan_share = amount / 2
            jordyn_share = amount / 2
        elif split_type == SplitType.RENT_SPLIT:
            ryan_share = amount * Decimal('0.47')
            jordyn_share = amount * Decimal('0.53')
        elif split_type == SplitType.RYAN_FULL:
            ryan_share = amount
            jordyn_share = Decimal('0')
        elif split_type == SplitType.JORDYN_FULL:
            ryan_share = Decimal('0')
            jordyn_share = amount
        # For SPLIT_CUSTOM, ryan_share and jordyn_share must be provided
        
        # Update the review
        cursor.execute("""
            UPDATE transaction_reviews SET
                status = ?,
                category = ?,
                split_type = ?,
                ryan_share = ?,
                jordyn_share = ?,
                allowed_amount = ?,
                is_personal = ?,
                notes = ?,
                reviewed_by = ?,
                reviewed_date = ?,
                updated_date = ?
            WHERE review_id = ?
        """, (
            ReviewStatus.COMPLETED.value,
            category.value,
            split_type.value,
            str(ryan_share) if ryan_share is not None else None,
            str(jordyn_share) if jordyn_share is not None else None,
            str(allowed_amount) if allowed_amount is not None else str(amount),
            1 if is_personal else 0,
            notes,
            reviewed_by,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            review_id
        ))
        
        # Add to history
        self._add_history(cursor, review_id, "reviewed", current, reviewed_by)
        
        # Learn from this review
        self._learn_pattern(cursor, current[3], category.value, split_type.value)
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_pending_reviews(self, limit: Optional[int] = None) -> pd.DataFrame:
        """Get transactions pending review."""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT review_id, date, description, amount, payer, source
            FROM transaction_reviews
            WHERE status = ?
            ORDER BY date DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        df = pd.read_sql_query(
            query,
            conn,
            params=(ReviewStatus.PENDING.value,)
        )
        
        conn.close()
        return df
    
    def get_review_by_id(self, review_id: int) -> Optional[Dict]:
        """Get a specific review by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM transaction_reviews WHERE review_id = ?
        """, (review_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        columns = [
            'review_id', 'transaction_hash', 'date', 'description',
            'amount', 'payer', 'source', 'status', 'category',
            'split_type', 'ryan_share', 'jordyn_share', 'allowed_amount',
            'is_personal', 'notes', 'reviewed_by', 'reviewed_date',
            'created_date', 'updated_date'
        ]
        
        return dict(zip(columns, row))
    
    def suggest_classification(self, description: str) -> Optional[Dict]:
        """Suggest classification based on learned patterns."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Look for exact matches first
        cursor.execute("""
            SELECT category, split_type, confidence, occurrence_count
            FROM learned_patterns
            WHERE pattern_type = 'exact' AND pattern_value = ?
            ORDER BY confidence DESC, occurrence_count DESC
            LIMIT 1
        """, (description.lower(),))
        
        result = cursor.fetchone()
        
        if not result:
            # Look for keyword matches
            keywords = description.lower().split()
            placeholders = ','.join(['?'] * len(keywords))
            
            cursor.execute(f"""
                SELECT category, split_type, confidence, occurrence_count
                FROM learned_patterns
                WHERE pattern_type = 'keyword' 
                AND pattern_value IN ({placeholders})
                GROUP BY category, split_type
                ORDER BY SUM(confidence * occurrence_count) DESC
                LIMIT 1
            """, keywords)
            
            result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'category': result[0],
                'split_type': result[1],
                'confidence': result[2],
                'occurrence_count': result[3]
            }
        
        return None
    
    def bulk_review(self, reviews: List[Dict]) -> int:
        """Process multiple reviews at once."""
        count = 0
        for review in reviews:
            success = self.review_transaction(
                review_id=review['review_id'],
                category=TransactionCategory(review['category']),
                split_type=SplitType(review['split_type']),
                ryan_share=review.get('ryan_share'),
                jordyn_share=review.get('jordyn_share'),
                allowed_amount=review.get('allowed_amount'),
                is_personal=review.get('is_personal', False),
                notes=review.get('notes'),
                reviewed_by=review.get('reviewed_by', 'Bulk Review')
            )
            if success:
                count += 1
        return count
    
    def export_reviews(self, status: Optional[ReviewStatus] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Export reviews to DataFrame."""
        conn = sqlite3.connect(self.db_path)
        
        query = "SELECT * FROM transaction_reviews WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY date DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df
    
    def get_review_statistics(self) -> Dict:
        """Get statistics about reviews."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count by status
        cursor.execute("""
            SELECT status, COUNT(*) FROM transaction_reviews
            GROUP BY status
        """)
        stats['by_status'] = dict(cursor.fetchall())
        
        # Count by category
        cursor.execute("""
            SELECT category, COUNT(*) FROM transaction_reviews
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        stats['by_category'] = dict(cursor.fetchall())
        
        # Count by split type
        cursor.execute("""
            SELECT split_type, COUNT(*) FROM transaction_reviews
            WHERE split_type IS NOT NULL
            GROUP BY split_type
        """)
        stats['by_split_type'] = dict(cursor.fetchall())
        
        # Personal vs shared
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN is_personal = 1 THEN 1 ELSE 0 END) as personal,
                SUM(CASE WHEN is_personal = 0 THEN 1 ELSE 0 END) as shared
            FROM transaction_reviews
            WHERE status = 'completed'
        """)
        result = cursor.fetchone()
        stats['personal_vs_shared'] = {
            'personal': result[0] or 0,
            'shared': result[1] or 0
        }
        
        # Average review time
        cursor.execute("""
            SELECT AVG(
                julianday(reviewed_date) - julianday(created_date)
            ) * 24 as avg_hours
            FROM transaction_reviews
            WHERE status = 'completed' AND reviewed_date IS NOT NULL
        """)
        result = cursor.fetchone()
        stats['avg_review_time_hours'] = result[0] or 0
        
        conn.close()
        return stats
    
    def _generate_transaction_hash(self, date: datetime, description: str,
                                   amount: Decimal, payer: str) -> str:
        """Generate unique hash for transaction."""
        data = f"{date}|{description}|{amount}|{payer}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _add_history(self, cursor: sqlite3.Cursor, review_id: int,
                     action: str, old_values: tuple, changed_by: str):
        """Add entry to review history."""
        # Convert old values to JSON
        old_dict = {
            'status': old_values[7],
            'category': old_values[8],
            'split_type': old_values[9],
            'ryan_share': old_values[10],
            'jordyn_share': old_values[11],
            'allowed_amount': old_values[12],
            'is_personal': old_values[13],
            'notes': old_values[14]
        }
        
        cursor.execute("""
            INSERT INTO review_history
            (review_id, action, old_values, changed_by, changed_date)
            VALUES (?, ?, ?, ?, ?)
        """, (
            review_id,
            action,
            json.dumps(old_dict),
            changed_by,
            datetime.now().isoformat()
        ))
    
    def _learn_pattern(self, cursor: sqlite3.Cursor, description: str,
                       category: str, split_type: str):
        """Learn from review decision for future suggestions."""
        # Learn exact match
        self._update_pattern(
            cursor, 'exact', description.lower(), category, split_type
        )
        
        # Learn keywords
        keywords = [
            word.lower() for word in description.split()
            if len(word) > 3  # Skip short words
        ]
        
        for keyword in keywords:
            self._update_pattern(
                cursor, 'keyword', keyword, category, split_type
            )
    
    def _update_pattern(self, cursor: sqlite3.Cursor, pattern_type: str,
                        pattern_value: str, category: str, split_type: str):
        """Update or create a learned pattern."""
        cursor.execute("""
            SELECT pattern_id, confidence, occurrence_count
            FROM learned_patterns
            WHERE pattern_type = ? AND pattern_value = ? 
            AND category = ? AND split_type = ?
        """, (pattern_type, pattern_value, category, split_type))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing pattern
            pattern_id, confidence, count = result
            new_confidence = min(0.95, confidence + 0.05)  # Cap at 95%
            
            cursor.execute("""
                UPDATE learned_patterns SET
                    confidence = ?,
                    occurrence_count = ?,
                    last_seen_date = ?
                WHERE pattern_id = ?
            """, (
                new_confidence,
                count + 1,
                datetime.now().isoformat(),
                pattern_id
            ))
        else:
            # Create new pattern
            cursor.execute("""
                INSERT INTO learned_patterns
                (pattern_type, pattern_value, category, split_type,
                 confidence, occurrence_count, created_date, last_seen_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_type,
                pattern_value,
                category,
                split_type,
                0.5,  # Start with 50% confidence
                1,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))


class InteractiveReviewer:
    """Interactive command-line interface for reviewing transactions."""
    
    def __init__(self, review_system: ManualReviewSystem):
        self.review_system = review_system
    
    def run(self):
        """Run the interactive review interface."""
        print("\n" + "="*60)
        print("MANUAL TRANSACTION REVIEW SYSTEM")
        print("="*60)
        
        while True:
            print("\nOptions:")
            print("1. Review pending transactions")
            print("2. View review statistics")
            print("3. Export completed reviews")
            print("4. Search transactions")
            print("5. Exit")
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                self._review_pending()
            elif choice == '2':
                self._show_statistics()
            elif choice == '3':
                self._export_reviews()
            elif choice == '4':
                self._search_transactions()
            elif choice == '5':
                print("\nExiting review system.")
                break
            else:
                print("Invalid option. Please try again.")
    
    def _review_pending(self):
        """Review pending transactions interactively."""
        pending = self.review_system.get_pending_reviews(limit=10)
        
        if pending.empty:
            print("\nNo pending transactions to review!")
            return
        
        print(f"\nFound {len(pending)} pending transactions:")
        
        for idx, row in pending.iterrows():
            print(f"\n--- Transaction {idx + 1} of {len(pending)} ---")
            print(f"Date: {row['date']}")
            print(f"Description: {row['description']}")
            print(f"Amount: ${row['amount']:,.2f}")
            print(f"Payer: {row['payer']}")
            
            # Check for suggestions
            suggestion = self.review_system.suggest_classification(row['description'])
            if suggestion:
                print(f"\nSuggested: {suggestion['category']} - {suggestion['split_type']}")
                print(f"Confidence: {suggestion['confidence']:.0%}")
            
            # Get classification
            while True:
                print("\nCategories:")
                for i, cat in enumerate(TransactionCategory, 1):
                    print(f"{i}. {cat.value}")
                
                cat_choice = input("\nSelect category (1-15) or 's' to skip: ").strip()
                
                if cat_choice.lower() == 's':
                    break
                
                try:
                    cat_idx = int(cat_choice) - 1
                    category = list(TransactionCategory)[cat_idx]
                    
                    # Get split type
                    print("\nSplit types:")
                    for i, split in enumerate(SplitType, 1):
                        print(f"{i}. {split.value}")
                    
                    split_choice = input("\nSelect split type (1-5): ").strip()
                    split_idx = int(split_choice) - 1
                    split_type = list(SplitType)[split_idx]
                    
                    # Get notes
                    notes = input("\nNotes (optional): ").strip() or None
                    
                    # Review the transaction
                    success = self.review_system.review_transaction(
                        review_id=row['review_id'],
                        category=category,
                        split_type=split_type,
                        notes=notes,
                        reviewed_by='Interactive User'
                    )
                    
                    if success:
                        print("✓ Transaction reviewed successfully!")
                    break
                    
                except (ValueError, IndexError):
                    print("Invalid selection. Please try again.")
            
            # Ask if continue
            if input("\nContinue reviewing? (y/n): ").strip().lower() != 'y':
                break
    
    def _show_statistics(self):
        """Display review statistics."""
        stats = self.review_system.get_review_statistics()
        
        print("\n" + "="*40)
        print("REVIEW STATISTICS")
        print("="*40)
        
        print("\nBy Status:")
        for status, count in stats.get('by_status', {}).items():
            print(f"  {status}: {count}")
        
        print("\nBy Category:")
        for category, count in sorted(stats.get('by_category', {}).items()):
            print(f"  {category}: {count}")
        
        print("\nBy Split Type:")
        for split, count in stats.get('by_split_type', {}).items():
            print(f"  {split}: {count}")
        
        print(f"\nPersonal vs Shared:")
        print(f"  Personal: {stats['personal_vs_shared']['personal']}")
        print(f"  Shared: {stats['personal_vs_shared']['shared']}")
        
        print(f"\nAverage Review Time: {stats['avg_review_time_hours']:.1f} hours")
    
    def _export_reviews(self):
        """Export completed reviews."""
        filename = input("\nExport filename (default: completed_reviews.csv): ").strip()
        if not filename:
            filename = "completed_reviews.csv"
        
        df = self.review_system.export_reviews(status=ReviewStatus.COMPLETED)
        df.to_csv(filename, index=False)
        print(f"\n✓ Exported {len(df)} reviews to {filename}")
    
    def _search_transactions(self):
        """Search for specific transactions."""
        search_term = input("\nEnter search term: ").strip()
        
        conn = sqlite3.connect(self.review_system.db_path)
        df = pd.read_sql_query("""
            SELECT review_id, date, description, amount, payer, status, category
            FROM transaction_reviews
            WHERE description LIKE ?
            ORDER BY date DESC
            LIMIT 20
        """, conn, params=(f'%{search_term}%',))
        conn.close()
        
        if df.empty:
            print(f"\nNo transactions found matching '{search_term}'")
        else:
            print(f"\nFound {len(df)} transactions:")
            print(df.to_string(index=False))


def main():
    """Run the manual review system."""
    # Initialize system
    review_system = ManualReviewSystem()
    
    # Example: Add some test transactions
    print("Adding test transactions for review...")
    
    test_transactions = [
        (datetime(2024, 10, 1), "Costco Wholesale", Decimal("234.56"), "Ryan"),
        (datetime(2024, 10, 5), "Unknown Merchant 123", Decimal("45.00"), "Jordyn"),
        (datetime(2024, 10, 10), "Venmo Payment", Decimal("100.00"), "Ryan"),
    ]
    
    for date, desc, amount, payer in test_transactions:
        review_id = review_system.add_transaction_for_review(
            date, desc, amount, payer, "Test"
        )
        print(f"Added review ID: {review_id}")
    
    # Run interactive reviewer
    reviewer = InteractiveReviewer(review_system)
    reviewer.run()


if __name__ == "__main__":
    main()