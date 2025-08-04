#!/usr/bin/env python3
"""
Ultra Modern Financial Reconciliation GUI
========================================

A stunning, visually appealing interface for reviewing financial transactions
with modern design principles, smooth animations, and delightful user experience.

Features:
- Beautiful gradient backgrounds and glassmorphism effects
- Smooth animations and micro-interactions
- Card-based layout with depth and shadows
- Color-coded transaction categories
- Visual progress tracking
- Keyboard shortcuts for efficiency
- Dark/Light theme support
- Responsive design

Author: Claude (Anthropic)
Date: August 4, 2025
Version: 3.0.0
"""

import tkinter as tk
from tkinter import ttk, font
import customtkinter as ctk
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import math
import colorsys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.review.manual_review_system import (
    ManualReviewSystem, TransactionCategory, SplitType, ReviewStatus
)

# Configure CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class ModernPalette:
    """Ultra-modern color palette with gradients and effects."""
    
    # Primary gradient colors
    GRADIENT_START = "#667eea"  # Purple
    GRADIENT_END = "#764ba2"    # Deep Purple
    
    # Accent colors
    ACCENT_PRIMARY = "#f093fb"   # Pink
    ACCENT_SECONDARY = "#4facfe" # Blue
    ACCENT_SUCCESS = "#00f2fe"   # Cyan
    
    # Category colors with vibrancy
    CATEGORY_EXPENSE = "#ff6b6b"     # Coral Red
    CATEGORY_RENT = "#4ecdc4"        # Turquoise
    CATEGORY_SETTLEMENT = "#a8e6cf"  # Mint Green
    CATEGORY_PERSONAL = "#ffd93d"    # Golden Yellow
    CATEGORY_SHARED = "#95e1d3"      # Seafoam
    
    # Glassmorphism colors
    GLASS_WHITE = "#ffffff"
    GLASS_OVERLAY = "#ffffff80"
    GLASS_BORDER = "#ffffff20"
    
    # Dark theme colors
    DARK_BG = "#0f0e13"
    DARK_SURFACE = "#1a1825"
    DARK_ACCENT = "#7f5af0"
    
    # Text colors
    TEXT_LIGHT = "#ffffff"
    TEXT_DARK = "#2d3436"
    TEXT_MUTED = "#636e72"
    
    # UI States
    HOVER_OVERLAY = "#00000010"
    PRESSED_OVERLAY = "#00000020"
    SHADOW_COLOR = "#00000040"


class AnimatedButton(ctk.CTkButton):
    """Custom button with hover animations and effects."""
    
    def __init__(self, master, **kwargs):
        self.normal_color = kwargs.get('fg_color', ModernPalette.ACCENT_PRIMARY)
        self.hover_color = self._lighten_color(self.normal_color)
        
        super().__init__(master, **kwargs)
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
    def _lighten_color(self, color):
        """Lighten a color for hover effect."""
        # Convert hex to RGB
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        
        # Convert to HSL and increase lightness
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        l = min(1.0, l + 0.1)
        
        # Convert back to RGB
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        
        # Convert to hex
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        
    def _on_enter(self, event):
        self.configure(fg_color=self.hover_color)
        
    def _on_leave(self, event):
        self.configure(fg_color=self.normal_color)


class TransactionCard(ctk.CTkFrame):
    """Beautiful card component for displaying transaction details."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, corner_radius=20, **kwargs)
        
        # Add subtle shadow effect
        self.configure(border_width=1, border_color=ModernPalette.GLASS_BORDER)
        
        
class UltraModernReconciliationGUI:
    """Ultra-modern GUI for financial reconciliation with stunning visuals."""
    
    def __init__(self, review_db_path: str = "data/phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.current_transaction = None
        self.current_index = 0
        self.transactions = []
        self.theme = "light"
        
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
        """Create the main GUI with modern styling."""
        self.root = ctk.CTk()
        self.root.title("Financial Reconciliation • Modern Review Interface")
        self.root.geometry("1400x900")
        
        # Set window properties
        self.root.minsize(1200, 800)
        
        # Create gradient background
        self.create_gradient_background()
        
        # Create main interface
        self.create_main_interface()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Center window
        self.center_window()
        
    def create_gradient_background(self):
        """Create a beautiful gradient background."""
        self.gradient_frame = tk.Canvas(self.root, highlightthickness=0)
        self.gradient_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create gradient
        self.draw_gradient()
        
        # Main container on top of gradient
        self.main_container = ctk.CTkFrame(
            self.gradient_frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.gradient_frame.create_window(
            0, 0,
            anchor="nw",
            window=self.main_container,
            width=1400,
            height=900
        )
        
    def draw_gradient(self):
        """Draw a smooth gradient background."""
        width = 1400
        height = 900
        
        # Create gradient
        for i in range(height):
            # Calculate color
            ratio = i / height
            r1, g1, b1 = tuple(int(ModernPalette.GRADIENT_START[i:i+2], 16) for i in (1, 3, 5))
            r2, g2, b2 = tuple(int(ModernPalette.GRADIENT_END[i:i+2], 16) for i in (1, 3, 5))
            
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            
            color = f"#{r:02x}{g:02x}{b:02x}"
            
            self.gradient_frame.create_line(0, i, width, i, fill=color, width=1)
            
    def create_main_interface(self):
        """Create the main interface with glassmorphism cards."""
        # Header section
        self.create_header_section()
        
        # Content area with padding
        content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="transparent"
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Create three-column layout
        # Left: Transaction details
        left_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Center: Review controls
        center_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Right: Statistics
        right_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
        
        # Create cards
        self.create_transaction_details_card(left_frame)
        self.create_review_controls_card(center_frame)
        self.create_statistics_card(right_frame)
        
        # Bottom navigation
        self.create_navigation_bar()
        
    def create_header_section(self):
        """Create stunning header with title and progress."""
        header_frame = ctk.CTkFrame(
            self.main_container,
            fg_color=ModernPalette.GLASS_OVERLAY,
            corner_radius=0,
            height=120
        )
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Inner container
        inner_header = ctk.CTkFrame(header_frame, fg_color="transparent")
        inner_header.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Title with icon
        title_frame = ctk.CTkFrame(inner_header, fg_color="transparent")
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # App icon (emoji for simplicity)
        icon_label = ctk.CTkLabel(
            title_frame,
            text="💰",
            font=ctk.CTkFont(size=40)
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Title and subtitle
        text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        text_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = ctk.CTkLabel(
            text_frame,
            text="Transaction Review",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ctk.CTkLabel(
            text_frame,
            text="Financial Reconciliation System",
            font=ctk.CTkFont(size=14),
            text_color=ModernPalette.GLASS_WHITE
        )
        subtitle_label.pack(anchor="w")
        
        # Progress section
        progress_frame = ctk.CTkFrame(inner_header, fg_color="transparent")
        progress_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Progress stats
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0 of 0 reviewed",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        self.progress_label.pack(anchor="e", pady=(0, 5))
        
        # Modern progress bar
        self.progress_bar = ctk.CTkProgressBar(
            progress_frame,
            width=300,
            height=15,
            corner_radius=10,
            progress_color=ModernPalette.ACCENT_SUCCESS
        )
        self.progress_bar.pack(anchor="e")
        self.progress_bar.set(0)
        
    def create_transaction_details_card(self, parent):
        """Create glassmorphism card for transaction details."""
        # Main card
        card = TransactionCard(
            parent,
            fg_color=ModernPalette.GLASS_OVERLAY,
            border_color=ModernPalette.GLASS_BORDER
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        header_label = ctk.CTkLabel(
            header,
            text="Transaction Details",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        header_label.pack(side=tk.LEFT)
        
        # Transaction ID badge
        self.transaction_badge = ctk.CTkLabel(
            header,
            text="#1",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=ModernPalette.ACCENT_PRIMARY,
            text_color=ModernPalette.TEXT_LIGHT,
            corner_radius=15,
            width=60,
            height=30
        )
        self.transaction_badge.pack(side=tk.RIGHT)
        
        # Details container
        details_frame = ctk.CTkFrame(card, fg_color="transparent")
        details_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 30))
        
        # Create detail fields with icons
        self.detail_widgets = {}
        details = [
            ("Date", "date", "📅", None),
            ("Amount", "amount", "💵", self._format_amount),
            ("Description", "description", "📝", None),
            ("Payer", "payer", "👤", None),
            ("Bank", "source", "🏦", None)
        ]
        
        for label, field_id, icon, formatter in details:
            # Row frame
            row = ctk.CTkFrame(details_frame, fg_color="transparent", height=60)
            row.pack(fill=tk.X, pady=10)
            row.pack_propagate(False)
            
            # Icon
            icon_label = ctk.CTkLabel(
                row,
                text=icon,
                font=ctk.CTkFont(size=24),
                width=40
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 15))
            
            # Label and value container
            text_container = ctk.CTkFrame(row, fg_color="transparent")
            text_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Label
            label_widget = ctk.CTkLabel(
                text_container,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=ModernPalette.GLASS_WHITE,
                anchor="w"
            )
            label_widget.pack(fill=tk.X)
            
            # Value
            if field_id == "description":
                # Scrollable text for description
                value_widget = ctk.CTkTextbox(
                    text_container,
                    height=50,
                    fg_color=ModernPalette.GLASS_OVERLAY,
                    border_color=ModernPalette.GLASS_BORDER,
                    border_width=1,
                    corner_radius=10,
                    font=ctk.CTkFont(size=14)
                )
                value_widget.pack(fill=tk.X)
            else:
                value_widget = ctk.CTkLabel(
                    text_container,
                    text="",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=ModernPalette.TEXT_LIGHT,
                    anchor="w"
                )
                value_widget.pack(fill=tk.X)
                
            self.detail_widgets[field_id] = (value_widget, formatter)
            
    def create_review_controls_card(self, parent):
        """Create card for review actions."""
        # Main card
        card = TransactionCard(
            parent,
            fg_color=ModernPalette.GLASS_OVERLAY,
            border_color=ModernPalette.GLASS_BORDER
        )
        card.pack(fill=tk.BOTH, expand=True)
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill=tk.X, padx=30, pady=(30, 20))
        
        header_label = ctk.CTkLabel(
            header,
            text="Review Actions",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        header_label.pack()
        
        # Category selection
        category_frame = ctk.CTkFrame(card, fg_color="transparent")
        category_frame.pack(fill=tk.X, padx=30, pady=20)
        
        category_label = ctk.CTkLabel(
            category_frame,
            text="Select Category",
            font=ctk.CTkFont(size=14),
            text_color=ModernPalette.GLASS_WHITE
        )
        category_label.pack(pady=(0, 10))
        
        # Category buttons grid
        categories_grid = ctk.CTkFrame(category_frame, fg_color="transparent")
        categories_grid.pack()
        
        self.category_buttons = {}
        categories = [
            ("Shared Expense", TransactionCategory.SHARED_EXPENSE, ModernPalette.CATEGORY_SHARED, "🍽️"),
            ("Rent Payment", TransactionCategory.RENT_PAYMENT, ModernPalette.CATEGORY_RENT, "🏠"),
            ("Settlement", TransactionCategory.SETTLEMENT, ModernPalette.CATEGORY_SETTLEMENT, "💸"),
            ("Personal (Ryan)", TransactionCategory.PERSONAL_RYAN, ModernPalette.CATEGORY_PERSONAL, "👤"),
            ("Personal (Jordyn)", TransactionCategory.PERSONAL_JORDYN, ModernPalette.CATEGORY_EXPENSE, "👤")
        ]
        
        for i, (label, category, color, icon) in enumerate(categories):
            btn = AnimatedButton(
                categories_grid,
                text=f"{icon} {label}",
                fg_color=color,
                hover_color=color,
                text_color=ModernPalette.TEXT_DARK if color in [ModernPalette.CATEGORY_SETTLEMENT, ModernPalette.CATEGORY_PERSONAL] else ModernPalette.TEXT_LIGHT,
                corner_radius=15,
                height=50,
                font=ctk.CTkFont(size=14, weight="bold"),
                command=lambda c=category: self.select_category(c)
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            self.category_buttons[category] = btn
            
        # Configure grid
        categories_grid.grid_columnconfigure(0, weight=1)
        categories_grid.grid_columnconfigure(1, weight=1)
        
        # Amount input for splits
        self.amount_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.amount_frame.pack(fill=tk.X, padx=30, pady=20)
        
        amount_label = ctk.CTkLabel(
            self.amount_frame,
            text="Allowed Amount (for splits)",
            font=ctk.CTkFont(size=14),
            text_color=ModernPalette.GLASS_WHITE
        )
        amount_label.pack(pady=(0, 10))
        
        self.amount_entry = ctk.CTkEntry(
            self.amount_frame,
            placeholder_text="Enter amount...",
            font=ctk.CTkFont(size=16),
            height=40,
            corner_radius=10
        )
        self.amount_entry.pack(fill=tk.X)
        
        # Action buttons
        action_frame = ctk.CTkFrame(card, fg_color="transparent")
        action_frame.pack(fill=tk.X, padx=30, pady=(20, 30))
        
        # Submit button
        self.submit_btn = AnimatedButton(
            action_frame,
            text="✓ Submit Review",
            fg_color=ModernPalette.ACCENT_SUCCESS,
            hover_color=ModernPalette.ACCENT_SUCCESS,
            text_color=ModernPalette.TEXT_DARK,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.submit_review
        )
        self.submit_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Skip button
        self.skip_btn = AnimatedButton(
            action_frame,
            text="→ Skip for Now",
            fg_color=ModernPalette.GLASS_OVERLAY,
            hover_color=ModernPalette.GLASS_WHITE,
            text_color=ModernPalette.TEXT_LIGHT,
            border_width=2,
            border_color=ModernPalette.GLASS_BORDER,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.skip_transaction
        )
        self.skip_btn.pack(fill=tk.X)
        
    def create_statistics_card(self, parent):
        """Create card for session statistics."""
        # Main card
        card = TransactionCard(
            parent,
            fg_color=ModernPalette.GLASS_OVERLAY,
            border_color=ModernPalette.GLASS_BORDER,
            width=300
        )
        card.pack(fill=tk.Y)
        card.pack_propagate(False)
        
        # Card header
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill=tk.X, padx=20, pady=(20, 15))
        
        header_label = ctk.CTkLabel(
            header,
            text="Session Stats",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        header_label.pack()
        
        # Stats container
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create stat displays
        self.stat_widgets = {}
        stats = [
            ("Total", "total", "📊"),
            ("Reviewed", "reviewed", "✅"),
            ("Skipped", "skipped", "⏭️"),
            ("Remaining", "remaining", "⏳")
        ]
        
        for label, stat_id, icon in stats:
            # Stat row
            stat_row = ctk.CTkFrame(stats_frame, fg_color="transparent", height=60)
            stat_row.pack(fill=tk.X, pady=10)
            stat_row.pack_propagate(False)
            
            # Left side - icon and label
            left_frame = ctk.CTkFrame(stat_row, fg_color="transparent")
            left_frame.pack(side=tk.LEFT, fill=tk.Y)
            
            icon_label = ctk.CTkLabel(
                left_frame,
                text=icon,
                font=ctk.CTkFont(size=20),
                width=30
            )
            icon_label.pack(side=tk.LEFT)
            
            label_widget = ctk.CTkLabel(
                left_frame,
                text=label,
                font=ctk.CTkFont(size=14),
                text_color=ModernPalette.GLASS_WHITE
            )
            label_widget.pack(side=tk.LEFT, padx=(5, 0))
            
            # Right side - value
            value_widget = ctk.CTkLabel(
                stat_row,
                text="0",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color=ModernPalette.TEXT_LIGHT
            )
            value_widget.pack(side=tk.RIGHT)
            
            self.stat_widgets[stat_id] = value_widget
            
        # Session time
        time_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        time_frame.pack(fill=tk.X, pady=(20, 0))
        
        time_label = ctk.CTkLabel(
            time_frame,
            text="⏱️ Session Time",
            font=ctk.CTkFont(size=14),
            text_color=ModernPalette.GLASS_WHITE
        )
        time_label.pack()
        
        self.time_label = ctk.CTkLabel(
            time_frame,
            text="00:00:00",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=ModernPalette.TEXT_LIGHT
        )
        self.time_label.pack()
        
        # Update timer
        self.update_session_time()
        
    def create_navigation_bar(self):
        """Create bottom navigation bar."""
        nav_bar = ctk.CTkFrame(
            self.main_container,
            fg_color=ModernPalette.GLASS_OVERLAY,
            corner_radius=0,
            height=80
        )
        nav_bar.pack(side=tk.BOTTOM, fill=tk.X)
        nav_bar.pack_propagate(False)
        
        # Inner container
        inner_nav = ctk.CTkFrame(nav_bar, fg_color="transparent")
        inner_nav.pack(fill=tk.BOTH, expand=True, padx=40, pady=15)
        
        # Previous button
        self.prev_btn = AnimatedButton(
            inner_nav,
            text="← Previous",
            fg_color=ModernPalette.GLASS_OVERLAY,
            hover_color=ModernPalette.GLASS_WHITE,
            text_color=ModernPalette.TEXT_LIGHT,
            border_width=2,
            border_color=ModernPalette.GLASS_BORDER,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.previous_transaction
        )
        self.prev_btn.pack(side=tk.LEFT)
        
        # Center info
        center_frame = ctk.CTkFrame(inner_nav, fg_color="transparent")
        center_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.nav_info_label = ctk.CTkLabel(
            center_frame,
            text="Transaction 1 of 1",
            font=ctk.CTkFont(size=16),
            text_color=ModernPalette.TEXT_LIGHT
        )
        self.nav_info_label.pack()
        
        # Keyboard shortcuts hint
        shortcuts_label = ctk.CTkLabel(
            center_frame,
            text="⌨️ Shortcuts: Enter=Submit, Space=Skip, ←/→=Navigate",
            font=ctk.CTkFont(size=12),
            text_color=ModernPalette.GLASS_WHITE
        )
        shortcuts_label.pack()
        
        # Next button
        self.next_btn = AnimatedButton(
            inner_nav,
            text="Next →",
            fg_color=ModernPalette.GLASS_OVERLAY,
            hover_color=ModernPalette.GLASS_WHITE,
            text_color=ModernPalette.TEXT_LIGHT,
            border_width=2,
            border_color=ModernPalette.GLASS_BORDER,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self.next_transaction
        )
        self.next_btn.pack(side=tk.RIGHT)
        
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for efficiency."""
        self.root.bind('<Return>', lambda e: self.submit_review())
        self.root.bind('<space>', lambda e: self.skip_transaction())
        self.root.bind('<Left>', lambda e: self.previous_transaction())
        self.root.bind('<Right>', lambda e: self.next_transaction())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
        # Number keys for category selection
        self.root.bind('1', lambda e: self.select_category(TransactionCategory.SHARED_EXPENSE))
        self.root.bind('2', lambda e: self.select_category(TransactionCategory.RENT_PAYMENT))
        self.root.bind('3', lambda e: self.select_category(TransactionCategory.SETTLEMENT))
        self.root.bind('4', lambda e: self.select_category(TransactionCategory.PERSONAL_RYAN))
        self.root.bind('5', lambda e: self.select_category(TransactionCategory.PERSONAL_JORDYN))
        
    def center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def load_pending_transactions(self):
        """Load all pending transactions."""
        try:
            df = self.review_system.get_pending_reviews()
            self.transactions = df.to_dict('records') if not df.empty else []
            self.stats['total'] = len(self.transactions)
            self.update_display()
        except Exception as e:
            print(f"Error loading transactions: {e}")
            self.transactions = []
            
    def show_current_transaction(self):
        """Display the current transaction details."""
        if not self.transactions or self.current_index >= len(self.transactions):
            self.show_completion_message()
            return
            
        self.current_transaction = self.transactions[self.current_index]
        
        # Update transaction details
        for field_id, (widget, formatter) in self.detail_widgets.items():
            value = self.current_transaction.get(field_id, "")
            
            if formatter:
                value = formatter(value)
                
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", str(value))
            else:
                widget.configure(text=str(value))
                
        # Update badge
        self.transaction_badge.configure(text=f"#{self.current_index + 1}")
        
        # Update navigation
        self.nav_info_label.configure(
            text=f"Transaction {self.current_index + 1} of {len(self.transactions)}"
        )
        
        # Update button states
        self.prev_btn.configure(state="normal" if self.current_index > 0 else "disabled")
        self.next_btn.configure(state="normal" if self.current_index < len(self.transactions) - 1 else "disabled")
        
        # Clear previous selection
        self.selected_category = None
        for btn in self.category_buttons.values():
            btn.configure(border_width=0)
            
        # Clear amount entry
        self.amount_entry.delete(0, tk.END)
        
    def select_category(self, category: TransactionCategory):
        """Select a transaction category."""
        self.selected_category = category
        
        # Update button appearance
        for cat, btn in self.category_buttons.items():
            if cat == category:
                btn.configure(border_width=3, border_color=ModernPalette.TEXT_LIGHT)
            else:
                btn.configure(border_width=0)
                
        # Show/hide amount entry based on category
        if category == TransactionCategory.SHARED_EXPENSE:
            self.amount_frame.pack(fill=tk.X, padx=30, pady=20)
        else:
            self.amount_frame.pack_forget()
            
    def submit_review(self):
        """Submit the current review."""
        if not self.current_transaction or not hasattr(self, 'selected_category'):
            return
            
        try:
            # Get allowed amount if applicable
            allowed_amount = None
            if self.selected_category == TransactionCategory.SHARED_EXPENSE:
                amount_text = self.amount_entry.get()
                if amount_text:
                    allowed_amount = Decimal(amount_text)
                    
            # Submit review
            self.review_system.review_transaction(
                review_id=self.current_transaction['id'],
                category=self.selected_category,
                allowed_amount=allowed_amount,
                split_type=SplitType.NONE,
                notes=f"Reviewed via Ultra Modern GUI at {datetime.now()}"
            )
            
            # Update stats
            self.stats['reviewed'] += 1
            
            # Move to next
            self.current_index += 1
            self.show_current_transaction()
            self.update_display()
            
        except Exception as e:
            print(f"Error submitting review: {e}")
            
    def skip_transaction(self):
        """Skip the current transaction."""
        if not self.current_transaction:
            return
            
        self.stats['skipped'] += 1
        self.current_index += 1
        self.show_current_transaction()
        self.update_display()
        
    def previous_transaction(self):
        """Go to previous transaction."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_current_transaction()
            
    def next_transaction(self):
        """Go to next transaction."""
        if self.current_index < len(self.transactions) - 1:
            self.current_index += 1
            self.show_current_transaction()
            
    def update_display(self):
        """Update all display elements."""
        # Update progress
        progress = self.stats['reviewed'] / self.stats['total'] if self.stats['total'] > 0 else 0
        self.progress_bar.set(progress)
        self.progress_label.configure(
            text=f"{self.stats['reviewed']} of {self.stats['total']} reviewed"
        )
        
        # Update stats
        self.stat_widgets['total'].configure(text=str(self.stats['total']))
        self.stat_widgets['reviewed'].configure(text=str(self.stats['reviewed']))
        self.stat_widgets['skipped'].configure(text=str(self.stats['skipped']))
        self.stat_widgets['remaining'].configure(
            text=str(self.stats['total'] - self.stats['reviewed'] - self.stats['skipped'])
        )
        
    def update_session_time(self):
        """Update session timer."""
        if hasattr(self, 'time_label'):
            elapsed = datetime.now() - self.stats['session_start']
            hours, remainder = divmod(elapsed.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label.configure(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            
        # Schedule next update
        self.root.after(1000, self.update_session_time)
        
    def show_completion_message(self):
        """Show completion message when all transactions are reviewed."""
        # Clear transaction details
        for field_id, (widget, _) in self.detail_widgets.items():
            if isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", tk.END)
                widget.insert("1.0", "No more transactions!")
            else:
                widget.configure(text="—")
                
        # Disable buttons
        self.submit_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        
        # Show completion in nav
        self.nav_info_label.configure(text="✨ All transactions reviewed!")
        
    def _format_amount(self, amount):
        """Format amount with currency symbol."""
        try:
            return f"${float(amount):,.2f}"
        except:
            return str(amount)
            
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = UltraModernReconciliationGUI()
    app.run()


if __name__ == "__main__":
    main()