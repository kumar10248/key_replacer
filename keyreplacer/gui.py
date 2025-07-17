"""
GUI module for Key Replacer application.
Provides a modern, user-friendly interface for managing text expansions.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import logging
import threading
from typing import Dict, Optional, Callable
import webbrowser
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class KeyReplacerGUI:
    """Main GUI class for Key Replacer application."""

    def __init__(self, config=None, key_replacer=None):
        """Initialize the GUI with configuration and core engine."""
        self.config = config
        self.key_replacer = key_replacer
        self.root: Optional[tk.Tk] = None
        self.tray_icon = None
        self.is_minimized_to_tray = False
        
        # GUI elements
        self.mappings_tree: Optional[ttk.Treeview] = None
        self.key_entry: Optional[tk.Entry] = None
        self.value_text: Optional[scrolledtext.ScrolledText] = None
        self.status_label: Optional[tk.Label] = None
        self.start_stop_button: Optional[tk.Button] = None
        self.pause_resume_button: Optional[tk.Button] = None
        
        # Status tracking
        self.expansion_count = 0
        self.last_expansion = None

    def create_main_window(self):
        """Create and configure the main application window."""
        self.root = tk.Tk()
        self.root.title("Key Replacer v1.0.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Set window icon if available
        icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            try:
                self.root.iconphoto(False, tk.PhotoImage(file=str(icon_path)))
            except Exception as e:
                logger.debug(f"Could not set window icon: {e}")
        
        # Configure style
        self.setup_styles()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main interface
        self.create_main_interface()
        
        # Create status bar
        self.create_status_bar()
        
        # Setup key replacer callbacks
        if self.key_replacer:
            self.key_replacer.set_callbacks(
                on_expansion=self.on_expansion,
                on_error=self.on_error,
                on_status_change=self.on_status_change
            )
        
        # Restore window position and size
        self.restore_window_geometry()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        logger.info("Main window created")

    def setup_styles(self):
        """Configure the visual style of the application."""
        style = ttk.Style()
        
        # Use a modern theme if available
        available_themes = style.theme_names()
        if "clam" in available_themes:
            style.theme_use("clam")
        elif "vista" in available_themes:
            style.theme_use("vista")
        
        # Configure colors and fonts
        style.configure("Heading.TLabel", font=("Arial", 12, "bold"))
        style.configure("Status.TLabel", font=("Arial", 9))

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Import Mappings...", command=self.import_mappings)
        file_menu.add_command(label="Export Mappings...", command=self.export_mappings)
        file_menu.add_separator()
        file_menu.add_command(label="Settings...", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Mapping", command=self.focus_key_entry)
        edit_menu.add_command(label="Edit Selected", command=self.edit_selected_mapping)
        edit_menu.add_command(label="Delete Selected", command=self.delete_selected_mapping)
        edit_menu.add_separator()
        edit_menu.add_command(label="Clear All Mappings", command=self.clear_all_mappings)
        
        # Control menu
        control_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Control", menu=control_menu)
        control_menu.add_command(label="Start/Stop", command=self.toggle_key_replacer)
        control_menu.add_command(label="Pause/Resume", command=self.toggle_pause)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Visit Website", command=self.open_website)
        help_menu.add_command(label="Report Issue", command=self.report_issue)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

    def create_main_interface(self):
        """Create the main interface components."""
        # Create main paned window for resizable layout
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - Mappings list
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
        
        # Right panel - Add/Edit mappings
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        self.create_mappings_panel(left_frame)
        self.create_edit_panel(right_frame)
        self.create_control_panel(right_frame)

    def create_mappings_panel(self, parent):
        """Create the mappings list panel."""
        # Header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        ttk.Label(header_frame, text="Text Expansions", 
                 style="Heading.TLabel").pack(side=tk.LEFT)
        
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Mappings tree
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Create treeview with scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.mappings_tree = ttk.Treeview(tree_frame, 
                                         columns=("key", "value"),
                                         show="headings",
                                         yscrollcommand=tree_scroll_y.set,
                                         xscrollcommand=tree_scroll_x.set)
        
        # Configure scrollbars
        tree_scroll_y.config(command=self.mappings_tree.yview)
        tree_scroll_x.config(command=self.mappings_tree.xview)
        
        # Configure columns
        self.mappings_tree.heading("key", text="Key")
        self.mappings_tree.heading("value", text="Expansion")
        self.mappings_tree.column("key", width=150, minwidth=100)
        self.mappings_tree.column("value", width=300, minwidth=200)
        
        self.mappings_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind events
        self.mappings_tree.bind("<Double-1>", self.on_tree_double_click)
        self.mappings_tree.bind("<Delete>", self.on_tree_delete_key)
        self.mappings_tree.bind("<<TreeviewSelect>>", self.on_tree_selection_changed)

    def create_edit_panel(self, parent):
        """Create the add/edit mappings panel."""
        # Header
        edit_frame = ttk.LabelFrame(parent, text="Add/Edit Mapping", padding=10)
        edit_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Key entry
        ttk.Label(edit_frame, text="Key (shortcut):").pack(anchor=tk.W)
        self.key_entry = ttk.Entry(edit_frame, font=("Consolas", 10))
        self.key_entry.pack(fill=tk.X, pady=(2, 10))
        self.key_entry.bind("<Return>", lambda e: self.value_text.focus())
        
        # Value text area
        ttk.Label(edit_frame, text="Expansion (replacement text):").pack(anchor=tk.W)
        
        # Create frame for text widget and scrollbar
        text_frame = ttk.Frame(edit_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 10))
        
        self.value_text = scrolledtext.ScrolledText(text_frame, 
                                                   height=6,
                                                   font=("Consolas", 10),
                                                   wrap=tk.WORD)
        self.value_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        buttons_frame = ttk.Frame(edit_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.add_button = ttk.Button(buttons_frame, text="Add Mapping", 
                                    command=self.add_mapping)
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.update_button = ttk.Button(buttons_frame, text="Update", 
                                       command=self.update_mapping, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_button = ttk.Button(buttons_frame, text="Clear", 
                                      command=self.clear_edit_fields)
        self.clear_button.pack(side=tk.LEFT)

    def create_control_panel(self, parent):
        """Create the control panel for start/stop/pause functionality."""
        control_frame = ttk.LabelFrame(parent, text="Control", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.start_stop_button = ttk.Button(button_frame, text="Start", 
                                           command=self.toggle_key_replacer)
        self.start_stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.pause_resume_button = ttk.Button(button_frame, text="Pause", 
                                             command=self.toggle_pause,
                                             state=tk.DISABLED)
        self.pause_resume_button.pack(side=tk.LEFT)
        
        # Statistics
        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(stats_frame, text="Statistics:", font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.expansions_label = ttk.Label(stats_frame, text="Expansions: 0")
        self.expansions_label.pack(anchor=tk.W)
        
        self.last_expansion_label = ttk.Label(stats_frame, text="Last: None")
        self.last_expansion_label.pack(anchor=tk.W)

    def create_status_bar(self):
        """Create the status bar at the bottom of the window."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="Ready", 
                                     style="Status.TLabel", relief=tk.SUNKEN)
        self.status_label.pack(side=tk.LEFT, padx=2, pady=2)

    def refresh_mappings_list(self):
        """Refresh the mappings list display."""
        if not self.mappings_tree or not self.config:
            return
        
        # Clear existing items
        for item in self.mappings_tree.get_children():
            self.mappings_tree.delete(item)
        
        # Get current mappings
        mappings = self.config.get_mappings()
        
        # Apply search filter if any
        search_term = getattr(self, 'search_var', tk.StringVar()).get().lower()
        
        # Add filtered mappings to tree
        for key, value in sorted(mappings.items()):
            if not search_term or search_term in key.lower() or search_term in value.lower():
                # Truncate long values for display
                display_value = value[:100] + "..." if len(value) > 100 else value
                # Replace newlines with spaces for display
                display_value = display_value.replace("\\n", " ").replace("\\n", " ")
                self.mappings_tree.insert("", tk.END, values=(key, display_value))

    def on_search_changed(self, *args):
        """Handle search text changes."""
        self.refresh_mappings_list()

    def focus_key_entry(self):
        """Focus the key entry field."""
        if self.key_entry:
            self.key_entry.focus()

    def add_mapping(self):
        """Add a new text expansion mapping."""
        key = self.key_entry.get().strip()
        value = self.value_text.get("1.0", tk.END).strip()
        
        if not key:
            messagebox.showerror("Error", "Key cannot be empty!")
            self.key_entry.focus()
            return
        
        if not value:
            messagebox.showerror("Error", "Expansion text cannot be empty!")
            self.value_text.focus()
            return
        
        # Add to configuration
        if self.config and self.config.add_mapping(key, value):
            # Update key replacer
            if self.key_replacer:
                self.key_replacer.set_mappings(self.config.get_mappings())
            
            # Refresh display
            self.refresh_mappings_list()
            self.clear_edit_fields()
            
            self.update_status(f"Added mapping: {key}")
            messagebox.showinfo("Success", f"Mapping added successfully!\n\nKey: {key}\nExpansion: {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            messagebox.showerror("Error", "Failed to add mapping!")

    def update_mapping(self):
        """Update an existing mapping."""
        selected = self.mappings_tree.selection()
        if not selected:
            messagebox.showerror("Error", "No mapping selected!")
            return
        
        # Get the old key from the selected item
        old_key = self.mappings_tree.item(selected[0])["values"][0]
        
        # Get new values
        new_key = self.key_entry.get().strip()
        new_value = self.value_text.get("1.0", tk.END).strip()
        
        if not new_key or not new_value:
            messagebox.showerror("Error", "Key and expansion text cannot be empty!")
            return
        
        if self.config:
            # Remove old mapping if key changed
            if old_key != new_key:
                self.config.remove_mapping(old_key)
            
            # Add new mapping
            if self.config.add_mapping(new_key, new_value):
                # Update key replacer
                if self.key_replacer:
                    self.key_replacer.set_mappings(self.config.get_mappings())
                
                # Refresh display
                self.refresh_mappings_list()
                self.clear_edit_fields()
                
                self.update_status(f"Updated mapping: {new_key}")
                messagebox.showinfo("Success", "Mapping updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update mapping!")

    def delete_selected_mapping(self):
        """Delete the selected mapping."""
        selected = self.mappings_tree.selection()
        if not selected:
            messagebox.showerror("Error", "No mapping selected!")
            return
        
        key = self.mappings_tree.item(selected[0])["values"][0]
        
        if messagebox.askyesno("Confirm Delete", f"Delete mapping for '{key}'?"):
            if self.config and self.config.remove_mapping(key):
                # Update key replacer
                if self.key_replacer:
                    self.key_replacer.set_mappings(self.config.get_mappings())
                
                # Refresh display
                self.refresh_mappings_list()
                self.clear_edit_fields()
                
                self.update_status(f"Deleted mapping: {key}")
            else:
                messagebox.showerror("Error", "Failed to delete mapping!")

    def clear_all_mappings(self):
        """Clear all mappings after confirmation."""
        if not self.config:
            return
        
        mappings_count = len(self.config.get_mappings())
        if mappings_count == 0:
            messagebox.showinfo("Info", "No mappings to clear!")
            return
        
        if messagebox.askyesno("Confirm Clear All", 
                              f"Delete all {mappings_count} mappings?\n\nThis action cannot be undone!"):
            if self.config.clear_mappings():
                # Update key replacer
                if self.key_replacer:
                    self.key_replacer.set_mappings({})
                
                # Refresh display
                self.refresh_mappings_list()
                self.clear_edit_fields()
                
                self.update_status("All mappings cleared")
                messagebox.showinfo("Success", "All mappings cleared!")
            else:
                messagebox.showerror("Error", "Failed to clear mappings!")

    def clear_edit_fields(self):
        """Clear the edit fields and reset buttons."""
        if self.key_entry:
            self.key_entry.delete(0, tk.END)
        if self.value_text:
            self.value_text.delete("1.0", tk.END)
        
        # Reset button states
        if self.add_button:
            self.add_button.config(state=tk.NORMAL)
        if self.update_button:
            self.update_button.config(state=tk.DISABLED)

    def toggle_key_replacer(self):
        """Toggle the key replacer on/off."""
        if not self.key_replacer:
            return
        
        if self.key_replacer.is_running:
            self.key_replacer.stop()
        else:
            if self.key_replacer.start():
                # Load current mappings
                if self.config:
                    self.key_replacer.set_mappings(self.config.get_mappings())

    def toggle_pause(self):
        """Toggle pause/resume of the key replacer."""
        if self.key_replacer:
            self.key_replacer.toggle_pause()

    def on_expansion(self, key: str, value: str):
        """Handle expansion events."""
        self.expansion_count += 1
        self.last_expansion = f"{key} → {value[:30]}{'...' if len(value) > 30 else ''}"
        
        # Update UI in main thread
        if self.root:
            self.root.after(0, self.update_statistics)

    def on_error(self, error_message: str):
        """Handle error events."""
        logger.error(f"Key replacer error: {error_message}")
        if self.root:
            self.root.after(0, lambda: self.update_status(f"Error: {error_message}"))

    def on_status_change(self, status: str):
        """Handle status change events."""
        if self.root:
            self.root.after(0, lambda: self.update_control_buttons(status))

    def update_statistics(self):
        """Update the statistics display."""
        if self.expansions_label:
            self.expansions_label.config(text=f"Expansions: {self.expansion_count}")
        
        if self.last_expansion_label and self.last_expansion:
            self.last_expansion_label.config(text=f"Last: {self.last_expansion}")

    def update_control_buttons(self, status: str):
        """Update control button states based on status."""
        if not self.start_stop_button or not self.pause_resume_button:
            return
        
        if status == "running":
            self.start_stop_button.config(text="Stop")
            self.pause_resume_button.config(text="Pause", state=tk.NORMAL)
            self.update_status("Key replacer is running")
        elif status == "stopped":
            self.start_stop_button.config(text="Start")
            self.pause_resume_button.config(text="Pause", state=tk.DISABLED)
            self.update_status("Key replacer stopped")
        elif status == "paused":
            self.start_stop_button.config(text="Stop")
            self.pause_resume_button.config(text="Resume", state=tk.NORMAL)
            self.update_status("Key replacer paused")

    def update_status(self, message: str):
        """Update the status bar message."""
        if self.status_label:
            self.status_label.config(text=message)

    def on_tree_double_click(self, event):
        """Handle double-click on tree item to edit."""
        self.edit_selected_mapping()

    def on_tree_delete_key(self, event):
        """Handle delete key press on tree."""
        self.delete_selected_mapping()

    def on_tree_selection_changed(self, event):
        """Handle tree selection changes."""
        selected = self.mappings_tree.selection()
        if selected and self.config:
            # Load selected mapping into edit fields
            key = self.mappings_tree.item(selected[0])["values"][0]
            mappings = self.config.get_mappings()
            
            if key in mappings:
                self.key_entry.delete(0, tk.END)
                self.key_entry.insert(0, key)
                
                self.value_text.delete("1.0", tk.END)
                self.value_text.insert("1.0", mappings[key])
                
                # Switch to update mode
                self.add_button.config(state=tk.DISABLED)
                self.update_button.config(state=tk.NORMAL)

    def edit_selected_mapping(self):
        """Edit the selected mapping."""
        selected = self.mappings_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a mapping to edit.")
            return
        
        # The selection change handler already loads the data
        self.key_entry.focus()

    def import_mappings(self):
        """Import mappings from a JSON file."""
        if not self.config:
            return
        
        file_path = filedialog.askopenfilename(
            title="Import Mappings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                result = messagebox.askyesnocancel(
                    "Import Mappings",
                    "How would you like to import the mappings?\n\n"
                    "Yes: Merge with existing mappings\n"
                    "No: Replace all existing mappings\n"
                    "Cancel: Cancel import"
                )
                
                if result is None:  # Cancel
                    return
                
                merge = result  # True for merge, False for replace
                
                if self.config.import_mappings(file_path, merge=merge):
                    # Update key replacer
                    if self.key_replacer:
                        self.key_replacer.set_mappings(self.config.get_mappings())
                    
                    # Refresh display
                    self.refresh_mappings_list()
                    
                    mappings_count = len(self.config.get_mappings())
                    action = "merged" if merge else "imported"
                    messagebox.showinfo("Success", f"Mappings {action} successfully!\n\nTotal mappings: {mappings_count}")
                    self.update_status(f"Mappings {action} from {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", "Failed to import mappings!")
                    
            except Exception as e:
                logger.error(f"Error importing mappings: {e}")
                messagebox.showerror("Error", f"Failed to import mappings:\n{e}")

    def export_mappings(self):
        """Export mappings to a JSON file."""
        if not self.config:
            return
        
        mappings = self.config.get_mappings()
        if not mappings:
            messagebox.showinfo("Info", "No mappings to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Mappings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if self.config.export_mappings(file_path):
                    messagebox.showinfo("Success", f"Mappings exported successfully!\n\nFile: {file_path}\nMappings: {len(mappings)}")
                    self.update_status(f"Mappings exported to {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", "Failed to export mappings!")
            except Exception as e:
                logger.error(f"Error exporting mappings: {e}")
                messagebox.showerror("Error", f"Failed to export mappings:\n{e}")

    def show_settings(self):
        """Show the settings dialog."""
        # TODO: Implement settings dialog
        messagebox.showinfo("Settings", "Settings dialog will be implemented in a future update.")

    def show_help(self):
        """Show the help dialog."""
        help_text = """Key Replacer - Quick Start Guide

1. ADD MAPPINGS:
   • Enter a short key (e.g., "myemail")
   • Enter the expansion text (e.g., "john@example.com")
   • Click "Add Mapping"

2. USE EXPANSIONS:
   • Start the key replacer by clicking "Start"
   • Type your key followed by space, enter, or tab
   • Watch it expand automatically!

3. MANAGE MAPPINGS:
   • Double-click a mapping to edit it
   • Select and press Delete to remove
   • Use search to find specific mappings

4. EXAMPLES:
   • "addr" → "123 Main St, City, State 12345"
   • "sig" → "Best regards,\\nJohn Doe"
   • "phone" → "+1-234-567-8900"

TIPS:
• Keys are case-insensitive by default
• Use \\n for line breaks in expansions
• The app runs in the background when minimized
• All data is stored locally on your computer"""

        help_window = tk.Toplevel(self.root)
        help_window.title("Quick Start Guide")
        help_window.geometry("500x400")
        help_window.resizable(False, False)
        
        # Make it modal
        help_window.grab_set()
        help_window.transient(self.root)
        
        # Center the window
        help_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                               font=("Consolas", 10), padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(help_window, text="Close", 
                  command=help_window.destroy).pack(pady=(0, 10))

    def show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        shortcuts_text = """Keyboard Shortcuts

MAIN WINDOW:
• Ctrl+N       - Focus key entry field
• Ctrl+S       - Start/Stop key replacer
• Ctrl+P       - Pause/Resume
• Delete       - Delete selected mapping
• F1           - Show this help
• Ctrl+Q       - Quit application

MAPPINGS LIST:
• Double-click - Edit mapping
• Enter        - Edit selected mapping
• Delete       - Delete selected mapping
• Ctrl+F       - Focus search field

EDITING:
• Enter        - Move to expansion field
• Ctrl+Enter   - Add/Update mapping
• Escape       - Clear fields

GLOBAL (when running):
• Ctrl+Alt+K   - Toggle pause (configurable)"""

        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("400x300")
        shortcuts_window.resizable(False, False)
        
        # Make it modal
        shortcuts_window.grab_set()
        shortcuts_window.transient(self.root)
        
        # Center the window
        shortcuts_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 100,
            self.root.winfo_rooty() + 100
        ))
        
        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD, 
                                               font=("Consolas", 9), padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert("1.0", shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(shortcuts_window, text="Close", 
                  command=shortcuts_window.destroy).pack(pady=(0, 10))

    def show_about(self):
        """Show about dialog."""
        about_text = """Key Replacer v1.0.0

A powerful, cross-platform text expansion tool
that helps boost your productivity.

• Real-time text expansion
• Cross-platform support (Windows, macOS, Linux)
• Simple and intuitive interface
• Local data storage (no cloud dependency)
• Open source and free

Created by Kumar Devashish

Built with Python and Tkinter
Uses keyboard and pyautogui libraries"""

        messagebox.showinfo("About Key Replacer", about_text)

    def open_website(self):
        """Open the project website."""
        webbrowser.open("https://github.com/yourusername/key-replacer")

    def report_issue(self):
        """Open the issue reporting page."""
        webbrowser.open("https://github.com/yourusername/key-replacer/issues")

    def restore_window_geometry(self):
        """Restore window position and size from configuration."""
        if not self.config:
            return
        
        try:
            pos = self.config.get_setting("settings.window_position", {"x": 100, "y": 100})
            size = self.config.get_setting("settings.window_size", {"width": 800, "height": 600})
            
            self.root.geometry(f"{size['width']}x{size['height']}+{pos['x']}+{pos['y']}")
        except Exception as e:
            logger.debug(f"Could not restore window geometry: {e}")

    def save_window_geometry(self):
        """Save current window position and size to configuration."""
        if not self.config or not self.root:
            return
        
        try:
            # Get current geometry
            geometry = self.root.geometry()
            # Parse: "800x600+100+50"
            size_part, pos_part = geometry.split("+", 1)
            width, height = map(int, size_part.split("x"))
            x, y = map(int, pos_part.split("+"))
            
            self.config.set_setting("settings.window_position", {"x": x, "y": y})
            self.config.set_setting("settings.window_size", {"width": width, "height": height})
        except Exception as e:
            logger.debug(f"Could not save window geometry: {e}")

    def on_closing(self):
        """Handle window closing event."""
        # Save window geometry
        self.save_window_geometry()
        
        # Check if should minimize to tray
        if self.config and self.config.get_setting("settings.minimize_to_tray", True):
            # TODO: Implement system tray functionality
            pass
        
        # Stop key replacer
        if self.key_replacer and self.key_replacer.is_running:
            self.key_replacer.stop()
        
        # Destroy window
        if self.root:
            self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        if not self.root:
            self.create_main_window()
        
        # Load and display mappings
        self.refresh_mappings_list()
        
        # Start the main loop
        self.root.mainloop()


def create_gui(config=None, key_replacer=None) -> KeyReplacerGUI:
    """Create and return a GUI instance."""
    return KeyReplacerGUI(config=config, key_replacer=key_replacer)
