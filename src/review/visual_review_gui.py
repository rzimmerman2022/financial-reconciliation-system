#!/usr/bin/env python3
"""
Visual Transaction Review GUI
============================

A user-friendly graphical interface for reviewing financial transactions.
This provides an intuitive way to categorize transactions, adjust amounts,
and add notes during the manual review process.

Features:
- Clean, professional interface
- Keyboard shortcuts for efficient review
- Progress tracking with statistics
- Category selection with quick buttons
- Amount adjustment with validation
- Notes field for detailed comments
- Auto-save functionality

Author: Claude (Anthropic)
Date: July 31, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Callable
import json

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.review.manual_review_system import (
    ManualReviewSystem, TransactionCategory, SplitType, ReviewStatus
)


class TransactionReviewGUI:
    """Visual GUI for reviewing transactions with intuitive controls."""
    
    def __init__(self, review_db_path: str = "data/phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.current_transaction = None
        self.current_index = 0
        self.transactions = []
        self.auto_save = True
        
        # Statistics
        self.stats = {
            'total': 0,
            'reviewed': 0,
            'skipped': 0,
            'session_start': datetime.now()
        }
        
        # Initialize GUI
        self.setup_gui()
        self.load_pending_transactions()
        self.show_current_transaction()
        
    def setup_gui(self):
        """Create the main GUI interface."""
        self.root = tk.Tk()
        self.root.title("Financial Transaction Review")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom fonts
        self.title_font = font.Font(family="Arial", size=12, weight="bold")
        self.heading_font = font.Font(family="Arial", size=10, weight="bold")
        self.body_font = font.Font(family="Arial", size=9)
        
        self.create_widgets()
        self.setup_keyboard_shortcuts()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Progress section
        self.create_progress_section(main_frame, row=0)
        
        # Transaction details section
        self.create_transaction_section(main_frame, row=1)
        
        # Review controls section
        self.create_review_section(main_frame, row=2)
        
        # Navigation section
        self.create_navigation_section(main_frame, row=3)
        
        # Statistics section
        self.create_stats_section(main_frame, row=4)
        
    def create_progress_section(self, parent, row):
        """Create progress tracking section."""
        frame = ttk.LabelFrame(parent, text="Progress", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            frame, 
            variable=self.progress_var, 
            maximum=100,
            length=400
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Progress label
        self.progress_label = ttk.Label(frame, text="Loading transactions...", font=self.body_font)
        self.progress_label.grid(row=1, column=0)
        
    def create_transaction_section(self, parent, row):
        """Create transaction details section."""
        frame = ttk.LabelFrame(parent, text="Transaction Details", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Transaction details
        details = [
            ("Date:", "transaction_date"),
            ("Description:", "transaction_desc"),
            ("Amount:", "transaction_amount"),
            ("Payer:", "transaction_payer"),
            ("Source:", "transaction_source")
        ]
        
        self.transaction_vars = {}
        for i, (label, var_name) in enumerate(details):
            ttk.Label(frame, text=label, font=self.heading_font).grid(
                row=i, column=0, sticky=tk.W, pady=2, padx=(0, 10)
            )
            
            var = tk.StringVar()
            self.transaction_vars[var_name] = var
            
            if var_name == "transaction_desc":
                # Multi-line for description
                text_widget = tk.Text(frame, height=3, width=50, font=self.body_font, wrap=tk.WORD)
                text_widget.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
                self.transaction_desc_widget = text_widget
            else:
                entry = ttk.Entry(frame, textvariable=var, font=self.body_font, state='readonly')
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
                
    def create_review_section(self, parent, row):
        """Create review controls section."""
        frame = ttk.LabelFrame(parent, text="Review Decision", padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        frame.columnconfigure(1, weight=1)
        
        # Category selection
        ttk.Label(frame, text="Category:", font=self.heading_font).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10)
        )
        
        category_frame = ttk.Frame(frame)
        category_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.category_var = tk.StringVar()
        categories = [
            ("Expense (E)", "expense"),
            ("Rent (R)", "rent"), 
            ("Settlement (S)", "settlement"),
            ("Personal (P)", "personal")
        ]
        
        self.category_buttons = {}
        for i, (text, value) in enumerate(categories):
            btn = ttk.Radiobutton(
                category_frame, 
                text=text, 
                variable=self.category_var, 
                value=value,
                command=self.on_category_change
            )
            btn.grid(row=0, column=i, padx=5)
            self.category_buttons[value] = btn
            
        # Amount adjustment
        ttk.Label(frame, text="Allowed Amount:", font=self.heading_font).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10)
        )
        
        amount_frame = ttk.Frame(frame)
        amount_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(amount_frame, textvariable=self.amount_var, width=15, font=self.body_font)
        self.amount_entry.grid(row=0, column=0, padx=(0, 10))
        
        # Quick amount buttons
        quick_amounts = [("Full", "full"), ("Half", "half"), ("Zero", "zero")]
        for i, (text, action) in enumerate(quick_amounts):
            btn = ttk.Button(
                amount_frame, 
                text=text, 
                command=lambda a=action: self.set_quick_amount(a),
                width=8
            )
            btn.grid(row=0, column=i+1, padx=2)
            
        # Notes
        ttk.Label(frame, text="Notes:", font=self.heading_font).grid(
            row=2, column=0, sticky=(tk.W, tk.N), pady=5, padx=(0, 10)
        )
        
        self.notes_text = tk.Text(frame, height=4, width=60, font=self.body_font, wrap=tk.WORD)
        self.notes_text.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Scrollbar for notes
        notes_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        notes_scroll.grid(row=2, column=2, sticky=(tk.N, tk.S), pady=5)
        self.notes_text.configure(yscrollcommand=notes_scroll.set)
        
    def create_navigation_section(self, parent, row):
        """Create navigation controls."""
        frame = ttk.Frame(parent, padding="10")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Navigation buttons
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(side=tk.LEFT)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous (A)", command=self.previous_transaction, width=15)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.skip_btn = ttk.Button(nav_frame, text="Skip (S)", command=self.skip_transaction, width=12)
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(nav_frame, text="Save & Next (D)", command=self.save_and_next, width=15)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Action buttons on the right
        action_frame = ttk.Frame(frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="Export All", command=self.export_decisions, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Settings", command=self.show_settings, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Help (F1)", command=self.show_help, width=12).pack(side=tk.LEFT, padx=5)
        
    def create_stats_section(self, parent, row):
        """Create statistics section."""
        frame = ttk.LabelFrame(parent, text="Session Statistics", padding="5")
        frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.stats_label = ttk.Label(frame, text="Ready to begin review", font=self.body_font)
        self.stats_label.pack()
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for efficient review."""
        shortcuts = {
            '<Key-e>': lambda e: self.set_category('expense'),
            '<Key-r>': lambda e: self.set_category('rent'),
            '<Key-s>': lambda e: self.set_category('settlement'),
            '<Key-p>': lambda e: self.set_category('personal'),
            '<Key-a>': lambda e: self.previous_transaction(),
            '<Key-d>': lambda e: self.save_and_next(),
            '<Key-S>': lambda e: self.skip_transaction(),
            '<F1>': lambda e: self.show_help(),
            '<Control-s>': lambda e: self.save_current(),
            '<Control-q>': lambda e: self.quit_application(),
            '<Escape>': lambda e: self.quit_application(),
        }
        
        for key, command in shortcuts.items():
            self.root.bind(key, command)
            
    def load_pending_transactions(self):
        """Load transactions needing review."""
        try:
            # Get pending transactions from the review system
            pending = self.review_system.get_pending_transactions()
            self.transactions = [t for t in pending if t['status'] == ReviewStatus.PENDING]
            
            self.stats['total'] = len(self.transactions)
            self.update_progress()
            
            if not self.transactions:
                messagebox.showinfo("Complete", "No transactions need review!")
                self.root.quit()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {e}")
            self.root.quit()
            
    def show_current_transaction(self):
        """Display the current transaction in the GUI."""
        if not self.transactions or self.current_index >= len(self.transactions):
            messagebox.showinfo("Complete", "All transactions reviewed!")
            self.root.quit()
            return
            
        self.current_transaction = self.transactions[self.current_index]
        
        # Update transaction details
        self.transaction_vars['transaction_date'].set(
            self.current_transaction['date'].strftime('%Y-%m-%d')
        )
        
        self.transaction_desc_widget.delete(1.0, tk.END)
        self.transaction_desc_widget.insert(1.0, self.current_transaction['description'])
        
        self.transaction_vars['transaction_amount'].set(f"${self.current_transaction['amount']:.2f}")
        self.transaction_vars['transaction_payer'].set(self.current_transaction['payer'])
        self.transaction_vars['transaction_source'].set(self.current_transaction.get('source', 'Unknown'))
        
        # Reset review fields
        self.category_var.set("")
        self.amount_var.set(f"{self.current_transaction['amount']:.2f}")
        self.notes_text.delete(1.0, tk.END)
        
        # Load existing review if available
        self.load_existing_review()
        
        self.update_progress()
        self.update_navigation_buttons()
        
    def load_existing_review(self):
        """Load existing review decision if available."""
        try:
            review_id = self.current_transaction.get('review_id')
            if review_id:
                decision = self.review_system.get_review_decision(review_id)
                if decision and decision['status'] != ReviewStatus.PENDING:
                    self.category_var.set(decision['category'].value)
                    self.amount_var.set(f"{decision['allowed_amount']:.2f}")
                    if decision['notes']:
                        self.notes_text.insert(1.0, decision['notes'])
        except Exception:
            pass  # No existing review, that's fine
            
    def set_category(self, category: str):
        """Set the category and update related fields."""
        self.category_var.set(category)
        self.on_category_change()
        
    def on_category_change(self):
        """Handle category selection changes."""
        category = self.category_var.get()
        original_amount = float(self.current_transaction['amount'])
        
        # Auto-adjust amount based on category
        if category == 'personal':
            self.amount_var.set("0.00")
        elif category == 'settlement':
            self.amount_var.set(f"{original_amount:.2f}")
        elif category in ['expense', 'rent']:
            # Default to full amount, user can adjust
            self.amount_var.set(f"{original_amount:.2f}")
            
    def set_quick_amount(self, action: str):
        """Set amount using quick buttons."""
        original_amount = float(self.current_transaction['amount'])
        
        if action == 'full':
            self.amount_var.set(f"{original_amount:.2f}")
        elif action == 'half':
            self.amount_var.set(f"{original_amount / 2:.2f}")
        elif action == 'zero':
            self.amount_var.set("0.00")
            
    def save_current(self):
        """Save the current review decision."""
        if not self.validate_review():
            return False
            
        try:
            category = TransactionCategory(self.category_var.get())
            allowed_amount = Decimal(self.amount_var.get())
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            # Save the review decision
            review_id = self.current_transaction.get('review_id')
            if review_id:
                self.review_system.update_review_decision(
                    review_id=review_id,
                    category=category,
                    allowed_amount=allowed_amount,
                    notes=notes
                )
            else:
                # Add new review
                self.review_system.add_transaction_for_review(
                    date=self.current_transaction['date'],
                    description=self.current_transaction['description'],
                    amount=self.current_transaction['amount'],
                    payer=self.current_transaction['payer'],
                    source=self.current_transaction.get('source', 'Unknown'),
                    category=category,
                    allowed_amount=allowed_amount,
                    notes=notes
                )
                
            self.stats['reviewed'] += 1
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save review: {e}")
            return False
            
    def validate_review(self):
        """Validate the current review decision."""
        if not self.category_var.get():
            messagebox.showwarning("Validation", "Please select a category")
            return False
            
        try:
            amount = Decimal(self.amount_var.get())
            if amount < 0:
                messagebox.showwarning("Validation", "Amount cannot be negative")
                return False
        except (ValueError, InvalidOperation):
            messagebox.showwarning("Validation", "Please enter a valid amount")
            return False
            
        return True
        
    def save_and_next(self):
        """Save current transaction and move to next."""
        if self.save_current():
            self.next_transaction()
            
    def next_transaction(self):
        """Move to the next transaction."""
        self.current_index += 1
        self.show_current_transaction()
        
    def previous_transaction(self):
        """Move to the previous transaction."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_transaction()
            
    def skip_transaction(self):
        """Skip the current transaction."""
        self.stats['skipped'] += 1
        self.next_transaction()
        
    def update_progress(self):
        """Update progress bar and statistics."""
        if self.stats['total'] > 0:
            completed = self.current_index
            progress = (completed / self.stats['total']) * 100
            self.progress_var.set(progress)
            
            self.progress_label.config(
                text=f"Transaction {self.current_index + 1} of {self.stats['total']} "
                     f"({progress:.1f}% complete)"
            )
            
        # Update session stats
        elapsed = datetime.now() - self.stats['session_start']
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        stats_text = (
            f"Reviewed: {self.stats['reviewed']} | "
            f"Skipped: {self.stats['skipped']} | "
            f"Session time: {elapsed_str}"
        )
        self.stats_label.config(text=stats_text)
        
    def update_navigation_buttons(self):
        """Update navigation button states."""
        self.prev_btn.config(state='normal' if self.current_index > 0 else 'disabled')
        
    def export_decisions(self):
        """Export all review decisions."""
        try:
            filename = f"review_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            decisions = self.review_system.export_decisions()
            
            with open(filename, 'w') as f:
                json.dump(decisions, f, indent=2, default=str)
                
            messagebox.showinfo("Export Complete", f"Decisions exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
            
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("300x200")
        settings_window.transient(self.root)
        
        ttk.Label(settings_window, text="Settings", font=self.title_font).pack(pady=10)
        
        # Auto-save setting
        self.auto_save_var = tk.BooleanVar(value=self.auto_save)
        ttk.Checkbutton(
            settings_window, 
            text="Auto-save decisions", 
            variable=self.auto_save_var,
            command=lambda: setattr(self, 'auto_save', self.auto_save_var.get())
        ).pack(pady=5)
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=20)
        
    def show_help(self):
        """Show help dialog."""
        help_text = """
Keyboard Shortcuts:
- E: Set category to Expense
- R: Set category to Rent  
- S: Set category to Settlement
- P: Set category to Personal
- A: Previous transaction
- D: Save and next transaction
- Shift+S: Skip transaction
- F1: Show this help
- Ctrl+S: Save current
- Ctrl+Q / Escape: Quit

Quick Amount Buttons:
- Full: Use original amount
- Half: Use half the amount
- Zero: Set amount to zero

Categories:
- Expense: Shared expenses (groceries, utilities)
- Rent: Monthly rent payments
- Settlement: Zelle/Venmo transfers
- Personal: Individual purchases
"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help - Keyboard Shortcuts")
        help_window.geometry("500x400")
        help_window.transient(self.root)
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, font=self.body_font)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(1.0, help_text)
        text_widget.config(state='disabled')
        
        ttk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)
        
    def quit_application(self):
        """Quit the application with confirmation."""
        if messagebox.askokcancel("Quit", "Are you sure you want to quit?"):
            self.root.quit()
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the GUI application."""
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "data/phase5_manual_reviews.db"
        
    try:
        app = TransactionReviewGUI(db_path)
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()