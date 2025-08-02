#!/usr/bin/env python3
"""Test basic Tkinter functionality."""

import tkinter as tk
import sys

try:
    print("Creating Tkinter root window...")
    root = tk.Tk()
    print("Success! Tkinter is working.")
    
    print("Setting window properties...")
    root.title("Test Window")
    root.geometry("400x300")
    
    print("Creating a label...")
    label = tk.Label(root, text="Tkinter is working!", font=("Arial", 16))
    label.pack(pady=50)
    
    print("Creating a button to close...")
    button = tk.Button(root, text="Close", command=root.quit)
    button.pack()
    
    print("Window created successfully. Starting mainloop...")
    print("(Window should appear now - click 'Close' to exit)")
    
    root.mainloop()
    print("Mainloop ended successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()