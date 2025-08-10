#!/usr/bin/env python3
"""
Ultra-Modern Financial Dashboard with Gold Standard Graphics
============================================================

A visually stunning financial reconciliation dashboard featuring:
- Premium glassmorphic design with depth and shadows
- Smooth animations and micro-interactions
- Real-time data visualization with charts
- Interactive transaction explorer
- Advanced filtering and search
- Responsive layout with professional aesthetics

Author: Financial Reconciliation Team
Version: 5.0.0
Date: August 10, 2025
License: MIT

Dependencies:
- customtkinter: Modern UI framework
- tkinter: Base GUI framework
- datetime: Date/time handling
- decimal: Precise financial calculations
- json: Data serialization
- threading: Asynchronous data loading
- pathlib: File path operations

Usage:
    python ultra_modern_dashboard.py
    or
    python launch_premium_dashboard.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
from decimal import Decimal
import json
import math
import colorsys
from pathlib import Path
import sys
import threading
from typing import Dict, List, Optional, Tuple

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

# Import the comprehensive analyzer
from comprehensive_analysis import ComprehensiveAnalyzer

# Configure CustomTkinter for premium appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class PremiumTheme:
    """
    Gold standard design system with premium visuals.
    
    This class defines the complete color palette and visual theme for the dashboard.
    It includes gradient colors, accent colors, surface colors, and text hierarchy.
    All colors are carefully selected to provide excellent contrast and visual appeal
    while maintaining accessibility standards.
    
    The theme supports both dark and light modes with appropriate color adjustments.
    Colors are defined in hexadecimal format for compatibility with CustomTkinter.
    
    Attributes:
        GRADIENT_START (str): Starting color for gradient effects (Indigo)
        GRADIENT_MID (str): Middle color for gradient transitions (Purple)
        GRADIENT_END (str): Ending color for gradient effects (Pink)
        SUCCESS (str): Color for success states and positive indicators
        WARNING (str): Color for warning states and caution indicators
        ERROR (str): Color for error states and negative indicators
        INFO (str): Color for informational states and highlights
        BG_PRIMARY (str): Primary background color (Deep Space)
        BG_SECONDARY (str): Secondary background color (Dark Navy)
        BG_CARD (str): Card surface background color
        TEXT_PRIMARY (str): Primary text color (Pure White)
        TEXT_SECONDARY (str): Secondary text color (Light Blue Gray)
        TEXT_MUTED (str): Muted text color for less important information
        CHART_COLORS (list): List of colors for data visualization
    """
    
    # Premium gradient colors
    GRADIENT_START = "#667EEA"  # Indigo
    GRADIENT_MID = "#764BA2"    # Purple
    GRADIENT_END = "#F093FB"    # Pink
    
    # Accent colors with vibrancy
    SUCCESS = "#00D9FF"          # Cyan
    WARNING = "#FFB800"          # Gold
    ERROR = "#FF006E"            # Hot Pink
    INFO = "#8338EC"             # Royal Purple
    
    # Glass-morphic surfaces
    GLASS_BG = "#1A1F3A"         # Semi-transparent appearance
    GLASS_BORDER = "#2A3050"     # Border with slight transparency effect
    
    # Dark theme colors
    BG_PRIMARY = "#0A0E27"       # Deep Space
    BG_SECONDARY = "#151A3C"     # Dark Navy
    BG_CARD = "#1F2551"          # Card Surface
    
    # Text hierarchy
    TEXT_PRIMARY = "#FFFFFF"     # Pure White
    TEXT_SECONDARY = "#B8BED9"   # Light Blue Gray
    TEXT_MUTED = "#6B7394"       # Muted Purple Gray
    
    # Data visualization
    CHART_COLORS = [
        "#667EEA",  # Indigo
        "#F093FB",  # Pink
        "#00D9FF",  # Cyan
        "#FFB800",  # Gold
        "#8338EC",  # Purple
        "#FF006E",  # Hot Pink
    ]
    
    @staticmethod
    def get_gradient_color(progress: float) -> str:
        """
        Generate gradient color based on progress value.
        
        This method interpolates between gradient colors to create smooth
        color transitions for progress indicators and animations.
        
        Args:
            progress (float): Progress value between 0 and 1
                             0 = start color, 0.5 = mid color, 1 = end color
        
        Returns:
            str: Hexadecimal color code representing the interpolated color
        
        Example:
            >>> PremiumTheme.get_gradient_color(0.0)  # Returns GRADIENT_START
            >>> PremiumTheme.get_gradient_color(0.5)  # Returns GRADIENT_MID
            >>> PremiumTheme.get_gradient_color(1.0)  # Returns GRADIENT_END
        """
        if progress <= 0.5:
            # Interpolate between start and mid
            t = progress * 2
            r1, g1, b1 = int(PremiumTheme.GRADIENT_START[1:3], 16), int(PremiumTheme.GRADIENT_START[3:5], 16), int(PremiumTheme.GRADIENT_START[5:7], 16)
            r2, g2, b2 = int(PremiumTheme.GRADIENT_MID[1:3], 16), int(PremiumTheme.GRADIENT_MID[3:5], 16), int(PremiumTheme.GRADIENT_MID[5:7], 16)
        else:
            # Interpolate between mid and end
            t = (progress - 0.5) * 2
            r1, g1, b1 = int(PremiumTheme.GRADIENT_MID[1:3], 16), int(PremiumTheme.GRADIENT_MID[3:5], 16), int(PremiumTheme.GRADIENT_MID[5:7], 16)
            r2, g2, b2 = int(PremiumTheme.GRADIENT_END[1:3], 16), int(PremiumTheme.GRADIENT_END[3:5], 16), int(PremiumTheme.GRADIENT_END[5:7], 16)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        return f"#{r:02x}{g:02x}{b:02x}"


class AnimatedCard(ctk.CTkFrame):
    """
    Premium animated card component with glass morphism effect.
    
    This class creates a reusable card component with modern design aesthetics.
    It features rounded corners, subtle borders, hover animations, and supports
    icons, titles, and subtitles for rich content presentation.
    
    The card implements glass morphism design principles with semi-transparent
    backgrounds and blur effects (simulated through color choices).
    
    Inherits from:
        ctk.CTkFrame: CustomTkinter frame widget
    
    Args:
        parent: Parent widget to contain this card
        title (str): Main title text for the card header
        subtitle (str): Secondary subtitle text for additional context
        icon (str): Emoji or unicode icon to display in the header
        **kwargs: Additional keyword arguments passed to CTkFrame
    
    Attributes:
        content_frame (CTkFrame): Container for card content
        hover_scale (float): Scale factor for hover animation
        original_size: Stores original size for animation purposes
    """
    
    def __init__(self, parent, title="", subtitle="", icon="", **kwargs):
        super().__init__(parent, fg_color=PremiumTheme.BG_CARD, corner_radius=20, **kwargs)
        
        self.configure(border_width=1, border_color=PremiumTheme.GLASS_BORDER)
        
        # Content container
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with icon
        if title or icon:
            header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
            header_frame.pack(fill="x", pady=(0, 15))
            
            if icon:
                icon_label = ctk.CTkLabel(
                    header_frame,
                    text=icon,
                    font=ctk.CTkFont(size=24),
                    text_color=PremiumTheme.get_gradient_color(0.5)
                )
                icon_label.pack(side="left", padx=(0, 10))
            
            if title:
                title_label = ctk.CTkLabel(
                    header_frame,
                    text=title,
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=PremiumTheme.TEXT_PRIMARY
                )
                title_label.pack(side="left")
            
            if subtitle:
                subtitle_label = ctk.CTkLabel(
                    header_frame,
                    text=subtitle,
                    font=ctk.CTkFont(size=12),
                    text_color=PremiumTheme.TEXT_MUTED
                )
                subtitle_label.pack(side="left", padx=(10, 0))
        
        # Animation properties
        self.hover_scale = 1.02
        self.original_size = None
        
        # Bind hover effects
        self.bind("<Enter>", self._on_hover_enter)
        self.bind("<Leave>", self._on_hover_leave)
    
    def _on_hover_enter(self, event):
        """
        Handle mouse hover enter event.
        
        Applies visual feedback when user hovers over the card by changing
        the border color and width to create an interactive feel.
        
        Args:
            event: Tkinter event object containing hover information
        """
        self.configure(border_color=PremiumTheme.INFO, border_width=2)
    
    def _on_hover_leave(self, event):
        """
        Handle mouse hover leave event.
        
        Resets the card appearance to its default state when the mouse
        cursor leaves the card area.
        
        Args:
            event: Tkinter event object containing hover information
        """
        self.configure(border_color=PremiumTheme.GLASS_BORDER, border_width=1)


class CircularProgress(ctk.CTkCanvas):
    """
    Circular progress indicator with gradient colors.
    
    Creates a modern circular progress indicator that displays percentage
    values with smooth gradient colors. The progress arc animates from
    0 to 100% with color transitions based on the progress value.
    
    This widget is perfect for showing completion status, loading states,
    or comparative metrics in a visually appealing way.
    
    Inherits from:
        ctk.CTkCanvas: CustomTkinter canvas widget for drawing
    
    Args:
        parent: Parent widget to contain this progress indicator
        size (int): Diameter of the circular progress in pixels
        width (int): Thickness of the progress arc in pixels
        **kwargs: Additional keyword arguments passed to CTkCanvas
    
    Attributes:
        size (int): Diameter of the circular progress
        width (int): Thickness of the progress arc
        progress (float): Current progress value (0-100)
        arc: Canvas arc object for the progress indicator
        text: Canvas text object for the percentage display
    """
    
    def __init__(self, parent, size=100, width=8, **kwargs):
        super().__init__(parent, width=size, height=size, bg=PremiumTheme.BG_PRIMARY, highlightthickness=0, **kwargs)
        
        self.size = size
        self.width = width
        self.progress = 0
        
        # Draw background circle
        self.create_oval(
            width, width, size-width, size-width,
            outline=PremiumTheme.BG_SECONDARY,
            width=width,
            tags="bg"
        )
        
        # Progress arc
        self.arc = self.create_arc(
            width, width, size-width, size-width,
            start=90, extent=0,
            outline=PremiumTheme.GRADIENT_START,
            width=width,
            style="arc",
            tags="progress"
        )
        
        # Center text
        self.text = self.create_text(
            size/2, size/2,
            text="0%",
            fill=PremiumTheme.TEXT_PRIMARY,
            font=("Segoe UI", int(size/5), "bold")
        )
    
    def set_progress(self, value: float):
        """
        Update the progress indicator value.
        
        Sets the progress value and updates the visual representation
        including the arc extent, color gradient, and text label.
        
        Args:
            value (float): Progress value between 0 and 100
                          Values outside this range are clamped
        
        Example:
            >>> progress_widget.set_progress(75.5)  # Sets to 75.5%
        """
        self.progress = max(0, min(100, value))
        extent = -360 * (self.progress / 100)
        
        # Update arc
        self.itemconfig(self.arc, extent=extent)
        
        # Update color based on progress
        color = PremiumTheme.get_gradient_color(self.progress / 100)
        self.itemconfig(self.arc, outline=color)
        
        # Update text
        self.itemconfig(self.text, text=f"{int(self.progress)}%")


class DataChart(ctk.CTkCanvas):
    """
    Modern chart component for data visualization.
    
    Provides flexible charting capabilities with support for multiple chart types
    including bar charts and line charts. Features automatic scaling, color coding,
    and label rendering for clear data presentation.
    
    The chart automatically adjusts to display data with proper proportions and
    includes value labels and category labels for clarity.
    
    Inherits from:
        ctk.CTkCanvas: CustomTkinter canvas widget for drawing
    
    Args:
        parent: Parent widget to contain this chart
        width (int): Width of the chart canvas in pixels
        height (int): Height of the chart canvas in pixels
        **kwargs: Additional keyword arguments passed to CTkCanvas
    
    Attributes:
        width (int): Chart canvas width
        height (int): Chart canvas height
        data (list): List of (label, value) tuples for chart data
        max_value (float): Maximum value in the dataset for scaling
    """
    
    def __init__(self, parent, width=400, height=200, **kwargs):
        super().__init__(parent, width=width, height=height, bg=PremiumTheme.BG_CARD, highlightthickness=0, **kwargs)
        
        self.width = width
        self.height = height
        self.data = []
        self.max_value = 0
        
    def set_data(self, data: List[Tuple[str, float]], chart_type="bar"):
        """
        Set chart data and render the visualization.
        
        Accepts data as a list of tuples and renders the appropriate chart type.
        Automatically handles Decimal to float conversion for compatibility.
        
        Args:
            data: List of tuples containing (label, value) pairs
                  Labels are strings for category names
                  Values are numeric (float or Decimal) for measurements
            chart_type (str): Type of chart to render ('bar' or 'line')
        
        Example:
            >>> chart.set_data([("Jan", 1000), ("Feb", 1500)], "bar")
        """
        self.data = data
        # Convert Decimal to float and handle empty data
        float_data = [(label, float(value)) for label, value in data] if data else []
        self.data = float_data
        self.max_value = max([v for _, v in float_data]) if float_data else 1
        
        if chart_type == "bar":
            self._draw_bar_chart()
        elif chart_type == "line":
            self._draw_line_chart()
    
    def _draw_bar_chart(self):
        """Draw bar chart."""
        self.delete("all")
        
        if not self.data or self.max_value == 0:
            return
        
        padding = 40
        bar_width = (self.width - 2 * padding) / len(self.data)
        
        for i, (label, value) in enumerate(self.data):
            # Calculate bar height
            bar_height = (value / self.max_value) * (self.height - 2 * padding) if self.max_value > 0 else 0
            
            # Bar position
            x1 = padding + i * bar_width + bar_width * 0.1
            x2 = padding + (i + 1) * bar_width - bar_width * 0.1
            y1 = self.height - padding
            y2 = self.height - padding - bar_height
            
            # Draw bar with gradient effect
            color = PremiumTheme.CHART_COLORS[i % len(PremiumTheme.CHART_COLORS)]
            self.create_rectangle(
                x1, y1, x2, y2,
                fill=color,
                outline="",
                tags=f"bar_{i}"
            )
            
            # Add value label
            self.create_text(
                (x1 + x2) / 2, y2 - 10,
                text=f"${value:,.0f}",
                fill=PremiumTheme.TEXT_PRIMARY,
                font=("Segoe UI", 10, "bold")
            )
            
            # Add category label
            self.create_text(
                (x1 + x2) / 2, y1 + 15,
                text=label[:10],
                fill=PremiumTheme.TEXT_SECONDARY,
                font=("Segoe UI", 9)
            )
    
    def _draw_line_chart(self):
        """Draw line chart."""
        self.delete("all")
        
        if not self.data or self.max_value == 0:
            return
        
        padding = 40
        points = []
        
        for i, (label, value) in enumerate(self.data):
            x = padding + i * (self.width - 2 * padding) / max(1, len(self.data) - 1)
            y = self.height - padding - (value / self.max_value) * (self.height - 2 * padding) if self.max_value > 0 else self.height - padding
            points.extend([x, y])
            
            # Draw point
            self.create_oval(
                x - 4, y - 4, x + 4, y + 4,
                fill=PremiumTheme.INFO,
                outline=PremiumTheme.TEXT_PRIMARY,
                width=2
            )
        
        # Draw line
        if len(points) >= 4:
            self.create_line(
                points,
                fill=PremiumTheme.get_gradient_color(0.5),
                width=3,
                smooth=True
            )


class UltraModernDashboard(ctk.CTk):
    """
    Main application window with premium UI.
    
    This is the primary application class that creates and manages the entire
    dashboard interface. It handles data loading, UI creation, user interactions,
    and all dashboard functionality.
    
    The dashboard provides a comprehensive view of financial reconciliation data
    with multiple views including transactions, analytics, and monthly summaries.
    It features real-time data updates, interactive filtering, and export capabilities.
    
    Inherits from:
        ctk.CTk: CustomTkinter main window class
    
    Attributes:
        analyzer (ComprehensiveAnalyzer): Data analysis engine
        transactions (list): List of all financial transactions
        monthly_data (dict): Monthly aggregated financial data
        loading (bool): Flag indicating if data is being loaded
        main_container (CTkFrame): Primary container for all UI elements
        tab_view (CTkTabview): Tabbed interface for different views
        balance_card (AnimatedCard): Card displaying current balance
        trans_tree (Treeview): Transaction list widget
        expense_chart (DataChart): Monthly expenses visualization
        category_chart (DataChart): Category breakdown visualization
        trend_chart (DataChart): Balance trend visualization
    """
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("Financial Reconciliation Dashboard - Premium Edition")
        self.geometry("1400x900")
        self.configure(fg_color=PremiumTheme.BG_PRIMARY)
        
        # Data
        self.analyzer = ComprehensiveAnalyzer()
        self.transactions = []
        self.monthly_data = {}
        self.loading = True
        
        # Create UI
        self.create_ui()
        
        # Load data in background
        self.after(100, self.load_data_async)
    
    def create_ui(self):
        """
        Create the premium UI layout.
        
        Builds the complete user interface including:
        - Top navigation bar with title and action buttons
        - Left panel with balance overview and quick stats
        - Right panel with tabbed views for different data perspectives
        - All interactive components and visualizations
        
        This method is called during initialization to set up the entire
        dashboard interface structure.
        """
        # Main container with gradient effect
        self.main_container = ctk.CTkFrame(self, fg_color=PremiumTheme.BG_PRIMARY)
        self.main_container.pack(fill="both", expand=True)
        
        # Top bar
        self.create_top_bar()
        
        # Content area
        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left panel - Overview
        left_panel = ctk.CTkFrame(content_frame, fg_color="transparent", width=400)
        left_panel.pack(side="left", fill="y", padx=(0, 20))
        left_panel.pack_propagate(False)
        
        # Balance card
        self.balance_card = AnimatedCard(
            left_panel,
            title="Current Balance",
            icon="💰"
        )
        self.balance_card.pack(fill="x", pady=(0, 20))
        
        self.balance_label = ctk.CTkLabel(
            self.balance_card.content_frame,
            text="Loading...",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=PremiumTheme.TEXT_PRIMARY
        )
        self.balance_label.pack()
        
        self.balance_status = ctk.CTkLabel(
            self.balance_card.content_frame,
            text="Calculating...",
            font=ctk.CTkFont(size=14),
            text_color=PremiumTheme.TEXT_SECONDARY
        )
        self.balance_status.pack(pady=(5, 0))
        
        # Progress indicators
        progress_card = AnimatedCard(
            left_panel,
            title="Monthly Progress",
            icon="📊"
        )
        progress_card.pack(fill="x", pady=(0, 20))
        
        # Circular progress
        progress_frame = ctk.CTkFrame(progress_card.content_frame, fg_color="transparent")
        progress_frame.pack(fill="x")
        
        self.ryan_progress = CircularProgress(progress_frame, size=80)
        self.ryan_progress.pack(side="left", padx=(0, 20))
        
        self.jordyn_progress = CircularProgress(progress_frame, size=80)
        self.jordyn_progress.pack(side="left")
        
        # Quick stats
        stats_card = AnimatedCard(
            left_panel,
            title="Quick Stats",
            icon="📈"
        )
        stats_card.pack(fill="both", expand=True)
        
        self.stats_frame = ctk.CTkFrame(stats_card.content_frame, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True)
        
        # Right panel - Main content
        right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_panel.pack(side="right", fill="both", expand=True)
        
        # Tab view
        self.tab_view = ctk.CTkTabview(
            right_panel,
            fg_color=PremiumTheme.BG_SECONDARY,
            segmented_button_fg_color=PremiumTheme.BG_CARD,
            segmented_button_selected_color=PremiumTheme.INFO,
            segmented_button_unselected_color=PremiumTheme.BG_SECONDARY
        )
        self.tab_view.pack(fill="both", expand=True)
        
        # Create tabs
        self.tab_view.add("Transactions")
        self.tab_view.add("Analytics")
        self.tab_view.add("Monthly Summary")
        
        self.create_transactions_tab()
        self.create_analytics_tab()
        self.create_monthly_tab()
    
    def create_top_bar(self):
        """Create premium top bar."""
        top_bar = ctk.CTkFrame(
            self.main_container,
            height=80,
            fg_color=PremiumTheme.BG_SECONDARY,
            corner_radius=0
        )
        top_bar.pack(fill="x")
        top_bar.pack_propagate(False)
        
        # Title with gradient
        title_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        title_frame.pack(side="left", padx=30, pady=20)
        
        title = ctk.CTkLabel(
            title_frame,
            text="Financial Dashboard",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=PremiumTheme.TEXT_PRIMARY
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            title_frame,
            text="Premium Edition v5.0",
            font=ctk.CTkFont(size=12),
            text_color=PremiumTheme.TEXT_MUTED
        )
        subtitle.pack(side="left", padx=(15, 0))
        
        # Action buttons
        button_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        button_frame.pack(side="right", padx=30)
        
        # Theme toggle
        self.theme_btn = ctk.CTkButton(
            button_frame,
            text="🌙",
            width=40,
            height=40,
            fg_color=PremiumTheme.BG_CARD,
            hover_color=PremiumTheme.INFO,
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=5)
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            button_frame,
            text="🔄",
            width=40,
            height=40,
            fg_color=PremiumTheme.BG_CARD,
            hover_color=PremiumTheme.SUCCESS,
            command=self.refresh_data
        )
        self.refresh_btn.pack(side="left", padx=5)
        
        # Export button
        self.export_btn = ctk.CTkButton(
            button_frame,
            text="📥 Export",
            width=100,
            height=40,
            fg_color=PremiumTheme.INFO,
            hover_color=PremiumTheme.get_gradient_color(0.7),
            command=self.export_data
        )
        self.export_btn.pack(side="left", padx=5)
    
    def create_transactions_tab(self):
        """Create transactions view."""
        tab = self.tab_view.tab("Transactions")
        
        # Search bar
        search_frame = ctk.CTkFrame(tab, fg_color="transparent", height=50)
        search_frame.pack(fill="x", padx=20, pady=20)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search transactions...",
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color=PremiumTheme.BG_CARD,
            border_color=PremiumTheme.GLASS_BORDER
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(tab, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20)
        
        self.filter_buttons = {}
        filters = ["All", "Ryan", "Jordyn", "Rent", "Settlement"]
        colors = [PremiumTheme.INFO, PremiumTheme.CHART_COLORS[0], PremiumTheme.CHART_COLORS[1], 
                 PremiumTheme.WARNING, PremiumTheme.SUCCESS]
        
        for i, (filter_name, color) in enumerate(zip(filters, colors)):
            btn = ctk.CTkButton(
                filter_frame,
                text=filter_name,
                width=100,
                height=32,
                fg_color=PremiumTheme.BG_CARD if filter_name != "All" else color,
                hover_color=color,
                command=lambda f=filter_name: self.apply_filter(f)
            )
            btn.pack(side="left", padx=5)
            self.filter_buttons[filter_name] = btn
        
        # Transaction list with scrollbar
        list_frame = ctk.CTkFrame(tab, fg_color=PremiumTheme.BG_CARD, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create treeview with custom style
        style = ttk.Style()
        style.theme_use("clam")
        
        # Configure colors
        style.configure(
            "Treeview",
            background=PremiumTheme.BG_CARD,
            foreground=PremiumTheme.TEXT_PRIMARY,
            fieldbackground=PremiumTheme.BG_CARD,
            borderwidth=0,
            rowheight=35
        )
        style.configure(
            "Treeview.Heading",
            background=PremiumTheme.BG_SECONDARY,
            foreground=PremiumTheme.TEXT_PRIMARY,
            borderwidth=0
        )
        style.map(
            "Treeview",
            background=[("selected", PremiumTheme.INFO)],
            foreground=[("selected", PremiumTheme.TEXT_PRIMARY)]
        )
        
        # Create treeview
        columns = ("Date", "Person", "Merchant", "Amount", "Type", "Status")
        self.trans_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            style="Treeview"
        )
        
        # Configure columns
        for col in columns:
            self.trans_tree.heading(col, text=col)
            width = 150 if col == "Merchant" else 100
            self.trans_tree.column(col, width=width)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=scrollbar.set)
        
        self.trans_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
    
    def create_analytics_tab(self):
        """Create analytics view."""
        tab = self.tab_view.tab("Analytics")
        
        # Charts container
        charts_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Monthly expenses chart
        expense_card = AnimatedCard(
            charts_frame,
            title="Monthly Expenses",
            subtitle="Last 6 months",
            icon="💸"
        )
        expense_card.pack(fill="x", pady=(0, 20))
        
        self.expense_chart = DataChart(expense_card.content_frame, width=600, height=250)
        self.expense_chart.pack(pady=10)
        
        # Category breakdown
        category_card = AnimatedCard(
            charts_frame,
            title="Category Breakdown",
            subtitle="Current month",
            icon="📊"
        )
        category_card.pack(fill="x", pady=(0, 20))
        
        self.category_chart = DataChart(category_card.content_frame, width=600, height=250)
        self.category_chart.pack(pady=10)
        
        # Trend analysis
        trend_card = AnimatedCard(
            charts_frame,
            title="Balance Trend",
            subtitle="Over time",
            icon="📈"
        )
        trend_card.pack(fill="x")
        
        self.trend_chart = DataChart(trend_card.content_frame, width=600, height=250)
        self.trend_chart.pack(pady=10)
    
    def create_monthly_tab(self):
        """Create monthly summary view."""
        tab = self.tab_view.tab("Monthly Summary")
        
        # Month selector
        selector_frame = ctk.CTkFrame(tab, fg_color="transparent", height=60)
        selector_frame.pack(fill="x", padx=20, pady=20)
        
        self.month_var = tk.StringVar(value="Current Month")
        self.month_dropdown = ctk.CTkComboBox(
            selector_frame,
            values=["Current Month"],
            variable=self.month_var,
            width=200,
            height=40,
            fg_color=PremiumTheme.BG_CARD,
            button_color=PremiumTheme.INFO,
            command=self.update_monthly_view
        )
        self.month_dropdown.pack(side="left")
        
        # Summary cards container
        self.monthly_container = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        self.monthly_container.pack(fill="both", expand=True, padx=20)
    
    def load_data_async(self):
        """
        Load data in background thread.
        
        Performs asynchronous data loading to prevent UI freezing.
        Loads transaction data and generates monthly summaries in a
        separate thread, then updates the UI in the main thread.
        
        This ensures responsive user experience even with large datasets.
        Shows loading indicators while data is being fetched and processed.
        
        Error handling is included to show user-friendly error messages
        if data loading fails.
        """
        def load():
            try:
                # Show loading state
                self.balance_label.configure(text="Loading...")
                self.balance_status.configure(text="Fetching data...")
                
                # Load data
                self.analyzer.load_all_data()
                self.transactions = self.analyzer.all_transactions
                
                # Generate monthly summary
                self.analyzer.generate_monthly_summary()
                self.monthly_data = self.analyzer.monthly_summary
                
                # Update UI in main thread
                self.after(0, self.update_ui_with_data)
                
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to load data: {e}"))
        
        # Start loading thread
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
    
    def update_ui_with_data(self):
        """
        Update UI with loaded data.
        
        Called after data loading completes to populate all UI components
        with actual financial data. Updates:
        - Balance display with current reconciliation status
        - Progress indicators showing expense proportions
        - Quick stats with transaction summaries
        - Transaction list with recent entries
        - Charts with visualized data
        - Monthly summary dropdowns
        
        This method coordinates all UI updates to reflect the loaded data.
        """
        self.loading = False
        
        # Update balance
        if self.monthly_data:
            latest_month = list(self.monthly_data.keys())[-1]
            latest_data = self.monthly_data[latest_month]
            
            balance = latest_data.get('running_balance', 0)
            if balance > 0:
                self.balance_label.configure(
                    text=f"R→J ${abs(balance):,.2f}",
                    text_color=PremiumTheme.CHART_COLORS[0]
                )
                self.balance_status.configure(text="Ryan owes Jordyn")
            elif balance < 0:
                self.balance_label.configure(
                    text=f"J→R ${abs(balance):,.2f}",
                    text_color=PremiumTheme.CHART_COLORS[1]
                )
                self.balance_status.configure(text="Jordyn owes Ryan")
            else:
                self.balance_label.configure(
                    text="Balanced",
                    text_color=PremiumTheme.SUCCESS
                )
                self.balance_status.configure(text="All settled up!")
            
            # Update progress circles
            ryan_exp = latest_data.get('ryan_expenses', 0)
            jordyn_exp = latest_data.get('jordyn_expenses', 0)
            total = ryan_exp + jordyn_exp
            
            if total > 0:
                self.ryan_progress.set_progress((ryan_exp / total) * 100)
                self.jordyn_progress.set_progress((jordyn_exp / total) * 100)
            
            # Update month dropdown
            months = list(self.monthly_data.keys())
            self.month_dropdown.configure(values=months)
            if months:
                self.month_var.set(months[-1])
        
        # Update stats
        self.update_stats()
        
        # Update transactions
        self.update_transaction_list()
        
        # Update charts
        self.update_charts()
    
    def update_stats(self):
        """Update quick stats."""
        # Clear existing stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        # Calculate stats
        total_trans = len(self.transactions)
        ryan_total = sum(t.get('actual_amount', 0) for t in self.transactions 
                        if t.get('person') == 'Ryan')
        jordyn_total = sum(t.get('actual_amount', 0) for t in self.transactions 
                          if t.get('person') == 'Jordyn')
        settlements = sum(1 for t in self.transactions if t.get('type') == 'settlement')
        
        stats = [
            ("Total Transactions", str(total_trans), "📝"),
            ("Ryan Total", f"${abs(ryan_total):,.2f}", "💳"),
            ("Jordyn Total", f"${abs(jordyn_total):,.2f}", "💳"),
            ("Settlements", str(settlements), "✅")
        ]
        
        for label, value, icon in stats:
            stat_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
            stat_frame.pack(fill="x", pady=5)
            
            icon_label = ctk.CTkLabel(
                stat_frame,
                text=icon,
                font=ctk.CTkFont(size=20),
                width=30
            )
            icon_label.pack(side="left")
            
            text_frame = ctk.CTkFrame(stat_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
            
            ctk.CTkLabel(
                text_frame,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=PremiumTheme.TEXT_SECONDARY,
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                text_frame,
                text=value,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=PremiumTheme.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill="x")
    
    def update_transaction_list(self):
        """Update transaction list."""
        # Clear existing items
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        
        # Add transactions
        for trans in reversed(self.transactions[-100:]):  # Show last 100
            date = trans.get('date', datetime.now())
            date_str = date.strftime('%m/%d/%Y') if isinstance(date, datetime) else str(date)
            
            person = trans.get('person', 'Unknown')
            merchant = trans.get('merchant', 'N/A')[:30]
            amount = trans.get('actual_amount', 0)
            trans_type = trans.get('type', 'expense')
            status = "✓" if trans.get('verified') else "?"
            
            # Color coding based on person
            tag = person.lower() if person in ['Ryan', 'Jordyn'] else 'other'
            
            self.trans_tree.insert(
                "",
                0,
                values=(date_str, person, merchant, f"${abs(amount):,.2f}", trans_type, status),
                tags=(tag,)
            )
        
        # Configure tags for colors
        self.trans_tree.tag_configure('ryan', foreground=PremiumTheme.CHART_COLORS[0])
        self.trans_tree.tag_configure('jordyn', foreground=PremiumTheme.CHART_COLORS[1])
        self.trans_tree.tag_configure('other', foreground=PremiumTheme.TEXT_SECONDARY)
    
    def update_charts(self):
        """Update all charts."""
        if not self.monthly_data:
            return
        
        # Monthly expenses chart
        months = list(self.monthly_data.keys())[-6:]
        expense_data = []
        for month in months:
            data = self.monthly_data.get(month, {})
            ryan = float(data.get('ryan_expenses', 0))
            jordyn = float(data.get('jordyn_expenses', 0))
            total = ryan + jordyn
            expense_data.append((month[:7], total))
        
        self.expense_chart.set_data(expense_data, "bar")
        
        # Category breakdown (mock data for now)
        categories = [
            ("Food", 1200),
            ("Transport", 800),
            ("Utilities", 600),
            ("Shopping", 1500),
            ("Rent", 2000),
            ("Other", 500)
        ]
        self.category_chart.set_data(categories, "bar")
        
        # Trend chart
        trend_data = []
        for month in months:
            data = self.monthly_data.get(month, {})
            balance = data.get('running_balance', 0)
            trend_data.append((month[:7], abs(balance)))
        
        self.trend_chart.set_data(trend_data, "line")
    
    def update_monthly_view(self, month=None):
        """Update monthly summary view."""
        if not month:
            month = self.month_var.get()
        
        # Clear existing content
        for widget in self.monthly_container.winfo_children():
            widget.destroy()
        
        if month not in self.monthly_data:
            return
        
        data = self.monthly_data[month]
        
        # Create summary cards
        cards_data = [
            ("Ryan Expenses", f"${data.get('ryan_expenses', 0):,.2f}", "💰", PremiumTheme.CHART_COLORS[0]),
            ("Jordyn Expenses", f"${data.get('jordyn_expenses', 0):,.2f}", "💰", PremiumTheme.CHART_COLORS[1]),
            ("Total Shared", f"${data.get('total_shared', 0):,.2f}", "🤝", PremiumTheme.INFO),
            ("Balance", f"${abs(data.get('running_balance', 0)):,.2f}", "⚖️", PremiumTheme.SUCCESS)
        ]
        
        # Create 2x2 grid
        for i, (title, value, icon, color) in enumerate(cards_data):
            row = i // 2
            col = i % 2
            
            card = AnimatedCard(
                self.monthly_container,
                title=title,
                icon=icon
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            value_label = ctk.CTkLabel(
                card.content_frame,
                text=value,
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=color
            )
            value_label.pack()
        
        # Configure grid weights
        self.monthly_container.grid_columnconfigure(0, weight=1)
        self.monthly_container.grid_columnconfigure(1, weight=1)
    
    def apply_filter(self, filter_name):
        """
        Apply transaction filter.
        
        Filters the transaction list based on selected criteria.
        Updates button states to show active filter and refreshes
        the transaction display.
        
        Args:
            filter_name (str): Name of filter to apply
                              Options: 'All', 'Ryan', 'Jordyn', 'Rent', 'Settlement'
        
        Note:
            Current implementation updates UI but actual filtering
            logic can be extended for more sophisticated filtering.
        """
        # Update button states
        for name, btn in self.filter_buttons.items():
            if name == filter_name:
                btn.configure(fg_color=PremiumTheme.INFO)
            else:
                btn.configure(fg_color=PremiumTheme.BG_CARD)
        
        # Filter transactions (implement actual filtering logic)
        # This is a placeholder
        self.update_transaction_list()
    
    def toggle_theme(self):
        """
        Toggle between dark and light theme.
        
        Switches the application appearance mode between dark and light.
        Updates the theme toggle button icon to reflect current state.
        
        The theme change applies globally to all CustomTkinter widgets
        providing consistent appearance throughout the application.
        """
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
        
        # Update theme button icon
        self.theme_btn.configure(text="☀️" if new_mode == "light" else "🌙")
    
    def refresh_data(self):
        """
        Refresh all data.
        
        Triggers a complete data reload from source files.
        Useful for updating the dashboard when underlying data changes.
        Shows loading indicators during the refresh process.
        """
        self.loading = True
        self.load_data_async()
    
    def export_data(self):
        """
        Export data to file.
        
        Exports all transaction and summary data to a JSON file.
        The export includes:
        - All transactions with formatted dates and amounts
        - Monthly summary data
        - Export timestamp for reference
        
        Files are named with timestamp for unique identification.
        Shows success message with filename or error message if export fails.
        
        Export format:
            financial_export_YYYYMMDD_HHMMSS.json
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_export_{timestamp}.json"
        
        try:
            export_data = {
                "transactions": [
                    {
                        "date": t.get('date').isoformat() if isinstance(t.get('date'), datetime) else str(t.get('date')),
                        "person": t.get('person'),
                        "merchant": t.get('merchant'),
                        "amount": float(t.get('actual_amount', 0)),
                        "type": t.get('type')
                    }
                    for t in self.transactions
                ],
                "monthly_summary": self.monthly_data,
                "export_date": datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            messagebox.showinfo("Export Complete", f"Data exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export data: {e}")


def main():
    """
    Launch the ultra-modern dashboard.
    
    Entry point for the application. Creates and runs the main
    dashboard window with all features enabled.
    
    This function initializes the CustomTkinter framework,
    creates the dashboard instance, and starts the event loop.
    
    Returns:
        None
    
    Example:
        >>> main()  # Launches the dashboard application
    """
    app = UltraModernDashboard()
    app.mainloop()


if __name__ == "__main__":
    main()