#!/usr/bin/env python3
"""
Modern Visual Transaction Review GUI
===================================

A beautiful, modern graphical interface for reviewing financial transactions.
Follows Material Design principles with smooth animations and intuitive UX.

Features:
- Modern Material Design interface
- Smooth animations and transitions
- Beautiful color scheme with proper contrast
- Card-based layout with shadows
- Responsive design
- Progress visualization
- Keyboard shortcuts for power users
- Auto-save with visual feedback

Author: Claude (Anthropic)
Date: July 31, 2025
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Optional, Callable, Tuple
import json
import math
import pandas as pd

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.review.manual_review_system import (
    ManualReviewSystem, TransactionCategory, SplitType, ReviewStatus
)


class ModernColors:
    """Modern color palette following Material Design principles."""
    # Primary colors
    PRIMARY = "#1976D2"  # Blue 700
    PRIMARY_LIGHT = "#42A5F5"  # Blue 400
    PRIMARY_DARK = "#0D47A1"  # Blue 900
    
    # Accent colors
    ACCENT = "#00BCD4"  # Cyan 500
    ACCENT_LIGHT = "#4DD0E1"  # Cyan 300
    
    # Semantic colors
    SUCCESS = "#4CAF50"  # Green 500
    WARNING = "#FF9800"  # Orange 500
    ERROR = "#F44336"  # Red 500
    INFO = "#2196F3"  # Blue 500
    
    # Neutral colors
    BACKGROUND = "#FAFAFA"  # Grey 50
    SURFACE = "#FFFFFF"  # White
    SURFACE_VARIANT = "#F5F5F5"  # Grey 100
    
    # Text colors
    TEXT_PRIMARY = "#212121"  # Grey 900
    TEXT_SECONDARY = "#757575"  # Grey 600
    TEXT_DISABLED = "#BDBDBD"  # Grey 400
    TEXT_ON_PRIMARY = "#FFFFFF"
    
    # UI elements
    DIVIDER = "#E0E0E0"  # Grey 300
    SHADOW = "#00000029"  # Black 16%
    HOVER = "#00000014"  # Black 8%
    
    # Category colors
    CATEGORY_EXPENSE = "#FF5252"  # Red A200
    CATEGORY_RENT = "#536DFE"  # Indigo A200
    CATEGORY_SETTLEMENT = "#7C4DFF"  # Deep Purple A200
    CATEGORY_PERSONAL = "#FF6E40"  # Deep Orange A200


class ModernTransactionReviewGUI:
    """Modern visual GUI for reviewing transactions with Material Design."""
    
    def __init__(self, review_db_path: str = "data/phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.current_transaction = None
        self.current_index = 0
        self.transactions = []
        self.auto_save = True
        self.animation_duration = 300  # milliseconds
        
        # Statistics
        self.stats = {
            'total': 0,
            'reviewed': 0,
            'skipped': 0,
            'session_start': datetime.now()
        }
        
        # Animation state
        self.animation_running = False
        
        # Initialize GUI
        self.setup_gui()
        self.load_pending_transactions()
        self.show_current_transaction()
        
    def setup_gui(self):
        """Create the main GUI interface with modern styling."""
        self.root = tk.Tk()
        self.root.title("Transaction Review • Financial Reconciliation")
        self.root.geometry("1200x800")
        self.root.configure(bg=ModernColors.BACKGROUND)
        
        # Set minimum window size
        self.root.minsize(1000, 700)
        
        # Configure window icon (if available)
        try:
            self.root.iconbitmap('assets/icon.ico')
        except:
            pass
        
        # Configure custom fonts
        self.setup_fonts()
        
        # Configure custom styles
        self.setup_styles()
        
        # Create main interface
        self.create_modern_interface()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Center window on screen
        self.center_window()
        
    def setup_fonts(self):
        """Setup modern typography following Material Design guidelines."""
        # Try to use system fonts that look modern
        font_families = {
            'win32': 'Segoe UI',
            'darwin': 'SF Pro Display',
            'linux': 'Ubuntu'
        }
        
        base_font = font_families.get(sys.platform, 'Arial')
        
        # Material Design typography scale
        self.fonts = {
            'headline1': font.Font(family=base_font, size=32, weight="normal"),
            'headline2': font.Font(family=base_font, size=28, weight="normal"),
            'headline3': font.Font(family=base_font, size=24, weight="normal"),
            'headline4': font.Font(family=base_font, size=20, weight="normal"),
            'headline5': font.Font(family=base_font, size=18, weight="normal"),
            'headline6': font.Font(family=base_font, size=16, weight="bold"),
            'subtitle1': font.Font(family=base_font, size=14, weight="normal"),
            'subtitle2': font.Font(family=base_font, size=12, weight="bold"),
            'body1': font.Font(family=base_font, size=14, weight="normal"),
            'body2': font.Font(family=base_font, size=12, weight="normal"),
            'button': font.Font(family=base_font, size=13, weight="bold"),
            'caption': font.Font(family=base_font, size=11, weight="normal"),
            'overline': font.Font(family=base_font, size=10, weight="normal"),
        }
        
    def setup_styles(self):
        """Configure ttk styles for modern appearance."""
        self.style = ttk.Style()
        
        # Configure modern button style
        self.style.configure(
            "Modern.TButton",
            font=self.fonts['button'],
            foreground=ModernColors.TEXT_PRIMARY,
            background=ModernColors.SURFACE,
            borderwidth=0,
            focuscolor='none',
            relief="flat"
        )
        
        self.style.map("Modern.TButton",
            background=[('active', ModernColors.HOVER)],
            foreground=[('active', ModernColors.TEXT_PRIMARY)]
        )
        
        # Primary button style
        self.style.configure(
            "Primary.TButton",
            font=self.fonts['button'],
            foreground=ModernColors.TEXT_ON_PRIMARY,
            background=ModernColors.PRIMARY,
            borderwidth=0,
            focuscolor='none',
            relief="flat"
        )
        
        self.style.map("Primary.TButton",
            background=[('active', ModernColors.PRIMARY_DARK)],
            foreground=[('active', ModernColors.TEXT_ON_PRIMARY)]
        )
        
        # Configure label styles
        self.style.configure(
            "Heading.TLabel",
            font=self.fonts['headline6'],
            foreground=ModernColors.TEXT_PRIMARY,
            background=ModernColors.SURFACE
        )
        
        self.style.configure(
            "Body.TLabel",
            font=self.fonts['body1'],
            foreground=ModernColors.TEXT_SECONDARY,
            background=ModernColors.SURFACE
        )
        
    def create_modern_interface(self):
        """Create the modern Material Design interface."""
        # Main container with padding
        self.main_container = tk.Frame(self.root, bg=ModernColors.BACKGROUND)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header section
        self.create_header_section()
        
        # Create main content area with two columns
        self.content_container = tk.Frame(self.main_container, bg=ModernColors.BACKGROUND)
        self.content_container.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # Left column - Transaction details
        self.left_column = tk.Frame(self.content_container, bg=ModernColors.BACKGROUND)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right column - Review controls
        self.right_column = tk.Frame(self.content_container, bg=ModernColors.BACKGROUND)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Create cards for each section
        self.create_transaction_card()
        self.create_review_card()
        self.create_stats_card()
        
    def create_header_section(self):
        """Create modern header with title and progress."""
        # Header card
        header_card = self.create_card(self.main_container)
        header_card.pack(fill=tk.X, pady=(0, 20))
        
        # Title section
        title_frame = tk.Frame(header_card, bg=ModernColors.SURFACE)
        title_frame.pack(fill=tk.X, padx=24, pady=(24, 12))
        
        # App title
        title_label = tk.Label(
            title_frame,
            text="Transaction Review",
            font=self.fonts['headline4'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE
        )
        title_label.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = tk.Frame(header_card, bg=ModernColors.SURFACE)
        progress_frame.pack(fill=tk.X, padx=24, pady=(0, 24))
        
        # Progress label
        self.progress_label = tk.Label(
            progress_frame,
            text="Loading transactions...",
            font=self.fonts['body2'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        )
        self.progress_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Modern progress bar
        self.create_modern_progress_bar(progress_frame)
        
    def create_modern_progress_bar(self, parent):
        """Create a modern styled progress bar."""
        # Progress bar container
        progress_container = tk.Frame(parent, bg=ModernColors.DIVIDER, height=4)
        progress_container.pack(fill=tk.X)
        progress_container.pack_propagate(False)
        
        # Progress bar fill
        self.progress_fill = tk.Frame(
            progress_container,
            bg=ModernColors.PRIMARY,
            height=4
        )
        self.progress_fill.place(x=0, y=0, width=0, height=4)
        
        self.progress_container = progress_container
        
    def create_transaction_card(self):
        """Create card for transaction details."""
        # Transaction card
        transaction_card = self.create_card(self.left_column)
        transaction_card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header_frame = tk.Frame(transaction_card, bg=ModernColors.SURFACE)
        header_frame.pack(fill=tk.X, padx=24, pady=(24, 16))
        
        tk.Label(
            header_frame,
            text="Transaction Details",
            font=self.fonts['headline6'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE
        ).pack(side=tk.LEFT)
        
        # Transaction number badge
        self.transaction_badge = tk.Label(
            header_frame,
            text="#1",
            font=self.fonts['caption'],
            fg=ModernColors.TEXT_ON_PRIMARY,
            bg=ModernColors.PRIMARY,
            padx=12,
            pady=4
        )
        self.transaction_badge.pack(side=tk.RIGHT)
        
        # Divider
        self.create_divider(transaction_card)
        
        # Transaction details container
        details_frame = tk.Frame(transaction_card, bg=ModernColors.SURFACE)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(16, 24))
        
        # Create detail fields
        self.transaction_fields = {}
        details = [
            ("Date", "date", "📅"),
            ("Description", "description", "📝"),
            ("Amount", "amount", "💵"),
            ("Payer", "payer", "👤"),
            ("Source", "source", "🏦")
        ]
        
        for i, (label, field_id, icon) in enumerate(details):
            # Row container
            row_frame = tk.Frame(details_frame, bg=ModernColors.SURFACE)
            row_frame.pack(fill=tk.X, pady=8)
            
            # Icon and label
            label_frame = tk.Frame(row_frame, bg=ModernColors.SURFACE)
            label_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            tk.Label(
                label_frame,
                text=f"{icon}  {label}",
                font=self.fonts['subtitle2'],
                fg=ModernColors.TEXT_SECONDARY,
                bg=ModernColors.SURFACE
            ).pack(side=tk.LEFT)
            
            # Value
            if field_id == "description":
                # Multi-line text for description
                text_frame = tk.Frame(row_frame, bg=ModernColors.SURFACE_VARIANT)
                text_frame.pack(fill=tk.X, pady=(8, 0))
                
                text_widget = tk.Text(
                    text_frame,
                    height=3,
                    font=self.fonts['body1'],
                    fg=ModernColors.TEXT_PRIMARY,
                    bg=ModernColors.SURFACE_VARIANT,
                    relief=tk.FLAT,
                    wrap=tk.WORD,
                    padx=12,
                    pady=8
                )
                text_widget.pack(fill=tk.X)
                self.transaction_fields[field_id] = text_widget
            else:
                value_label = tk.Label(
                    row_frame,
                    text="",
                    font=self.fonts['body1'],
                    fg=ModernColors.TEXT_PRIMARY,
                    bg=ModernColors.SURFACE,
                    anchor=tk.E
                )
                value_label.pack(side=tk.RIGHT)
                self.transaction_fields[field_id] = value_label
                
    def create_review_card(self):
        """Create card for review controls."""
        # Review card
        review_card = self.create_card(self.right_column)
        review_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Card header
        header_frame = tk.Frame(review_card, bg=ModernColors.SURFACE)
        header_frame.pack(fill=tk.X, padx=24, pady=(24, 16))
        
        tk.Label(
            header_frame,
            text="Review Decision",
            font=self.fonts['headline6'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE
        ).pack(side=tk.LEFT)
        
        # Divider
        self.create_divider(review_card)
        
        # Review controls container
        controls_frame = tk.Frame(review_card, bg=ModernColors.SURFACE)
        controls_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(16, 24))
        
        # Category selection
        self.create_category_section(controls_frame)
        
        # Amount adjustment
        self.create_amount_section(controls_frame)
        
        # Notes section
        self.create_notes_section(controls_frame)
        
        # Action buttons
        self.create_action_buttons(controls_frame)
        
    def create_category_section(self, parent):
        """Create modern category selection with chips."""
        # Label
        tk.Label(
            parent,
            text="Category",
            font=self.fonts['subtitle1'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        ).pack(anchor=tk.W, pady=(0, 12))
        
        # Category chips container
        chips_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        chips_frame.pack(fill=tk.X, pady=(0, 24))
        
        self.category_var = tk.StringVar()
        self.category_chips = {}
        
        categories = [
            ("Expense", "expense", ModernColors.CATEGORY_EXPENSE, "E"),
            ("Rent", "rent", ModernColors.CATEGORY_RENT, "R"),
            ("Settlement", "settlement", ModernColors.CATEGORY_SETTLEMENT, "S"),
            ("Personal", "personal", ModernColors.CATEGORY_PERSONAL, "P")
        ]
        
        for i, (label, value, color, shortcut) in enumerate(categories):
            chip = self.create_chip(
                chips_frame,
                label,
                value,
                color,
                shortcut
            )
            chip.pack(side=tk.LEFT, padx=(0, 8))
            self.category_chips[value] = chip
            
    def create_chip(self, parent: tk.Frame, label: str, value: str, 
                   color: str, shortcut: str) -> tk.Frame:
        """Create a Material Design chip/tag."""
        chip = tk.Frame(
            parent,
            bg=ModernColors.SURFACE,
            relief=tk.FLAT,
            bd=1,
            highlightbackground=ModernColors.DIVIDER,
            highlightthickness=1
        )
        
        # Chip content
        content = tk.Frame(chip, bg=ModernColors.SURFACE)
        content.pack(padx=16, pady=8)
        
        # Radio button (hidden)
        radio = tk.Radiobutton(
            content,
            text=f"{label} ({shortcut})",
            variable=self.category_var,
            value=value,
            font=self.fonts['button'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE,
            activebackground=ModernColors.SURFACE,
            selectcolor=ModernColors.SURFACE,
            indicatoron=False,
            bd=0,
            padx=0,
            pady=0,
            command=lambda: self.on_category_change(value)
        )
        radio.pack()
        
        # Store references
        chip.radio = radio
        chip.color = color
        chip.value = value
        
        # Hover effects
        def on_enter(e):
            if self.category_var.get() != value:
                chip.configure(highlightbackground=color)
                
        def on_leave(e):
            if self.category_var.get() != value:
                chip.configure(highlightbackground=ModernColors.DIVIDER)
                
        chip.bind("<Enter>", on_enter)
        chip.bind("<Leave>", on_leave)
        content.bind("<Enter>", on_enter)
        content.bind("<Leave>", on_leave)
        radio.bind("<Enter>", on_enter)
        radio.bind("<Leave>", on_leave)
        
        return chip
        
    def create_amount_section(self, parent):
        """Create modern amount adjustment section."""
        # Label
        tk.Label(
            parent,
            text="Allowed Amount",
            font=self.fonts['subtitle1'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        ).pack(anchor=tk.W, pady=(0, 12))
        
        # Amount container
        amount_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        amount_frame.pack(fill=tk.X, pady=(0, 24))
        
        # Amount input with modern styling
        self.amount_var = tk.StringVar()
        amount_container = tk.Frame(
            amount_frame,
            bg=ModernColors.SURFACE_VARIANT,
            relief=tk.FLAT
        )
        amount_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        
        # Dollar sign
        tk.Label(
            amount_container,
            text="$",
            font=self.fonts['body1'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE_VARIANT
        ).pack(side=tk.LEFT, padx=(12, 4))
        
        # Amount entry
        self.amount_entry = tk.Entry(
            amount_container,
            textvariable=self.amount_var,
            font=self.fonts['body1'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE_VARIANT,
            relief=tk.FLAT,
            bd=0
        )
        self.amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=12)
        
        # Quick amount buttons
        quick_buttons = [
            ("Full", lambda: self.set_quick_amount("full"), ModernColors.SUCCESS),
            ("Half", lambda: self.set_quick_amount("half"), ModernColors.WARNING),
            ("Zero", lambda: self.set_quick_amount("zero"), ModernColors.ERROR)
        ]
        
        for text, command, color in quick_buttons:
            btn = self.create_modern_button(
                amount_frame,
                text,
                command,
                color,
                compact=True
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))
            
    def create_notes_section(self, parent):
        """Create modern notes section."""
        # Label
        tk.Label(
            parent,
            text="Notes (Optional)",
            font=self.fonts['subtitle1'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        ).pack(anchor=tk.W, pady=(0, 12))
        
        # Notes container with border
        notes_container = tk.Frame(
            parent,
            bg=ModernColors.SURFACE_VARIANT,
            relief=tk.FLAT
        )
        notes_container.pack(fill=tk.BOTH, expand=True, pady=(0, 24))
        
        # Notes text widget
        self.notes_text = tk.Text(
            notes_container,
            height=4,
            font=self.fonts['body2'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE_VARIANT,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=12,
            pady=12
        )
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
    def create_action_buttons(self, parent):
        """Create modern action buttons."""
        # Button container
        button_frame = tk.Frame(parent, bg=ModernColors.SURFACE)
        button_frame.pack(fill=tk.X)
        
        # Secondary actions
        secondary_frame = tk.Frame(button_frame, bg=ModernColors.SURFACE)
        secondary_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.create_modern_button(
            secondary_frame,
            "← Previous",
            self.previous_transaction,
            ModernColors.TEXT_SECONDARY,
            text_only=True
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.create_modern_button(
            secondary_frame,
            "Skip",
            self.skip_transaction,
            ModernColors.TEXT_SECONDARY,
            text_only=True
        ).pack(side=tk.LEFT)
        
        # Primary action
        self.save_button = self.create_modern_button(
            button_frame,
            "Save & Next →",
            self.save_and_next,
            ModernColors.PRIMARY
        )
        self.save_button.pack(side=tk.RIGHT)
        
    def create_stats_card(self):
        """Create statistics card at bottom."""
        # Stats card
        stats_card = self.create_card(self.main_container)
        stats_card.pack(fill=tk.X, pady=(20, 0))
        
        # Stats content
        stats_frame = tk.Frame(stats_card, bg=ModernColors.SURFACE)
        stats_frame.pack(fill=tk.X, padx=24, pady=16)
        
        # Session stats
        self.stats_label = tk.Label(
            stats_frame,
            text="Session Statistics",
            font=self.fonts['caption'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Quick actions on right
        quick_actions = tk.Frame(stats_frame, bg=ModernColors.SURFACE)
        quick_actions.pack(side=tk.RIGHT)
        
        self.create_modern_button(
            quick_actions,
            "Export",
            self.export_decisions,
            ModernColors.TEXT_SECONDARY,
            text_only=True,
            compact=True
        ).pack(side=tk.LEFT, padx=(0, 16))
        
        self.create_modern_button(
            quick_actions,
            "Help",
            self.show_help,
            ModernColors.TEXT_SECONDARY,
            text_only=True,
            compact=True
        ).pack(side=tk.LEFT)
        
    def create_card(self, parent: tk.Frame) -> tk.Frame:
        """Create a Material Design card with shadow."""
        # Shadow frame
        shadow_frame = tk.Frame(parent, bg=ModernColors.BACKGROUND)
        
        # Card
        card = tk.Frame(
            shadow_frame,
            bg=ModernColors.SURFACE,
            relief=tk.FLAT,
            bd=0
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        # Add subtle shadow effect (simplified for tkinter)
        shadow_frame.configure(highlightbackground=ModernColors.DIVIDER, highlightthickness=1)
        
        return card
        
    def create_divider(self, parent: tk.Frame):
        """Create a horizontal divider."""
        divider = tk.Frame(parent, bg=ModernColors.DIVIDER, height=1)
        divider.pack(fill=tk.X, padx=24)
        
    def create_modern_button(self, parent: tk.Frame, text: str, command: Callable,
                           color: str = None, text_only: bool = False,
                           compact: bool = False) -> tk.Button:
        """Create a modern styled button."""
        # Button styling
        if text_only:
            bg_color = ModernColors.SURFACE
            fg_color = color or ModernColors.PRIMARY
            hover_bg = ModernColors.HOVER
            hover_fg = color or ModernColors.PRIMARY_DARK
            active_bg = ModernColors.DIVIDER
        else:
            bg_color = color or ModernColors.PRIMARY
            fg_color = ModernColors.TEXT_ON_PRIMARY
            hover_bg = ModernColors.PRIMARY_DARK if color == ModernColors.PRIMARY else color
            hover_fg = ModernColors.TEXT_ON_PRIMARY
            active_bg = hover_bg
            
        # Create button
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts['button'] if not compact else self.fonts['caption'],
            fg=fg_color,
            bg=bg_color,
            relief=tk.FLAT,
            bd=0,
            padx=16 if not compact else 12,
            pady=10 if not compact else 6,
            cursor="hand2"
        )
        
        # Hover effects
        def on_enter(e):
            btn.configure(bg=hover_bg, fg=hover_fg)
            
        def on_leave(e):
            btn.configure(bg=bg_color, fg=fg_color)
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
        
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
            
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        
        # Get window size
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Set window position
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
    def load_pending_transactions(self):
        """Load transactions needing review."""
        try:
            # Get pending transactions from the review system
            self.transactions = self.review_system.get_pending_reviews()
            
            if self.transactions.empty:
                self.transactions = []
            else:
                # Convert to list of dicts with proper datetime objects
                transactions_list = []
                for _, row in self.transactions.iterrows():
                    transaction = row.to_dict()
                    # Parse date string to datetime if needed
                    if isinstance(transaction['date'], str):
                        transaction['date'] = datetime.fromisoformat(transaction['date'])
                    transactions_list.append(transaction)
                self.transactions = transactions_list
            
            self.stats['total'] = len(self.transactions)
            self.update_progress()
            
            if not self.transactions:
                self.show_completion_message()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {e}")
            self.root.quit()
            
    def show_current_transaction(self):
        """Display the current transaction with animation."""
        if not self.transactions or self.current_index >= len(self.transactions):
            self.show_completion_message()
            return
            
        self.current_transaction = self.transactions[self.current_index]
        
        # Update transaction badge
        self.transaction_badge.configure(text=f"#{self.current_index + 1}")
        
        # Animate transaction details
        self.animate_transaction_update()
        
        # Update progress
        self.update_progress()
        
    def animate_transaction_update(self):
        """Animate the transaction details update."""
        # Update transaction fields
        date_str = self.current_transaction['date'].strftime('%B %d, %Y')
        self.transaction_fields['date'].configure(text=date_str)
        
        # Clear and update description
        self.transaction_fields['description'].delete(1.0, tk.END)
        self.transaction_fields['description'].insert(1.0, self.current_transaction['description'])
        
        # Format amount with color
        amount = float(self.current_transaction['amount'])
        amount_str = f"${amount:,.2f}"
        self.transaction_fields['amount'].configure(
            text=amount_str,
            fg=ModernColors.ERROR if amount > 0 else ModernColors.SUCCESS
        )
        
        self.transaction_fields['payer'].configure(text=self.current_transaction['payer'])
        self.transaction_fields['source'].configure(
            text=self.current_transaction.get('source', 'Unknown')
        )
        
        # Reset review fields with animation
        self.reset_review_fields()
        
        # Load existing review if available
        self.load_existing_review()
        
    def reset_review_fields(self):
        """Reset review fields to default state."""
        self.category_var.set("")
        self.update_category_chips()
        
        # Reset amount to original
        self.amount_var.set(f"{float(self.current_transaction['amount']):.2f}")
        
        # Clear notes
        self.notes_text.delete(1.0, tk.END)
        
    def load_existing_review(self):
        """Load existing review decision if available."""
        try:
            review_id = self.current_transaction.get('review_id')
            if review_id:
                decision = self.review_system.get_review_by_id(review_id)
                if decision and decision['status'] != ReviewStatus.PENDING.value:
                    self.category_var.set(decision['category'])
                    self.update_category_chips()
                    self.amount_var.set(f"{decision['allowed_amount']:.2f}")
                    if decision['notes']:
                        self.notes_text.insert(1.0, decision['notes'])
        except Exception:
            pass  # No existing review, that's fine
            
    def update_category_chips(self):
        """Update the visual state of category chips."""
        selected = self.category_var.get()
        for value, chip in self.category_chips.items():
            if value == selected:
                # Selected state
                chip.configure(
                    highlightbackground=chip.color,
                    highlightthickness=2
                )
                chip.winfo_children()[0].configure(bg=chip.color)
                chip.radio.configure(
                    fg=ModernColors.TEXT_ON_PRIMARY,
                    bg=chip.color,
                    activebackground=chip.color,
                    selectcolor=chip.color
                )
            else:
                # Unselected state
                chip.configure(
                    highlightbackground=ModernColors.DIVIDER,
                    highlightthickness=1
                )
                chip.winfo_children()[0].configure(bg=ModernColors.SURFACE)
                chip.radio.configure(
                    fg=ModernColors.TEXT_PRIMARY,
                    bg=ModernColors.SURFACE,
                    activebackground=ModernColors.SURFACE,
                    selectcolor=ModernColors.SURFACE
                )
                
    def set_category(self, category: str):
        """Set the category and update UI."""
        self.category_var.set(category)
        self.on_category_change(category)
        
    def on_category_change(self, category: str = None):
        """Handle category selection changes."""
        if not category:
            category = self.category_var.get()
            
        self.update_category_chips()
        
        # Auto-adjust amount based on category
        original_amount = float(self.current_transaction['amount'])
        
        if category == 'personal':
            self.amount_var.set("0.00")
            self.animate_amount_change(0)
        elif category == 'settlement':
            self.amount_var.set(f"{original_amount:.2f}")
            self.animate_amount_change(original_amount)
        elif category in ['expense', 'rent']:
            # Default to full amount
            self.amount_var.set(f"{original_amount:.2f}")
            self.animate_amount_change(original_amount)
            
    def animate_amount_change(self, target_amount: float):
        """Animate amount change with visual feedback."""
        # Flash the amount entry background
        original_bg = self.amount_entry.cget('bg')
        self.amount_entry.configure(bg=ModernColors.ACCENT_LIGHT)
        self.root.after(200, lambda: self.amount_entry.configure(bg=original_bg))
        
    def set_quick_amount(self, action: str):
        """Set amount using quick buttons."""
        original_amount = float(self.current_transaction['amount'])
        
        if action == 'full':
            self.amount_var.set(f"{original_amount:.2f}")
            self.animate_amount_change(original_amount)
        elif action == 'half':
            half_amount = original_amount / 2
            self.amount_var.set(f"{half_amount:.2f}")
            self.animate_amount_change(half_amount)
        elif action == 'zero':
            self.amount_var.set("0.00")
            self.animate_amount_change(0)
            
    def save_current(self) -> bool:
        """Save the current review decision."""
        if not self.validate_review():
            return False
            
        try:
            # Map GUI categories to TransactionCategory enum values
            category_map = {
                'expense': TransactionCategory.OTHER,  # Generic expense
                'rent': TransactionCategory.RENT,
                'settlement': TransactionCategory.SETTLEMENT,
                'personal': TransactionCategory.OTHER  # Will use allowed_amount=0
            }
            category = category_map.get(self.category_var.get(), TransactionCategory.OTHER)
            allowed_amount = Decimal(self.amount_var.get())
            notes = self.notes_text.get(1.0, tk.END).strip()
            
            # Map categories to split types
            category_to_split = {
                'expense': SplitType.SPLIT_50_50,
                'rent': SplitType.RENT_SPLIT,
                'settlement': SplitType.SPLIT_50_50,
                'personal': SplitType.SPLIT_50_50  # Will be handled by allowed_amount
            }
            
            # Use the string value of category enum
            split_type = category_to_split.get(self.category_var.get(), SplitType.SPLIT_50_50)
            
            # Save the review decision
            review_id = self.current_transaction.get('review_id')
            success = self.review_system.review_transaction(
                review_id=review_id,
                category=category,
                split_type=split_type,
                allowed_amount=allowed_amount,
                notes=notes,
                reviewed_by='GUI User'
            )
            
            if success:
                self.stats['reviewed'] += 1
                self.show_save_feedback()
                return True
            else:
                messagebox.showerror("Error", "Failed to save review")
                return False
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save review: {e}")
            return False
            
    def show_save_feedback(self):
        """Show visual feedback when saving."""
        # Flash save button
        original_bg = self.save_button.cget('bg')
        self.save_button.configure(bg=ModernColors.SUCCESS)
        self.root.after(300, lambda: self.save_button.configure(bg=original_bg))
        
    def validate_review(self) -> bool:
        """Validate the current review decision."""
        if not self.category_var.get():
            self.show_validation_error("Please select a category")
            return False
            
        try:
            amount = Decimal(self.amount_var.get())
            if amount < 0:
                self.show_validation_error("Amount cannot be negative")
                return False
        except (ValueError, InvalidOperation):
            self.show_validation_error("Please enter a valid amount")
            return False
            
        return True
        
    def show_validation_error(self, message: str):
        """Show validation error with modern styling."""
        # Create custom error dialog
        error_dialog = tk.Toplevel(self.root)
        error_dialog.title("Validation Error")
        error_dialog.geometry("400x150")
        error_dialog.configure(bg=ModernColors.SURFACE)
        error_dialog.transient(self.root)
        
        # Center the dialog
        error_dialog.update_idletasks()
        x = (error_dialog.winfo_screenwidth() - 400) // 2
        y = (error_dialog.winfo_screenheight() - 150) // 2
        error_dialog.geometry(f"400x150+{x}+{y}")
        
        # Error content
        content_frame = tk.Frame(error_dialog, bg=ModernColors.SURFACE)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        # Error icon and message
        tk.Label(
            content_frame,
            text="⚠️  " + message,
            font=self.fonts['body1'],
            fg=ModernColors.ERROR,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 20))
        
        # OK button
        self.create_modern_button(
            content_frame,
            "OK",
            error_dialog.destroy,
            ModernColors.ERROR
        ).pack()
        
        # Make dialog modal
        error_dialog.grab_set()
        
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
            
            # Update progress bar width
            bar_width = int((progress / 100) * self.progress_container.winfo_width())
            self.progress_fill.place(width=bar_width)
            
            # Update progress label
            self.progress_label.configure(
                text=f"Reviewing transaction {self.current_index + 1} of {self.stats['total']} • {progress:.0f}% complete"
            )
            
        # Update session stats
        elapsed = datetime.now() - self.stats['session_start']
        elapsed_str = str(elapsed).split('.')[0]
        
        stats_text = (
            f"Reviewed: {self.stats['reviewed']} • "
            f"Skipped: {self.stats['skipped']} • "
            f"Time: {elapsed_str}"
        )
        self.stats_label.configure(text=stats_text)
        
    def show_completion_message(self):
        """Show completion message with modern design."""
        # Create completion dialog
        completion_dialog = tk.Toplevel(self.root)
        completion_dialog.title("Review Complete")
        completion_dialog.geometry("500x300")
        completion_dialog.configure(bg=ModernColors.SURFACE)
        completion_dialog.transient(self.root)
        
        # Center the dialog
        completion_dialog.update_idletasks()
        x = (completion_dialog.winfo_screenwidth() - 500) // 2
        y = (completion_dialog.winfo_screenheight() - 300) // 2
        completion_dialog.geometry(f"500x300+{x}+{y}")
        
        # Content
        content_frame = tk.Frame(completion_dialog, bg=ModernColors.SURFACE)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Success icon and title
        tk.Label(
            content_frame,
            text="✅",
            font=font.Font(size=48),
            fg=ModernColors.SUCCESS,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 16))
        
        tk.Label(
            content_frame,
            text="All transactions reviewed!",
            font=self.fonts['headline5'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 8))
        
        # Stats summary
        tk.Label(
            content_frame,
            text=f"You reviewed {self.stats['reviewed']} transactions",
            font=self.fonts['body1'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 24))
        
        # Action buttons
        button_frame = tk.Frame(content_frame, bg=ModernColors.SURFACE)
        button_frame.pack()
        
        self.create_modern_button(
            button_frame,
            "Export Results",
            lambda: [self.export_decisions(), completion_dialog.destroy()],
            ModernColors.PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 12))
        
        self.create_modern_button(
            button_frame,
            "Close",
            lambda: [completion_dialog.destroy(), self.quit_application()],
            ModernColors.TEXT_SECONDARY,
            text_only=True
        ).pack(side=tk.LEFT)
        
        # Make dialog modal
        completion_dialog.grab_set()
        
    def export_decisions(self):
        """Export all review decisions."""
        try:
            filename = f"review_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            decisions = self.review_system.export_reviews()
            decisions.to_csv(filename, index=False)
            
            # Show success message
            self.show_export_success(filename, len(decisions))
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
            
    def show_export_success(self, filename: str, count: int):
        """Show export success message."""
        success_dialog = tk.Toplevel(self.root)
        success_dialog.title("Export Successful")
        success_dialog.geometry("400x200")
        success_dialog.configure(bg=ModernColors.SURFACE)
        success_dialog.transient(self.root)
        
        # Center
        success_dialog.update_idletasks()
        x = (success_dialog.winfo_screenwidth() - 400) // 2
        y = (success_dialog.winfo_screenheight() - 200) // 2
        success_dialog.geometry(f"400x200+{x}+{y}")
        
        # Content
        content = tk.Frame(success_dialog, bg=ModernColors.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        
        tk.Label(
            content,
            text="✅  Export Complete",
            font=self.fonts['headline6'],
            fg=ModernColors.SUCCESS,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 16))
        
        tk.Label(
            content,
            text=f"Exported {count} decisions to:\n{filename}",
            font=self.fonts['body2'],
            fg=ModernColors.TEXT_SECONDARY,
            bg=ModernColors.SURFACE
        ).pack(pady=(0, 20))
        
        self.create_modern_button(
            content,
            "OK",
            success_dialog.destroy,
            ModernColors.PRIMARY
        ).pack()
        
        success_dialog.grab_set()
        
    def show_help(self):
        """Show help dialog with modern design."""
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("Help")
        help_dialog.geometry("600x500")
        help_dialog.configure(bg=ModernColors.SURFACE)
        help_dialog.transient(self.root)
        
        # Center
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() - 600) // 2
        y = (help_dialog.winfo_screenheight() - 500) // 2
        help_dialog.geometry(f"600x500+{x}+{y}")
        
        # Scrollable content
        canvas = tk.Canvas(help_dialog, bg=ModernColors.SURFACE, highlightthickness=0)
        scrollbar = tk.Scrollbar(help_dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernColors.SURFACE)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Help content
        content = tk.Frame(scrollable_frame, bg=ModernColors.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=32, pady=32)
        
        # Title
        tk.Label(
            content,
            text="Keyboard Shortcuts",
            font=self.fonts['headline5'],
            fg=ModernColors.TEXT_PRIMARY,
            bg=ModernColors.SURFACE
        ).pack(anchor=tk.W, pady=(0, 16))
        
        # Shortcuts
        shortcuts = [
            ("Category Selection", [
                ("E", "Set category to Expense"),
                ("R", "Set category to Rent"),
                ("S", "Set category to Settlement"),
                ("P", "Set category to Personal")
            ]),
            ("Navigation", [
                ("A", "Previous transaction"),
                ("D", "Save and next transaction"),
                ("Shift+S", "Skip transaction")
            ]),
            ("General", [
                ("F1", "Show this help"),
                ("Ctrl+S", "Save current"),
                ("Ctrl+Q / Escape", "Quit application")
            ])
        ]
        
        for section_title, items in shortcuts:
            # Section header
            tk.Label(
                content,
                text=section_title,
                font=self.fonts['subtitle1'],
                fg=ModernColors.TEXT_SECONDARY,
                bg=ModernColors.SURFACE
            ).pack(anchor=tk.W, pady=(12, 8))
            
            # Section items
            for key, description in items:
                item_frame = tk.Frame(content, bg=ModernColors.SURFACE)
                item_frame.pack(fill=tk.X, pady=4)
                
                # Key badge
                key_badge = tk.Label(
                    item_frame,
                    text=key,
                    font=self.fonts['caption'],
                    fg=ModernColors.TEXT_PRIMARY,
                    bg=ModernColors.SURFACE_VARIANT,
                    padx=8,
                    pady=4
                )
                key_badge.pack(side=tk.LEFT, padx=(20, 12))
                
                # Description
                tk.Label(
                    item_frame,
                    text=description,
                    font=self.fonts['body2'],
                    fg=ModernColors.TEXT_PRIMARY,
                    bg=ModernColors.SURFACE
                ).pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Close button
        button_frame = tk.Frame(help_dialog, bg=ModernColors.SURFACE)
        button_frame.pack(fill=tk.X, padx=32, pady=16)
        
        self.create_modern_button(
            button_frame,
            "Close",
            help_dialog.destroy,
            ModernColors.PRIMARY
        ).pack(side=tk.RIGHT)
        
        help_dialog.grab_set()
        
    def quit_application(self):
        """Quit the application with confirmation."""
        if self.stats['reviewed'] > 0:
            # Custom confirmation dialog
            confirm_dialog = tk.Toplevel(self.root)
            confirm_dialog.title("Confirm Exit")
            confirm_dialog.geometry("400x200")
            confirm_dialog.configure(bg=ModernColors.SURFACE)
            confirm_dialog.transient(self.root)
            
            # Center
            confirm_dialog.update_idletasks()
            x = (confirm_dialog.winfo_screenwidth() - 400) // 2
            y = (confirm_dialog.winfo_screenheight() - 200) // 2
            confirm_dialog.geometry(f"400x200+{x}+{y}")
            
            # Content
            content = tk.Frame(confirm_dialog, bg=ModernColors.SURFACE)
            content.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
            
            tk.Label(
                content,
                text="Are you sure you want to quit?",
                font=self.fonts['headline6'],
                fg=ModernColors.TEXT_PRIMARY,
                bg=ModernColors.SURFACE
            ).pack(pady=(0, 8))
            
            tk.Label(
                content,
                text=f"You have reviewed {self.stats['reviewed']} transactions.",
                font=self.fonts['body2'],
                fg=ModernColors.TEXT_SECONDARY,
                bg=ModernColors.SURFACE
            ).pack(pady=(0, 24))
            
            # Buttons
            button_frame = tk.Frame(content, bg=ModernColors.SURFACE)
            button_frame.pack()
            
            self.create_modern_button(
                button_frame,
                "Cancel",
                confirm_dialog.destroy,
                ModernColors.TEXT_SECONDARY,
                text_only=True
            ).pack(side=tk.LEFT, padx=(0, 12))
            
            self.create_modern_button(
                button_frame,
                "Quit",
                lambda: [confirm_dialog.destroy(), self.root.quit()],
                ModernColors.ERROR
            ).pack(side=tk.LEFT)
            
            confirm_dialog.grab_set()
        else:
            self.root.quit()
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the modern GUI application."""
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = "data/phase5_manual_reviews.db"
        
    try:
        app = ModernTransactionReviewGUI(db_path)
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()