#!/usr/bin/env python3
"""
GUI Launcher for Financial Reconciliation System
==============================================

Choose and launch your preferred reconciliation interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from pathlib import Path
import subprocess

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


class GUILauncher:
    """Launcher for selecting reconciliation GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Financial Reconciliation - Choose Interface")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f2f5")
        
        # Center window
        self.center_window()
        
        # Create interface
        self.create_interface()
        
    def center_window(self):
        """Center window on screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_interface(self):
        """Create the launcher interface."""
        # Header
        header = tk.Frame(self.root, bg="#5e72e4", height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(
            header,
            text="💰 Financial Reconciliation System",
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#5e72e4"
        )
        title.pack(expand=True)
        
        # Subtitle
        subtitle = tk.Label(
            self.root,
            text="Choose your preferred interface for reviewing transactions",
            font=("Arial", 14),
            fg="#666",
            bg="#f0f2f5"
        )
        subtitle.pack(pady=20)
        
        # Options container
        options_frame = tk.Frame(self.root, bg="#f0f2f5")
        options_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # GUI Options
        guis = [
            {
                "name": "Modern Visual Review",
                "description": "Clean Material Design interface with smooth animations",
                "file": "src/review/modern_visual_review_gui.py",
                "icon": "🎨",
                "color": "#4CAF50"
            },
            {
                "name": "Ultra Modern Interface",
                "description": "Stunning gradients, glassmorphism, and visual effects",
                "file": "src/review/ultra_modern_reconciliation_gui.py",
                "icon": "✨",
                "color": "#9C27B0"
            },
            {
                "name": "Premium Experience",
                "description": "AI-powered with particle effects and advanced features",
                "file": "src/review/premium_reconciliation_gui.py",
                "icon": "💎",
                "color": "#FF9800"
            },
            {
                "name": "Classic CLI Review",
                "description": "Terminal-based interface for power users",
                "file": "bin/manual_review_cli.py",
                "icon": "⌨️",
                "color": "#607D8B"
            }
        ]
        
        for i, gui in enumerate(guis):
            # Card frame
            card = tk.Frame(
                options_frame,
                bg="white",
                relief=tk.RAISED,
                bd=1
            )
            card.pack(fill=tk.X, pady=10)
            
            # Inner padding
            inner = tk.Frame(card, bg="white")
            inner.pack(fill=tk.X, padx=20, pady=15)
            
            # Icon and title
            title_frame = tk.Frame(inner, bg="white")
            title_frame.pack(fill=tk.X)
            
            icon_label = tk.Label(
                title_frame,
                text=gui["icon"],
                font=("Arial", 24),
                bg="white"
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))
            
            name_label = tk.Label(
                title_frame,
                text=gui["name"],
                font=("Arial", 16, "bold"),
                fg=gui["color"],
                bg="white"
            )
            name_label.pack(side=tk.LEFT)
            
            # Description
            desc_label = tk.Label(
                inner,
                text=gui["description"],
                font=("Arial", 12),
                fg="#666",
                bg="white",
                anchor="w"
            )
            desc_label.pack(fill=tk.X, pady=(5, 10))
            
            # Launch button
            btn = tk.Button(
                inner,
                text=f"Launch {gui['name']}",
                font=("Arial", 12, "bold"),
                bg=gui["color"],
                fg="white",
                activebackground=gui["color"],
                activeforeground="white",
                relief=tk.FLAT,
                padx=20,
                pady=10,
                cursor="hand2",
                command=lambda f=gui["file"]: self.launch_gui(f)
            )
            btn.pack(anchor="e")
            
            # Hover effect
            card.bind("<Enter>", lambda e, c=card: c.configure(bg="#f8f9fa"))
            card.bind("<Leave>", lambda e, c=card: c.configure(bg="white"))
            
        # Footer
        footer = tk.Frame(self.root, bg="#f0f2f5")
        footer.pack(fill=tk.X, pady=20)
        
        info_label = tk.Label(
            footer,
            text="💡 Tip: Use keyboard shortcuts in any GUI for faster review!",
            font=("Arial", 11),
            fg="#666",
            bg="#f0f2f5"
        )
        info_label.pack()
        
    def launch_gui(self, file_path):
        """Launch the selected GUI."""
        try:
            # Check if customtkinter is needed
            if "ultra_modern" in file_path or "premium" in file_path:
                try:
                    import customtkinter
                except ImportError:
                    response = messagebox.askyesno(
                        "Install Required Package",
                        "This interface requires 'customtkinter' package.\n\nWould you like to install it now?"
                    )
                    if response:
                        messagebox.showinfo(
                            "Installing",
                            "Installing customtkinter... This may take a moment."
                        )
                        subprocess.check_call([
                            sys.executable, "-m", "pip", "install", "customtkinter"
                        ])
                        messagebox.showinfo(
                            "Success",
                            "Package installed successfully! Launching GUI..."
                        )
                    else:
                        return
                        
            # Check if Pillow is needed for premium
            if "premium" in file_path:
                try:
                    from PIL import Image
                except ImportError:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", "Pillow"
                    ])
                    
            # Close launcher
            self.root.destroy()
            
            # Launch the GUI
            subprocess.run([sys.executable, file_path])
            
        except Exception as e:
            messagebox.showerror(
                "Launch Error",
                f"Failed to launch GUI:\n{str(e)}"
            )
            
    def run(self):
        """Run the launcher."""
        self.root.mainloop()


def main():
    """Main entry point."""
    launcher = GUILauncher()
    launcher.run()


if __name__ == "__main__":
    main()