import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import json
import threading
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

class BrowserProfileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Browser Profile Manager")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        self.root.minsize(700, 500)
        
        # Theme management
        self.dark_mode = False
        self.setup_themes()
        self.load_theme_preference()
        
        # API base URL
        self.api_base = "http://127.0.0.1:25325"
        
        # Store original profiles data for sorting
        self.original_profiles = []
        self.sort_reverse = False  # Track sort direction
        
        # Auto View variables
        self.auto_view_running = False
        self.driver = None
        
        # Keywords tracking
        self.used_keywords = set()  # Track used keywords to avoid repetition
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Create GUI elements
        self.create_widgets()
        
        # Apply initial theme
        self.apply_theme()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
    
    def setup_themes(self):
        """Setup light and dark theme colors"""
        self.light_theme = {
            'bg': '#f0f0f0',
            'fg': '#000000',
            'button_bg': '#e1e1e1',
            'button_fg': '#000000',
            'entry_bg': '#ffffff',
            'entry_fg': '#000000',
            'text_bg': '#ffffff',
            'text_fg': '#000000',
            'frame_bg': '#ffffff',
            'label_bg': '#f0f0f0',
            'tree_bg': '#ffffff',
            'tree_fg': '#000000',
            'notebook_bg': '#f0f0f0',
            'notebook_fg': '#000000',
            'accent': '#007acc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        self.dark_theme = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'button_bg': '#404040',
            'button_fg': '#ffffff',
            'entry_bg': '#2d2d2d',
            'entry_fg': '#ffffff',
            'text_bg': '#2d2d2d',
            'text_fg': '#ffffff',
            'frame_bg': '#2d2d2d',
            'label_bg': '#1e1e1e',
            'tree_bg': '#2d2d2d',
            'tree_fg': '#ffffff',
            'notebook_bg': '#1e1e1e',
            'notebook_fg': '#ffffff',
            'accent': '#007acc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
        
        self.current_theme = self.light_theme
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.current_theme = self.dark_theme
            self.theme_btn.config(text="☀️ Light Mode")
        else:
            self.current_theme = self.light_theme
            self.theme_btn.config(text="🌙 Dark Mode")
        
        self.apply_theme()
        self.save_theme_preference()
        
    def apply_theme(self):
        """Apply the current theme to all widgets"""
        try:
            # Configure root window
            self.root.configure(bg=self.current_theme['bg'])
            
            # Configure notebook
            style = ttk.Style()
            style.theme_use('clam')
            
            # Configure notebook style
            style.configure('TNotebook', 
                          background=self.current_theme['notebook_bg'],
                          borderwidth=0)
            style.configure('TNotebook.Tab', 
                          background=self.current_theme['notebook_bg'],
                          foreground=self.current_theme['notebook_fg'],
                          padding=[10, 5])
            style.map('TNotebook.Tab',
                     background=[('selected', self.current_theme['button_bg'])])
            
            # Configure frame styles
            style.configure('TFrame', background=self.current_theme['frame_bg'])
            style.configure('TLabelframe', background=self.current_theme['frame_bg'])
            style.configure('TLabelframe.Label', 
                          background=self.current_theme['frame_bg'],
                          foreground=self.current_theme['fg'])
            
            # Configure button styles
            style.configure('TButton', 
                          background=self.current_theme['button_bg'],
                          foreground=self.current_theme['button_fg'])
            style.map('TButton',
                     background=[('active', self.current_theme['button_bg'])])
            
            # Configure entry styles
            style.configure('TEntry', 
                          fieldbackground=self.current_theme['entry_bg'],
                          foreground=self.current_theme['entry_fg'])
            
            # Configure label styles
            style.configure('TLabel', 
                          background=self.current_theme['label_bg'],
                          foreground=self.current_theme['fg'])
            
            # Configure treeview styles
            style.configure('Treeview', 
                          background=self.current_theme['tree_bg'],
                          foreground=self.current_theme['tree_fg'],
                          fieldbackground=self.current_theme['tree_bg'])
            style.configure('Treeview.Heading', 
                          background=self.current_theme['button_bg'],
                          foreground=self.current_theme['button_fg'])
            
            # Configure spinbox styles
            style.configure('TSpinbox', 
                          fieldbackground=self.current_theme['entry_bg'],
                          foreground=self.current_theme['entry_fg'])
            
            # Configure checkbutton styles
            style.configure('TCheckbutton', 
                          background=self.current_theme['frame_bg'],
                          foreground=self.current_theme['fg'])
            
            # Configure radiobutton styles
            style.configure('TRadiobutton', 
                          background=self.current_theme['frame_bg'],
                          foreground=self.current_theme['fg'])
            
            # Configure combobox styles
            style.configure('TCombobox', 
                          fieldbackground=self.current_theme['entry_bg'],
                          foreground=self.current_theme['entry_fg'])
            
            # Apply theme to specific widgets
            self.apply_widget_theme()
            
        except Exception as e:
            print(f"Theme application error: {e}")
    
    def apply_widget_theme(self):
        """Apply theme to specific widget instances"""
        try:
            # Apply to text widgets
            if hasattr(self, 'url_text'):
                self.url_text.configure(
                    bg=self.current_theme['text_bg'],
                    fg=self.current_theme['text_fg'],
                    insertbackground=self.current_theme['fg']
                )
            
            if hasattr(self, 'auto_view_log'):
                self.auto_view_log.configure(
                    bg=self.current_theme['text_bg'],
                    fg=self.current_theme['text_fg'],
                    insertbackground=self.current_theme['fg']
                )
            
            # Apply to canvas (now handled by popup)
            # Note: profile_canvas was removed when switching to popup
            # Canvas theming is now handled in apply_popup_theme
            
            # Apply to entry widgets - search more thoroughly
            self.apply_entry_theme()
            
        except Exception as e:
            print(f"Widget theme application error: {e}")
    
    def apply_entry_theme(self):
        """Apply theme to entry widgets throughout the application"""
        try:
            # Apply to profile ID entry
            if hasattr(self, 'profile_id_var'):
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Entry):
                        widget.configure(
                            bg=self.current_theme['entry_bg'],
                            fg=self.current_theme['entry_fg'],
                            insertbackground=self.current_theme['fg']
                        )
            
            # Apply to specific entry widgets we know about
            for widget_name in ['profile_id_entry', 'chrome_flags_entry', 'start_pages_entry']:
                if hasattr(self, widget_name):
                    widget = getattr(self, widget_name)
                    widget.configure(
                        bg=self.current_theme['entry_bg'],
                        fg=self.current_theme['entry_fg'],
                        insertbackground=self.current_theme['fg']
                    )
                    
        except Exception as e:
            print(f"Entry theme application error: {e}")
    
    def refresh_theme(self):
        """Refresh theme for all widgets"""
        self.apply_theme()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for the application"""
        try:
            # Theme toggle: Ctrl+T
            self.root.bind('<Control-t>', lambda e: self.toggle_theme())
            
            # Import URLs: Ctrl+I
            self.root.bind('<Control-i>', lambda e: self.import_urls_from_file())
            
            # Export URLs: Ctrl+E
            self.root.bind('<Control-e>', lambda e: self.export_urls_to_file())
            
            # Clear URLs: Ctrl+L
            self.root.bind('<Control-l>', lambda e: self.clear_urls())
            
            # Start Auto View: Ctrl+S
            self.root.bind('<Control-s>', lambda e: self.start_auto_view() if hasattr(self, 'start_auto_view_btn') and self.start_auto_view_btn['state'] != 'disabled' else None)
            
            # Stop Auto View: Ctrl+X
            self.root.bind('<Control-x>', lambda e: self.stop_auto_view() if hasattr(self, 'stop_auto_view_btn') and self.stop_auto_view_btn['state'] != 'disabled' else None)
            
            # Sort Profiles: Ctrl+P
            self.root.bind('<Control-p>', lambda e: self.toggle_profile_sort())
            
        except Exception as e:
            print(f"Failed to setup keyboard shortcuts: {e}")
    
    def save_theme_preference(self):
        """Save current theme preference to file"""
        try:
            import json
            import os
            
            config_dir = os.path.expanduser("~/.auto_view_config")
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, "theme_config.json")
            config = {
                'dark_mode': self.dark_mode,
                'theme_name': 'dark' if self.dark_mode else 'light'
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
                
        except Exception as e:
            print(f"Failed to save theme preference: {e}")
    
    def load_theme_preference(self):
        """Load theme preference from file"""
        try:
            import json
            import os
            
            config_dir = os.path.expanduser("~/.auto_view_config")
            config_file = os.path.join(config_dir, "theme_config.json")
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                if config.get('dark_mode', False):
                    self.dark_mode = True
                    self.current_theme = self.dark_theme
                    
        except Exception as e:
            print(f"Failed to load theme preference: {e}")
    
    def create_widgets(self):
        # Configure root window
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Create Profile Manager tab
        self.profile_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.profile_frame, text="Profile Manager")
        
        # Create Auto View tab
        self.auto_view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.auto_view_frame, text="Auto View")
        
        # Create Amazon Search tab
        self.amazon_search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.amazon_search_frame, text="Amazon Search")
        
        # Setup Profile Manager tab
        self.setup_profile_manager_tab()
        
        # Setup Auto View tab
        self.setup_auto_view_tab()
        
        # Setup Amazon Search tab
        self.setup_amazon_search_tab()
    
    def setup_profile_manager_tab(self):
        # Main frame for profile manager
        main_frame = ttk.Frame(self.profile_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.profile_frame.columnconfigure(0, weight=1)
        self.profile_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title and theme toggle
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        title_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, text="Browser Profile Manager", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(title_frame, text="🌙 Dark Mode", command=self.toggle_theme)
        self.theme_btn.grid(row=0, column=1, sticky=tk.E, padx=(20, 0))
        
        # Add tooltip for theme button
       # self.create_tooltip(self.theme_btn, "Toggle between Light and Dark themes\nKeyboard shortcut: Ctrl+T")
        
        # Help button
        help_btn = ttk.Button(title_frame, text="❓ Help", command=self.show_help)
        help_btn.grid(row=0, column=2, sticky=tk.E, padx=(10, 0))
        # self.create_tooltip(help_btn, "Show keyboard shortcuts and help information")
        
        # Update button text based on current theme
        if self.dark_mode:
            self.theme_btn.config(text="☀️ Light Mode")
        else:
            self.theme_btn.config(text="🌙 Dark Mode")
        

        # API Status
        self.status_label = ttk.Label(main_frame, text="Status: Ready", foreground="blue")
        self.status_label.grid(row=1, column=0, columnspan=3, pady=(0, 10))
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        # Refresh button
        refresh_btn = ttk.Button(button_frame, text="Refresh Profiles", command=self.refresh_profiles)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Start Profile section
        start_frame = ttk.LabelFrame(main_frame, text="Start Profile", padding="10")
        start_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        start_frame.columnconfigure(1, weight=1)
        
        # Profile ID input
        ttk.Label(start_frame, text="Profile ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.profile_id_var = tk.StringVar()
        profile_id_entry = ttk.Entry(start_frame, textvariable=self.profile_id_var, width=20)
        profile_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Chrome flags input
        ttk.Label(start_frame, text="Chrome Flags:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.chrome_flags_var = tk.StringVar()
        chrome_flags_entry = ttk.Entry(start_frame, textvariable=self.chrome_flags_var, width=40)
        chrome_flags_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Start pages input
        ttk.Label(start_frame, text="Start Pages:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.start_pages_var = tk.StringVar()
        start_pages_entry = ttk.Entry(start_frame, textvariable=self.start_pages_var, width=40)
        start_pages_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Start button
        start_btn = ttk.Button(start_frame, text="Start Profile", command=self.start_profile)
        start_btn.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Profiles list
        list_frame = ttk.LabelFrame(main_frame, text="Available Profiles", padding="10")
        list_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Treeview for profiles
        columns = ("ID", "Name", "Status", "Folder")
        self.profiles_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.profiles_tree.heading("ID", text="Profile ID")
        self.profiles_tree.heading("Name", text="Profile Name")
        self.profiles_tree.heading("Status", text="Status")
        self.profiles_tree.heading("Folder", text="Folder")
        self.profiles_tree.column("ID", width=200, minwidth=150)
        self.profiles_tree.column("Name", width=300, minwidth=200)
        self.profiles_tree.column("Status", width=100, minwidth=80)
        self.profiles_tree.column("Folder", width=100, minwidth=60)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.profiles_tree.yview)
        self.profiles_tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.profiles_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind double-click event to select profile ID
        self.profiles_tree.bind("<Double-1>", self.on_profile_select)
        
        # Bind column header click for sorting
        self.profiles_tree.bind("<Button-1>", self.on_column_click)
        
        # Load profiles on startup
        self.refresh_profiles()
        
        # Apply theme after widgets are created
        self.apply_theme()
    
    def setup_auto_view_tab(self):
        # Main frame for auto view
        main_frame = ttk.Frame(self.auto_view_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.auto_view_frame.columnconfigure(0, weight=1)
        self.auto_view_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # URLs input section
        urls_frame = ttk.LabelFrame(main_frame)
        urls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        urls_frame.columnconfigure(0, weight=1)
        urls_frame.rowconfigure(1, weight=1)
        
        # URLs header with import/clear buttons
        urls_header_frame = ttk.Frame(urls_frame)
        urls_header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        urls_header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(urls_header_frame, text="Enter URLs (one per line):").grid(row=0, column=0, sticky=tk.W)
        
        # Import and Clear buttons
        import_btn = ttk.Button(urls_header_frame, text="📁 Import TXT", command=self.import_urls_from_file)
        import_btn.grid(row=0, column=1, padx=(10, 5))
        self.create_tooltip(import_btn, "Import URLs from a text file\nKeyboard shortcut: Ctrl+I")
        
        clear_btn = ttk.Button(urls_header_frame, text="🗑️ Clear All", command=self.clear_urls)
        clear_btn.grid(row=0, column=2, padx=(5, 0))
        self.create_tooltip(clear_btn, "Clear all URLs from the text area\nKeyboard shortcut: Ctrl+L")
        
        # URLs text area
        self.url_text = scrolledtext.ScrolledText(urls_frame, height=8, width=60)
        self.url_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Scroll speed
        ttk.Label(settings_frame, text="Scroll Speed (seconds):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.scroll_speed_var = tk.DoubleVar(value=0.5)
        scroll_speed_spinbox = ttk.Spinbox(settings_frame, from_=0.1, to=5.0, width=10, 
                                         textvariable=self.scroll_speed_var, increment=0.1)
        scroll_speed_spinbox.grid(row=0, column=1, sticky=tk.W)
        
        # Time per page
        ttk.Label(settings_frame, text="Time per page (seconds):").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.time_per_page_var = tk.IntVar(value=30)
        self.time_per_page_spinbox = ttk.Spinbox(settings_frame, from_=10, to=300, width=10, 
                                          textvariable=self.time_per_page_var, increment=5)
        self.time_per_page_spinbox.grid(row=1, column=1, sticky=tk.W)
        # self.create_tooltip(self.time_per_page_spinbox, "Fixed time per page (used when Random time interval is disabled)")
        
        # Random time interval checkbox
        self.random_time_interval_var = tk.BooleanVar(value=False)
        random_time_check = ttk.Checkbutton(settings_frame, text="Random time interval", 
                                          variable=self.random_time_interval_var, command=self.on_random_time_change)
        random_time_check.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))
        # self.create_tooltip(random_time_check, "When enabled: Uses random time from range below\nWhen disabled: Uses fixed time from 'Time per page' setting")
        
        # Random time range frame
        self.random_time_frame = ttk.Frame(settings_frame)
        self.random_time_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.random_time_frame, text="Random range:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        # Min time frame
        min_time_frame = ttk.Frame(self.random_time_frame)
        min_time_frame.grid(row=0, column=1, sticky=tk.W, padx=(0, 5))
        
        self.min_hours_var = tk.IntVar(value=0)
        self.min_minutes_var = tk.IntVar(value=0)
        self.min_seconds_var = tk.IntVar(value=20)
        
        min_time_frame.columnconfigure(0, weight=1)
        min_time_frame.columnconfigure(2, weight=1)
        min_time_frame.columnconfigure(4, weight=1)
        
        min_hours_spinbox = ttk.Spinbox(min_time_frame, from_=0, to=23, width=3, 
                                      textvariable=self.min_hours_var, increment=1, command=lambda: self.validate_time_range())
        min_hours_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(min_time_frame, text=":").grid(row=0, column=1, sticky=tk.W, padx=(2, 2))
        
        min_minutes_spinbox = ttk.Spinbox(min_time_frame, from_=0, to=59, width=3, 
                                        textvariable=self.min_minutes_var, increment=1, command=lambda: self.validate_time_range())
        min_minutes_spinbox.grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(min_time_frame, text=":").grid(row=0, column=3, sticky=tk.W, padx=(2, 2))
        
        min_seconds_spinbox = ttk.Spinbox(min_time_frame, from_=0, to=59, width=3, 
                                        textvariable=self.min_seconds_var, increment=5, command=lambda: self.validate_time_range())
        min_seconds_spinbox.grid(row=0, column=4, sticky=tk.W)
        
        ttk.Label(self.random_time_frame, text="to").grid(row=0, column=2, sticky=tk.W, padx=(5, 5))
        
        # Max time frame
        max_time_frame = ttk.Frame(self.random_time_frame)
        max_time_frame.grid(row=0, column=3, sticky=tk.W, padx=(0, 10))
        
        self.max_hours_var = tk.IntVar(value=0)
        self.max_minutes_var = tk.IntVar(value=0)
        self.max_seconds_var = tk.IntVar(value=40)
        
        max_time_frame.columnconfigure(0, weight=1)
        max_time_frame.columnconfigure(2, weight=1)
        max_time_frame.columnconfigure(4, weight=1)
        
        max_hours_spinbox = ttk.Spinbox(max_time_frame, from_=0, to=23, width=3, 
                                      textvariable=self.max_hours_var, increment=1, command=lambda: self.validate_time_range())
        max_hours_spinbox.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(max_time_frame, text=":").grid(row=0, column=1, sticky=tk.W, padx=(2, 2))
        
        max_minutes_spinbox = ttk.Spinbox(max_time_frame, from_=0, to=59, width=3, 
                                        textvariable=self.max_minutes_var, increment=1, command=lambda: self.validate_time_range())
        max_minutes_spinbox.grid(row=0, column=2, sticky=tk.W)
        
        ttk.Label(max_time_frame, text=":").grid(row=0, column=3, sticky=tk.W, padx=(2, 2))
        
        max_seconds_spinbox = ttk.Spinbox(max_time_frame, from_=0, to=59, width=3, 
                                        textvariable=self.max_seconds_var, increment=5, command=lambda: self.validate_time_range())
        max_seconds_spinbox.grid(row=0, column=4, sticky=tk.W)
        
        ttk.Label(self.random_time_frame, text="(hh:mm:ss)").grid(row=0, column=4, sticky=tk.W)
        
        # Initially hide random time frame
        self.random_time_frame.grid_remove()
        
        # Random clicks
        self.random_clicks_var = tk.BooleanVar(value=True)
        random_clicks_check = ttk.Checkbutton(settings_frame, text="Random clicks on elements", 
                                            variable=self.random_clicks_var)
        random_clicks_check.grid(row=0, column=2, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Use profile browser
        self.use_profile_var = tk.BooleanVar(value=True)
        use_profile_check = ttk.Checkbutton(settings_frame, text="Use undetectable browser profile", 
                                          variable=self.use_profile_var)
        use_profile_check.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Profile selection section
        profile_frame = ttk.LabelFrame(settings_frame, text="Profile Selection", padding="10")
        profile_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        profile_frame.columnconfigure(0, weight=1)
        profile_frame.rowconfigure(1, weight=1)
        
        # Profile mode selection
        mode_frame = ttk.Frame(profile_frame)
        mode_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        self.profile_mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(mode_frame, text="Single Profile", variable=self.profile_mode_var, 
                       value="single", command=self.on_profile_mode_change).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Radiobutton(mode_frame, text="Multiple Profiles", variable=self.profile_mode_var, 
                       value="multiple", command=self.on_profile_mode_change).pack(side=tk.LEFT, padx=(20, 0))
        
        # Mode description
        mode_desc = ttk.Label(mode_frame, text="Single: Use one profile | Multiple: Use multiple profiles simultaneously", 
                            font=('TkDefaultFont', 8), foreground='gray')
        mode_desc.pack(side=tk.LEFT, padx=(20, 0))
        
        # Refresh profiles icon button (small icon next to mode)
        refresh_icon_btn = ttk.Button(mode_frame, text="🔄", width=3, 
                                    command=self.refresh_auto_view_profiles)
        refresh_icon_btn.pack(side=tk.LEFT, padx=(20, 0))
        self.create_tooltip(refresh_icon_btn, "Click to refresh profiles")
        
        # Single profile selection
        self.single_profile_frame = ttk.Frame(profile_frame)
        self.single_profile_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(self.single_profile_frame, text="Select Profile:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.auto_view_profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(self.single_profile_frame, textvariable=self.auto_view_profile_var, width=50)
        self.profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Bind profile selection change event
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selection_change)
        
        # Multiple profiles selection - Now using popup
        self.multiple_profile_frame = ttk.Frame(profile_frame)
        self.multiple_profile_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        self.multiple_profile_frame.columnconfigure(0, weight=1)
        
        # Multiple profile info and popup button
        info_frame = ttk.Frame(self.multiple_profile_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        info_frame.columnconfigure(0, weight=1)
        
        ttk.Label(info_frame, text="Multiple Profiles:").grid(row=0, column=0, sticky=tk.W)
        self.profile_count_label = ttk.Label(info_frame, text="(0 selected)", foreground="blue")
        self.profile_count_label.grid(row=0, column=1, sticky=tk.E)
        
        # Popup button for multiple profile selection
        self.popup_btn = ttk.Button(self.multiple_profile_frame, text="📋 Select Multiple Profiles", 
                                   command=self.show_multiple_profile_popup)
        self.popup_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        # self.create_tooltip(self.popup_btn, "Click to open profile selection popup")
        
        # Initialize profile variables for popup
        self.profile_checkboxes = {}
        self.profile_vars = {}
        self.profile_sort_order = "lowest_to_highest"
        
        # Initially hide multiple profile frame
        self.multiple_profile_frame.grid_remove()
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        self.start_auto_view_btn = ttk.Button(control_frame, text="Start Auto View", 
                                            command=self.start_auto_view)
        self.start_auto_view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_auto_view_btn = ttk.Button(control_frame, text="Stop", 
                                           command=self.stop_auto_view, state=tk.DISABLED)
        self.stop_auto_view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status and log
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Log header with full size button
        log_header_frame = ttk.Frame(log_frame)
        log_header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        log_header_frame.columnconfigure(0, weight=1)
        
        ttk.Label(log_header_frame, text="Activity Log:").pack(side=tk.LEFT)
        
        # Full size log button
        full_log_btn = ttk.Button(log_header_frame, text="📖 Full Size Log", 
                                 command=self.show_full_size_log)
        full_log_btn.pack(side=tk.RIGHT)
        
        # Log text area
        self.auto_view_log = scrolledtext.ScrolledText(log_frame, height=10, width=60)
        self.auto_view_log.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Auto View status
        self.auto_view_status = ttk.Label(main_frame, text="Status: Ready", foreground="blue")
        self.auto_view_status.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        

        # Apply theme after all widgets are created
        self.refresh_theme()
    
    def setup_amazon_search_tab(self):
        """Setup Amazon Search tab with dedicated interface"""
        # Main frame for amazon search
        main_frame = ttk.Frame(self.amazon_search_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.amazon_search_frame.columnconfigure(0, weight=1)
        self.amazon_search_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Amazon Keyword Search", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, text="Search Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Enable search keywords
        self.amazon_enable_search_var = tk.BooleanVar(value=False)
        enable_search_check = ttk.Checkbutton(settings_frame, text="Enable Amazon keyword search", 
                                            variable=self.amazon_enable_search_var, command=self.on_amazon_search_enable_change)
        enable_search_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Search frequency
        ttk.Label(settings_frame, text="Search after every:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        self.amazon_search_frequency_var = tk.IntVar(value=4)
        search_freq_spinbox = ttk.Spinbox(settings_frame, from_=1, to=10, width=8, 
                                         textvariable=self.amazon_search_frequency_var, increment=1)
        search_freq_spinbox.grid(row=1, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(settings_frame, text="URLs").grid(row=1, column=2, sticky=tk.W)
        
        # Typing speed setting
        ttk.Label(settings_frame, text="Typing speed:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        self.typing_speed_var = tk.IntVar(value=65)
        typing_speed_spinbox = ttk.Spinbox(settings_frame, from_=30, to=120, width=8, 
                                          textvariable=self.typing_speed_var, increment=5)
        typing_speed_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(0, 10))
        ttk.Label(settings_frame, text="WPM (words per minute)").grid(row=2, column=2, sticky=tk.W)
        
        # Keywords section
        keywords_frame = ttk.LabelFrame(main_frame, text="Amazon Keywords", padding="10")
        keywords_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        keywords_frame.columnconfigure(0, weight=1)
        keywords_frame.rowconfigure(1, weight=1)
        
        # Keywords input
        ttk.Label(keywords_frame, text="Keywords (one per line):").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Keywords text area with scrollbar
        keywords_text_frame = ttk.Frame(keywords_frame)
        keywords_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        keywords_text_frame.columnconfigure(0, weight=1)
        keywords_text_frame.rowconfigure(0, weight=1)
        
        self.amazon_keywords_text = scrolledtext.ScrolledText(keywords_text_frame, height=8, width=60)
        self.amazon_keywords_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Initially disable keywords text if search is not enabled
        if not self.amazon_enable_search_var.get():
            self.amazon_keywords_text.config(state='disabled')
        
        # Keywords control buttons
        keywords_btn_frame = ttk.Frame(keywords_frame)
        keywords_btn_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.amazon_import_keywords_btn = ttk.Button(keywords_btn_frame, text="📁 Import Keywords", 
                                                    command=self.import_amazon_keywords_from_file)
        self.amazon_import_keywords_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.amazon_clear_keywords_btn = ttk.Button(keywords_btn_frame, text="🗑️ Clear Keywords", 
                                                   command=self.clear_amazon_keywords)
        self.amazon_clear_keywords_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.amazon_sample_keywords_btn = ttk.Button(keywords_btn_frame, text="📝 Sample Keywords", 
                                                   command=self.create_amazon_sample_keywords)
        self.amazon_sample_keywords_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Initially disable buttons if search is not enabled
        if not self.amazon_enable_search_var.get():
            self.amazon_import_keywords_btn.config(state='disabled')
            self.amazon_clear_keywords_btn.config(state='disabled')
            self.amazon_sample_keywords_btn.config(state='disabled')
        
        # Test search section
        test_frame = ttk.LabelFrame(main_frame, text="Test Search", padding="10")
        test_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Test search button
        test_search_btn = ttk.Button(test_frame, text="🔍 Test Amazon Search", 
                                    command=self.test_amazon_search)
        test_search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.amazon_status_label = ttk.Label(test_frame, text="Status: Ready", foreground="blue")
        self.amazon_status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Apply theme
        self.apply_theme()
    
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()
            
            def hide_tooltip(event):
                tooltip.destroy()
            
            widget.bind('<Leave>', hide_tooltip)
            tooltip.bind('<Leave>', hide_tooltip)
            
            # Auto-hide after 3 seconds
            tooltip.after(3000, tooltip.destroy)
        
        widget.bind('<Enter>', show_tooltip)
    
    def refresh_profiles(self):
        """Fetch and display the list of browser profiles"""
        try:
            self.status_label.config(text="Status: 🔄 Fetching profiles...", foreground="orange")
            self.root.update()
            
            response = requests.get(f"{self.api_base}/list", timeout=10)
            
            if response.status_code == 200:
                try:
                    profiles = response.json()
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to get text content
                    profiles = response.text
                
                self.display_profiles(profiles)
                
                # Count profiles for status
                if isinstance(profiles, dict) and 'data' in profiles:
                    profile_count = len(profiles['data'])
                elif isinstance(profiles, list):
                    profile_count = len(profiles)
                else:
                    profile_count = 1
                
                self.status_label.config(text=f"Status: ✅ Loaded {profile_count} profiles", foreground="green")
                
                # Auto-resize window based on profile count
                self.auto_resize_window(profile_count)
            else:
                self.status_label.config(text=f"Status: ❌ Error {response.status_code}", foreground="red")
                messagebox.showerror("Error", f"Failed to fetch profiles. Status: {response.status_code}\nResponse: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.status_label.config(text="Status: ❌ Connection failed", foreground="red")
            messagebox.showerror("Connection Error", "Cannot connect to the API server. Make sure it's running on http://127.0.0.1:25325")
        except requests.exceptions.Timeout:
            self.status_label.config(text="Status: ❌ Request timeout", foreground="red")
            messagebox.showerror("Timeout Error", "Request timed out. Please try again.")
        except Exception as e:
            self.status_label.config(text="Status: ❌ Unexpected error", foreground="red")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def on_column_click(self, event):
        """Handle click on column header for sorting"""
        region = self.profiles_tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.profiles_tree.identify("column", event.x, event.y)
            if column == "#2":  # Profile Name column
                self.sort_by_name_numeric()
    
    def sort_by_name_numeric(self):
        """Sort profiles by name numerically (extract numbers from name)"""
        if not self.original_profiles:
            return
        
        def extract_number(name):
            """Extract the first number from profile name for sorting"""
            import re
            numbers = re.findall(r'\d+', str(name))
            return int(numbers[0]) if numbers else float('inf')  # Put non-numeric names at end
        
        # Sort profiles by extracted number
        sorted_profiles = sorted(self.original_profiles, 
                               key=lambda x: extract_number(x['name']), 
                               reverse=self.sort_reverse)
        
        # Toggle sort direction for next click
        self.sort_reverse = not self.sort_reverse
        
        # Update display
        self.update_treeview_display(sorted_profiles)
        
        # Update status with sort indication
        direction = "descending" if self.sort_reverse else "ascending"
        self.status_label.config(text=f"Status: Sorted by number ({direction}) - {len(sorted_profiles)} profiles", foreground="blue")
    
    def update_treeview_display(self, profiles):
        """Update treeview with sorted profiles"""
        # Clear existing items
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        
        # Add sorted profiles
        for profile in profiles:
            self.profiles_tree.insert("", tk.END, values=(
                profile['id'], 
                profile['name'], 
                profile['status'], 
                profile['folder']
            ))
    
    def auto_resize_window(self, profile_count):
        """Auto-resize window based on number of profiles"""
        # Calculate optimal height based on profile count
        base_height = 400  # Height for GUI elements
        row_height = 20    # Height per profile row
        max_display_rows = 15  # Maximum rows to show without scrolling
        
        # Calculate needed height
        needed_rows = min(profile_count, max_display_rows)
        optimal_height = base_height + (needed_rows * row_height)
        
        # Set minimum and maximum heights
        min_height = 500
        max_height = 900
        final_height = max(min_height, min(optimal_height, max_height))
        
        # Get current window size
        current_width = self.root.winfo_width()
        
        # Set optimal width (ensure all columns are visible)
        optimal_width = max(800, current_width)
        
        # Update window size
        self.root.geometry(f"{optimal_width}x{final_height}")
        
        # Update treeview height if needed
        if profile_count > 15:
            # Many profiles - keep scrolling
            self.profiles_tree.configure(height=15)
        else:
            # Few profiles - show all without scrolling
            self.profiles_tree.configure(height=max(5, profile_count + 1))
    
    def display_profiles(self, profiles):
        """Display profiles in the treeview"""
        # Clear existing items
        for item in self.profiles_tree.get_children():
            self.profiles_tree.delete(item)
        
        
        # Handle different response formats
        if isinstance(profiles, str):
            # If response is a string, try to parse as JSON
            try:
                profiles = json.loads(profiles)
            except json.JSONDecodeError:
                # If not JSON, treat as single profile
                self.profiles_tree.insert("", tk.END, values=(profiles, "Profile", "", ""))
                return
        
        # Handle API response format: {"code": 0, "data": {...}, "status": "success"}
        if isinstance(profiles, dict):
            if 'data' in profiles and profiles.get('code') == 0:
                profiles_data = profiles['data']
                
                # Store original profiles data for filtering
                self.original_profiles = []
                
                # Add each profile from the data object
                for profile_id, profile_info in profiles_data.items():
                    if isinstance(profile_info, dict):
                        profile_name = profile_info.get('name', profile_id)
                        status = profile_info.get('status', 'Unknown')
                        folder = profile_info.get('folder', '')
                        
                        # Store in original_profiles for filtering
                        self.original_profiles.append({
                            'id': profile_id,
                            'name': profile_name,
                            'status': status,
                            'folder': folder
                        })
                        
                        self.profiles_tree.insert("", tk.END, values=(profile_id, profile_name, status, folder))
                    else:
                        # Store simple profile
                        self.original_profiles.append({
                            'id': profile_id,
                            'name': str(profile_info),
                            'status': '',
                            'folder': ''
                        })
                        self.profiles_tree.insert("", tk.END, values=(profile_id, str(profile_info), "", ""))
                
                return
            else:
                # Handle other dict formats
                profile_id = profiles.get('id', profiles.get('profileId', 'unknown'))
                profile_name = profiles.get('name', profiles.get('profileName', 'Profile'))
                status = profiles.get('status', 'Unknown')
                folder = profiles.get('folder', '')
                self.profiles_tree.insert("", tk.END, values=(profile_id, profile_name, status, folder))
                return
        
        # Handle list format
        if isinstance(profiles, list):
            for i, profile in enumerate(profiles):
                if isinstance(profile, dict):
                    profile_id = profile.get('id', profile.get('profileId', f'profile_{i}'))
                    profile_name = profile.get('name', profile.get('profileName', f'Profile {i+1}'))
                    status = profile.get('status', 'Unknown')
                    folder = profile.get('folder', '')
                else:
                    profile_id = str(profile)
                    profile_name = f"Profile {i+1}"
                    status = 'Unknown'
                    folder = ''
                
                self.profiles_tree.insert("", tk.END, values=(profile_id, profile_name, status, folder))
            return
        
        # Fallback for other types
        self.profiles_tree.insert("", tk.END, values=(str(profiles), "Profile", "", ""))
    
    def on_profile_select(self, event):
        """Handle double-click on profile to select its ID"""
        selection = self.profiles_tree.selection()
        if selection:
            item = self.profiles_tree.item(selection[0])
            profile_id = item['values'][0]
            self.profile_id_var.set(profile_id)
    
    def start_profile(self):
        """Start a browser profile with the specified parameters"""
        profile_id = self.profile_id_var.get().strip()
        chrome_flags = self.chrome_flags_var.get().strip()
        start_pages = self.start_pages_var.get().strip()
        
        if not profile_id:
            messagebox.showwarning("Warning", "Please enter a Profile ID")
            return
        
        try:
            self.status_label.config(text="Status: Starting profile...", foreground="orange")
            self.root.update()
            
            # Build URL with parameters
            url = f"{self.api_base}/profile/start/{profile_id}"
            params = {}
            
            if chrome_flags:
                params['chrome_flags'] = chrome_flags
            if start_pages:
                params['start-pages'] = start_pages
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                self.status_label.config(text="Status: Profile started successfully", foreground="green")
                messagebox.showinfo("Success", f"Profile {profile_id} started successfully!")
            else:
                self.status_label.config(text=f"Status: Failed to start profile", foreground="red")
                messagebox.showerror("Error", f"Failed to start profile. Status: {response.status_code}\nResponse: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            self.status_label.config(text="Status: Connection failed", foreground="red")
            messagebox.showerror("Connection Error", "Cannot connect to the API server")
        except requests.exceptions.Timeout:
            self.status_label.config(text="Status: Request timeout", foreground="red")
            messagebox.showerror("Timeout Error", "Request timed out. Please try again.")
        except Exception as e:
            self.status_label.config(text="Status: Unexpected error", foreground="red")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    
    def refresh_auto_view_profiles(self):
        """Refresh available profiles for auto view"""
        try:
            self.log_auto_view("🔄 Refreshing profiles from API...")
            response = requests.get(f"{self.api_base}/list", timeout=10)
            if response.status_code == 200:
                try:
                    profiles = response.json()
                    if isinstance(profiles, dict) and 'data' in profiles and profiles.get('code') == 0:
                        profiles_data = profiles['data']
                        
                        # Create profile options with name and status
                        profile_options = []
                        for profile_id, profile_info in profiles_data.items():
                            if isinstance(profile_info, dict):
                                name = profile_info.get('name', profile_id)
                                status = profile_info.get('status', 'Unknown')
                                debug_port = profile_info.get('debug_port', '')
                                
                                # Format: "Name - Status (Port)"
                                if debug_port:
                                    option_text = f"{name} - {status} (Port: {debug_port})"
                                else:
                                    option_text = f"{name} - {status}"
                                
                                profile_options.append((option_text, profile_id, debug_port, status, name))
                        
                        # Sort profiles by name numerically (from lowest to highest) - DEFAULT BEHAVIOR
                        def extract_number_from_name(name):
                            """Extract the first number from profile name for sorting"""
                            import re
                            numbers = re.findall(r'\d+', str(name))
                            return int(numbers[0]) if numbers else float('inf')  # Put non-numeric names at end
                        
                        # Sort by extracted number (lowest to highest)
                        profile_options.sort(key=lambda x: extract_number_from_name(x[4]))
                        
                        # Remove the name from the tuple since we only needed it for sorting
                        profile_options = [(option[0], option[1], option[2], option[3]) for option in profile_options]
                        
                        # Update combobox
                        self.profile_combo['values'] = [option[0] for option in profile_options]
                        
                        # Update checkboxes for multiple selection
                        self.create_profile_checkboxes(profile_options)
                        
                        self.profile_options = profile_options  # Store for later use
                        
                        # Set default sort order to lowest_to_highest since this is now the default behavior
                        self.profile_sort_order = "lowest_to_highest"
                        
                        if profile_options:
                            # Set first started profile as default, or first available
                            started_profiles = [opt for opt in profile_options if opt[3] == 'Started']
                            if started_profiles:
                                self.profile_combo.set(started_profiles[0][0])
                            else:
                                self.profile_combo.set(profile_options[0][0])
                        
                        self.log_auto_view(f"✅ Successfully refreshed {len(profile_options)} profiles for auto view")
                        self.log_auto_view(f"📊 Profiles sorted by name: lowest to highest")
                        
                except Exception as e:
                    self.log_auto_view(f"❌ Error parsing profiles: {str(e)}")
            else:
                self.log_auto_view(f"❌ Error fetching profiles: HTTP {response.status_code}")
                
        except Exception as e:
            self.log_auto_view(f"❌ Error refreshing profiles: {str(e)}")
    
    def get_selected_profile_info(self):
        """Get selected profile information"""
        if not hasattr(self, 'profile_options'):
            return None, None, None
            
        selected_text = self.auto_view_profile_var.get()
        for option in self.profile_options:
            if option[0] == selected_text:
                return option[1], option[2], option[3]  # profile_id, debug_port, status
        return None, None, None
    
    def on_profile_mode_change(self):
        """Handle profile mode change"""
        if self.profile_mode_var.get() == "single":
            self.single_profile_frame.grid()
            self.multiple_profile_frame.grid_remove()
        else:
            self.single_profile_frame.grid_remove()
            self.multiple_profile_frame.grid()
            # Khi chọn multiple mode, tự động hiển thị popup
            self.show_multiple_profile_popup()
    
    def create_profile_checkboxes(self, profile_options):
        """Create checkboxes for profile selection - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        # The actual checkbox creation is handled in create_popup_profile_checkboxes
        try:
            # Store profile options for popup use
            self.profile_options = profile_options
            
            # Update profile count label if it exists
            if hasattr(self, 'profile_count_label'):
                total_count = len(profile_options)
                self.profile_count_label.config(text=f"(0/{total_count} selected)")
                self.profile_count_label.config(foreground="blue")
            
            # Log that profiles are ready for popup selection
            self.log_auto_view(f"Profiles loaded for popup selection: {total_count} profiles available")
            
        except Exception as e:
            self.log_auto_view(f"Error in create_profile_checkboxes: {str(e)}")
    
    def update_selection_count(self):
        """Update the selection count display - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            if hasattr(self, 'profile_vars') and self.profile_vars:
                selected_count = sum(1 for var in self.profile_vars.values() if var.get())
                total_count = len(self.profile_vars)
                
                # Update profile count label if it exists
                if hasattr(self, 'profile_count_label'):
                    self.profile_count_label.config(text=f"({selected_count}/{total_count} selected)")
                    
                    # Change color based on selection
                    if selected_count == 0:
                        self.profile_count_label.config(foreground="red")
                    elif selected_count == total_count:
                        self.profile_count_label.config(foreground="green")
                    else:
                        self.profile_count_label.config(foreground="blue")
                        
        except Exception as e:
            self.log_auto_view(f"Error in update_selection_count: {str(e)}")
    
    def sort_profiles_by_name(self):
        """Sort profiles by name numerically (lowest to highest)"""
        try:
            if hasattr(self, 'profile_options') and self.profile_options:
                # Create a copy with names for sorting
                profiles_with_names = []
                for option in self.profile_options:
                    option_text, profile_id, debug_port, status = option
                    # Extract name from option_text (format: "Name - Status (Port)")
                    name = option_text.split(' - ')[0]
                    profiles_with_names.append((option_text, profile_id, debug_port, status, name))
                
                # Sort by extracted number
                def extract_number_from_name(name):
                    """Extract the first number from profile name for sorting"""
                    import re
                    numbers = re.findall(r'\d+', str(name))
                    return int(numbers[0]) if numbers else float('inf')  # Put non-numeric names at end
                
                # Sort by extracted number (lowest to highest)
                profiles_with_names.sort(key=lambda x: extract_number_from_name(x[4]))
                
                # Remove the name from the tuple since we only needed it for sorting
                sorted_profiles = [(option[0], option[1], option[2], option[3]) for option in profiles_with_names]
                
                # Update the stored profile options
                self.profile_options = sorted_profiles
                
                # Update combobox values
                self.profile_combo['values'] = [option[0] for option in sorted_profiles]
                
                # Update sort order
                self.profile_sort_order = "lowest_to_highest"
                
                # Log the sorting action
                self.log_auto_view(f"Profiles sorted by name (lowest to highest): {len(sorted_profiles)} profiles")
                
                # Show confirmation message
                messagebox.showinfo("Sort Complete", 
                                  f"Profiles have been sorted by name from lowest to highest.\n"
                                  f"Total profiles: {len(sorted_profiles)}")
                
        except Exception as e:
            self.log_auto_view(f"Error sorting profiles: {str(e)}")
            messagebox.showerror("Sort Error", f"Failed to sort profiles: {str(e)}")
    
    def toggle_profile_sort(self):
        """Toggle between different sort orders - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            # Check if popup is open
            if hasattr(self, 'popup_sort_btn'):
                # Popup is open, use popup methods
                if self.profile_sort_order == "lowest_to_highest":
                    # Currently sorted, so reset to default order
                    self.popup_reset_profile_sort()
                    self.popup_sort_btn.config(text="🔢 Sort by Name")
                else:
                    # Currently not sorted, so sort from lowest to highest
                    self.popup_sort_profiles_by_name()
                    self.popup_sort_btn.config(text="🔄 Reset Sort")
            else:
                # Popup not open, show message to open popup first
                messagebox.showinfo("Sort Toggle", 
                                  "Please open the Multiple Profiles popup first to use sorting features.\n"
                                  "Click 'Multiple Profiles' mode to open the popup.")
                
        except Exception as e:
            self.log_auto_view(f"Error toggling sort: {str(e)}")
    
    def reset_profile_sort(self):
        """Reset profiles to default order (as received from API) - unsorted"""
        try:
            if hasattr(self, 'profile_options'):
                # Get the original profile data to show unsorted order
                response = requests.get(f"{self.api_base}/list", timeout=10)
                if response.status_code == 200:
                    profiles = response.json()
                    if isinstance(profiles, dict) and 'data' in profiles and profiles.get('code') == 0:
                        profiles_data = profiles['data']
                        
                        # Create profile options without sorting
                        profile_options = []
                        for profile_id, profile_info in profiles_data.items():
                            if isinstance(profile_info, dict):
                                name = profile_info.get('name', profile_id)
                                status = profile_info.get('status', 'Unknown')
                                debug_port = profile_info.get('debug_port', '')
                                
                                # Format: "Name - Status (Port)"
                                if debug_port:
                                    option_text = f"{name} - {status} (Port: {debug_port})"
                                else:
                                    option_text = f"{name} - {status}"
                                
                                profile_options.append((option_text, profile_id, debug_port, status))
                        
                        # Update the stored profile options (unsorted)
                        self.profile_options = profile_options
                        
                        # Update combobox values
                        self.profile_combo['values'] = [option[0] for option in profile_options]
                        
                        # Reset sort order
                        self.profile_sort_order = "default"
                        
                        # Log the reset action
                        self.log_auto_view("Profile sort order reset to default (API order)")
                        
                        # Show confirmation message
                        messagebox.showinfo("Sort Reset", "Profiles have been reset to default API order (unsorted).")
                        
        except Exception as e:
            self.log_auto_view(f"Error resetting sort: {str(e)}")
            messagebox.showerror("Reset Error", f"Failed to reset sort order: {str(e)}")
    
    def show_multiple_profile_popup(self):
        """Hiển thị popup window để chọn multiple profiles"""
        try:
            # Tạo popup window
            popup_window = tk.Toplevel(self.root)
            popup_window.title("Chọn Multiple Profiles")
            popup_window.geometry("800x600")
            popup_window.resizable(True, True)
            
            # Làm cho popup window modal
            popup_window.transient(self.root)
            popup_window.grab_set()
            
            # Căn giữa popup window
            popup_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            # Tạo main frame
            main_frame = ttk.Frame(popup_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Tiêu đề
            title_label = ttk.Label(main_frame, text="Chọn Multiple Profiles", font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Header với thông tin sort và count
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            # Sort order indicator
            self.popup_sort_order_label = ttk.Label(header_frame, text="Sort: Lowest → Highest", 
                                                   foreground="green", font=('TkDefaultFont', 9))
            self.popup_sort_order_label.pack(side=tk.LEFT)
            
            # Profile count
            self.popup_profile_count_label = ttk.Label(header_frame, text="(0 selected)", 
                                                      foreground="blue", font=('TkDefaultFont', 9))
            self.popup_profile_count_label.pack(side=tk.RIGHT)
            
            # Quick action buttons
            action_frame = ttk.Frame(main_frame)
            action_frame.pack(fill=tk.X, pady=(0, 10))
            
            select_all_btn = ttk.Button(action_frame, text="Select All", command=self.popup_select_all_profiles)
            select_all_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            clear_all_btn = ttk.Button(action_frame, text="Clear All", command=self.popup_clear_all_profiles)
            clear_all_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            started_only_btn = ttk.Button(action_frame, text="Started Only", command=self.popup_select_started_profiles)
            started_only_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            available_only_btn = ttk.Button(action_frame, text="Available Only", command=self.popup_select_available_profiles)
            available_only_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Sort button
            self.popup_sort_btn = ttk.Button(action_frame, text="🔄 Reset Sort", command=self.popup_toggle_profile_sort)
            self.popup_sort_btn.pack(side=tk.LEFT, padx=(0, 5))
            
            # Profile list với scrollbar
            list_frame = ttk.LabelFrame(main_frame, text="Profile List", padding="10")
            list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            # List header
            list_header = ttk.Frame(list_frame)
            list_header.pack(fill=tk.X, pady=(0, 5))
            
            self.popup_list_header_label = ttk.Label(list_header, 
                                                    text="Profile List - Sorted by Name (Lowest → Highest)", 
                                                    font=('TkDefaultFont', 9), foreground="green")
            self.popup_list_header_label.pack(side=tk.LEFT)
            
            # Create scrollable frame for checkboxes
            canvas_frame = ttk.Frame(list_frame)
            canvas_frame.pack(fill=tk.BOTH, expand=True)
            
            self.popup_profile_canvas = tk.Canvas(canvas_frame, height=300, bg='white', relief='sunken', bd=1)
            self.popup_profile_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.popup_profile_canvas.yview)
            self.popup_profile_scrollable_frame = ttk.Frame(self.popup_profile_canvas)
            
            self.popup_profile_scrollable_frame.bind(
                "<Configure>",
                lambda e: self.popup_profile_canvas.configure(scrollregion=self.popup_profile_canvas.bbox("all"))
            )
            
            self.popup_profile_canvas.create_window((0, 0), window=self.popup_profile_scrollable_frame, anchor="nw")
            self.popup_profile_canvas.configure(yscrollcommand=self.popup_profile_scrollbar.set)
            
            self.popup_profile_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.popup_profile_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bind mouse wheel scrolling to canvas
            def _on_mousewheel(event):
                self.popup_profile_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            def _on_mousewheel_linux(event):
                if event.num == 4:
                    self.popup_profile_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.popup_profile_canvas.yview_scroll(1, "units")
            
            # Bind mouse wheel events for different OS
            self.popup_profile_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
            self.popup_profile_canvas.bind("<Button-4>", _on_mousewheel_linux)  # Linux
            self.popup_profile_canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux
            
            # Also bind to the scrollable frame
            self.popup_profile_scrollable_frame.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
            self.popup_profile_scrollable_frame.bind("<Button-4>", _on_mousewheel_linux)  # Linux
            self.popup_profile_scrollable_frame.bind("<Button-5>", _on_mousewheel_linux)  # Linux
            
            # Make canvas focusable so it can receive mouse wheel events
            self.popup_profile_canvas.focus_set()
            
            # Control buttons
            control_frame = ttk.Frame(main_frame)
            control_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Apply và Cancel buttons
            apply_btn = ttk.Button(control_frame, text="Apply Selection", command=lambda: self.apply_profile_selection(popup_window))
            apply_btn.pack(side=tk.RIGHT, padx=(5, 0))
            
            cancel_btn = ttk.Button(control_frame, text="Cancel", command=popup_window.destroy)
            cancel_btn.pack(side=tk.RIGHT, padx=(0, 5))
            
            # Refresh profiles before creating checkboxes
            self.log_auto_view("Refreshing profiles for multiple profile selection...")
            self.refresh_auto_view_profiles()
            
            # Tạo profile checkboxes trong popup
            self.create_popup_profile_checkboxes()
            
            # Apply theme to popup
            self.apply_popup_theme(popup_window)
            
            # Bind mouse wheel to popup window and all child widgets
            def bind_to_mousewheel(widget):
                """Bind mouse wheel events to widget and all its children"""
                widget.bind("<MouseWheel>", _on_mousewheel)  # Windows/Mac
                widget.bind("<Button-4>", _on_mousewheel_linux)  # Linux
                widget.bind("<Button-5>", _on_mousewheel_linux)  # Linux
                for child in widget.winfo_children():
                    bind_to_mousewheel(child)
            
            # Apply mouse wheel binding to the entire popup
            bind_to_mousewheel(popup_window)
            
            # Add keyboard navigation for scrolling
            def on_key_press(event):
                if event.keysym == "Up":
                    self.popup_profile_canvas.yview_scroll(-1, "units")
                elif event.keysym == "Down":
                    self.popup_profile_canvas.yview_scroll(1, "units")
                elif event.keysym == "Page_Up":
                    self.popup_profile_canvas.yview_scroll(-5, "units")
                elif event.keysym == "Page_Down":
                    self.popup_profile_canvas.yview_scroll(5, "units")
                elif event.keysym == "Home":
                    self.popup_profile_canvas.yview_moveto(0)
                elif event.keysym == "End":
                    self.popup_profile_canvas.yview_moveto(1)
            
            popup_window.bind("<Key>", on_key_press)
            popup_window.focus_set()  # Make sure popup can receive key events
            
        except Exception as e:
            self.log_auto_view(f"Error creating popup: {str(e)}")
            messagebox.showerror("Popup Error", f"Failed to create popup: {str(e)}")
    
    def create_popup_profile_checkboxes(self):
        """Tạo profile checkboxes trong popup window"""
        try:
            # Clear existing checkboxes
            for widget in self.popup_profile_scrollable_frame.winfo_children():
                widget.destroy()
            
            # Clear existing variables
            self.profile_checkboxes.clear()
            self.profile_vars.clear()
            
            if hasattr(self, 'profile_options') and self.profile_options:
                # Create new checkboxes
                for i, (option_text, profile_id, debug_port, status) in enumerate(self.profile_options):
                    var = tk.BooleanVar()
                    self.profile_vars[profile_id] = var
                    
                    # Create frame for each profile row
                    profile_row = ttk.Frame(self.popup_profile_scrollable_frame)
                    profile_row.pack(fill=tk.X, padx=5, pady=2)
                    
                    # Color code based on status
                    if status == 'Started':
                        status_icon = "🟢"
                    elif status == 'Available':
                        status_icon = "🔵"
                    else:
                        status_icon = "⚪"
                    
                    # Checkbox with status icon
                    checkbox = ttk.Checkbutton(
                        profile_row,
                        text=f"{status_icon} {option_text}",
                        variable=var,
                        command=self.popup_update_selection_count
                    )
                    checkbox.pack(side=tk.LEFT)
                    
                    # Store reference
                    self.profile_checkboxes[profile_id] = checkbox
                
                # Update selection count
                self.popup_update_selection_count()
                
                # Force update the scroll region after widgets are created
                self.popup_profile_scrollable_frame.update_idletasks()
                self.popup_profile_canvas.configure(scrollregion=self.popup_profile_canvas.bbox("all"))
                
        except Exception as e:
            self.log_auto_view(f"Error creating popup checkboxes: {str(e)}")
    
    def popup_update_selection_count(self):
        """Cập nhật selection count trong popup"""
        try:
            if hasattr(self, 'profile_vars'):
                selected_count = sum(1 for var in self.profile_vars.values() if var.get())
                total_count = len(self.profile_vars)
                
                # Update popup count label
                if hasattr(self, 'popup_profile_count_label'):
                    self.popup_profile_count_label.config(text=f"({selected_count}/{total_count} selected)")
                    
                    # Change color based on selection
                    if selected_count == 0:
                        self.popup_profile_count_label.config(foreground="red")
                    elif selected_count == total_count:
                        self.popup_profile_count_label.config(foreground="green")
                    else:
                        self.popup_profile_count_label.config(foreground="blue")
                
                # Update main count label
                if hasattr(self, 'profile_count_label'):
                    self.profile_count_label.config(text=f"({selected_count}/{total_count} selected)")
                    
        except Exception as e:
            self.log_auto_view(f"Error updating popup selection count: {str(e)}")
    
    def popup_select_all_profiles(self):
        """Select all profiles trong popup"""
        for var in self.profile_vars.values():
            var.set(True)
        self.popup_update_selection_count()
    
    def popup_clear_all_profiles(self):
        """Clear all selections trong popup"""
        for var in self.profile_vars.values():
            var.set(False)
        self.popup_update_selection_count()
    
    def popup_select_started_profiles(self):
        """Select only started profiles trong popup"""
        if hasattr(self, 'profile_options'):
            # Clear all first
            for var in self.profile_vars.values():
                var.set(False)
            
            # Select only started profiles
            for option in self.profile_options:
                profile_id = option[1]
                status = option[3]
                if status == 'Started' and profile_id in self.profile_vars:
                    self.profile_vars[profile_id].set(True)
            
            self.popup_update_selection_count()
    
    def popup_select_available_profiles(self):
        """Select only available profiles trong popup"""
        if hasattr(self, 'profile_options'):
            # Clear all first
            for var in self.profile_vars.values():
                var.set(False)
            
            # Select only available profiles
            for option in self.profile_options:
                profile_id = option[1]
                status = option[3]
                if status == 'Available' and profile_id in self.profile_vars:
                    self.profile_vars[profile_id].set(True)
            
            self.popup_update_selection_count()
    
    def popup_toggle_profile_sort(self):
        """Toggle profile sorting trong popup"""
        try:
            if self.profile_sort_order == "lowest_to_highest":
                # Currently sorted, so reset to default order
                self.popup_reset_profile_sort()
                self.popup_sort_btn.config(text="🔢 Sort by Name")
            else:
                # Currently not sorted, so sort from lowest to highest
                self.popup_sort_profiles_by_name()
                self.popup_sort_btn.config(text="🔄 Reset Sort")
                
        except Exception as e:
            self.log_auto_view(f"Error toggling popup sort: {str(e)}")
    
    def popup_sort_profiles_by_name(self):
        """Sort profiles by name trong popup"""
        try:
            if hasattr(self, 'profile_options') and self.profile_options:
                # Create a copy with names for sorting
                profiles_with_names = []
                for option in self.profile_options:
                    option_text, profile_id, debug_port, status = option
                    # Extract name from option_text
                    name = option_text.split(' - ')[0]
                    profiles_with_names.append((option_text, profile_id, debug_port, status, name))
                
                # Sort by extracted number
                def extract_number_from_name(name):
                    import re
                    numbers = re.findall(r'\d+', str(name))
                    return int(numbers[0]) if numbers else float('inf')
                
                # Sort by extracted number (lowest to highest)
                profiles_with_names.sort(key=lambda x: extract_number_from_name(x[4]))
                
                # Remove the name from the tuple
                sorted_profiles = [(option[0], option[1], option[2], option[3]) for option in profiles_with_names]
                
                # Update the stored profile options
                self.profile_options = sorted_profiles
                
                # Recreate checkboxes with sorted order
                self.create_popup_profile_checkboxes()
                
                # Update sort order
                self.profile_sort_order = "lowest_to_highest"
                
                # Update labels
                if hasattr(self, 'popup_sort_order_label'):
                    self.popup_sort_order_label.config(text="Sort: Lowest → Highest", foreground="green")
                
                if hasattr(self, 'popup_list_header_label'):
                    self.popup_list_header_label.config(text="Profile List - Sorted by Name (Lowest → Highest)", foreground="green")
                
                self.log_auto_view("Profiles sorted by name (lowest to highest) in popup")
                
        except Exception as e:
            self.log_auto_view(f"Error sorting profiles in popup: {str(e)}")
    
    def popup_reset_profile_sort(self):
        """Reset profile sort trong popup"""
        try:
            if hasattr(self, 'profile_options'):
                # Get the original profile data to show unsorted order
                response = requests.get(f"{self.api_base}/list", timeout=10)
                if response.status_code == 200:
                    profiles = response.json()
                    if isinstance(profiles, dict) and 'data' in profiles and profiles.get('code') == 0:
                        profiles_data = profiles['data']
                        
                        # Create profile options without sorting
                        profile_options = []
                        for profile_id, profile_info in profiles_data.items():
                            if isinstance(profile_info, dict):
                                name = profile_info.get('name', profile_id)
                                status = profile_info.get('status', 'Unknown')
                                debug_port = profile_info.get('debug_port', '')
                                
                                if debug_port:
                                    option_text = f"{name} - {status} (Port: {debug_port})"
                                else:
                                    option_text = f"{name} - {status}"
                                
                                profile_options.append((option_text, profile_id, debug_port, status))
                        
                        # Update the stored profile options (unsorted)
                        self.profile_options = profile_options
                        
                        # Recreate checkboxes with unsorted order
                        self.create_popup_profile_checkboxes()
                        
                        # Update sort order
                        self.profile_sort_order = "default"
                        
                        # Update labels
                        if hasattr(self, 'popup_sort_order_label'):
                            self.popup_sort_order_label.config(text="Sort: Default (API Order)", foreground="gray")
                        
                        if hasattr(self, 'popup_list_header_label'):
                            self.popup_list_header_label.config(text="Profile List - Default Order", foreground="gray")
                        
                        self.log_auto_view("Profile sort order reset to default in popup")
                        
        except Exception as e:
            self.log_auto_view(f"Error resetting sort in popup: {str(e)}")
    
    def apply_profile_selection(self, popup_window):
        """Apply profile selection từ popup và đóng popup"""
        try:
            # Update main profile count label
            if hasattr(self, 'profile_count_label'):
                selected_count = sum(1 for var in self.profile_vars.values() if var.get())
                total_count = len(self.profile_vars)
                self.profile_count_label.config(text=f"({selected_count}/{total_count} selected)")
                
                # Change color based on selection
                if selected_count == 0:
                    self.profile_count_label.config(foreground="red")
                elif selected_count == total_count:
                    self.profile_count_label.config(foreground="green")
                else:
                    self.profile_count_label.config(foreground="blue")
            
            # Log the selection
            selected_profiles = []
            for option in self.profile_options:
                profile_id = option[1]
                if profile_id in self.profile_vars and self.profile_vars[profile_id].get():
                    selected_profiles.append(profile_id)
            
            self.log_auto_view(f"Applied profile selection: {len(selected_profiles)} profiles selected")
            
            # Close popup
            popup_window.destroy()
            
            # Show confirmation
            messagebox.showinfo("Selection Applied", 
                              f"Profile selection applied successfully!\n"
                              f"Selected {len(selected_profiles)} profiles.")
            
        except Exception as e:
            self.log_auto_view(f"Error applying profile selection: {str(e)}")
            messagebox.showerror("Apply Error", f"Failed to apply selection: {str(e)}")
    
    def apply_popup_theme(self, popup_window):
        """Apply theme cho popup window"""
        try:
            popup_window.configure(bg=self.current_theme['bg'])
            
            # Apply theme to canvas
            if hasattr(self, 'popup_profile_canvas'):
                self.popup_profile_canvas.configure(bg=self.current_theme['text_bg'])
                
        except Exception as e:
            print(f"Failed to apply theme to popup: {e}")
    
    def select_all_profiles(self):
        """Select all profiles - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            if hasattr(self, 'profile_vars') and self.profile_vars:
                for var in self.profile_vars.values():
                    var.set(True)
                self.update_selection_count()
                self.log_auto_view("All profiles selected via main interface")
            else:
                self.log_auto_view("No profiles available for selection")
        except Exception as e:
            self.log_auto_view(f"Error selecting all profiles: {str(e)}")
    
    def clear_all_profiles(self):
        """Clear all selections - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            if hasattr(self, 'profile_vars') and self.profile_vars:
                for var in self.profile_vars.values():
                    var.set(False)
                self.update_selection_count()
                self.log_auto_view("All profile selections cleared via main interface")
            else:
                self.log_auto_view("No profiles available to clear")
        except Exception as e:
            self.log_auto_view(f"Error clearing all profiles: {str(e)}")
    
    def select_started_profiles(self):
        """Select only started profiles - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            if hasattr(self, 'profile_options') and hasattr(self, 'profile_vars'):
                # Clear all first
                for var in self.profile_vars.values():
                    var.set(False)
                
                # Select only started profiles
                for option in self.profile_options:
                    profile_id = option[1]
                    status = option[3]
                    if status == 'Started' and profile_id in self.profile_vars:
                        self.profile_vars[profile_id].set(True)
                
                self.update_selection_count()
                self.log_auto_view("Started profiles selected via main interface")
            else:
                self.log_auto_view("No profiles available for selection")
        except Exception as e:
            self.log_auto_view(f"Error selecting started profiles: {str(e)}")
    
    def select_available_profiles(self):
        """Select only available profiles - now handled by popup"""
        # This method is kept for compatibility but now delegates to popup
        try:
            if hasattr(self, 'profile_options') and hasattr(self, 'profile_vars'):
                # Clear all first
                for var in self.profile_vars.values():
                    var.set(False)
                
                # Select only available profiles
                for option in self.profile_options:
                    profile_id = option[1]
                    status = option[3]
                    if status == 'Available' and profile_id in self.profile_vars:
                        self.profile_vars[profile_id].set(True)
                
                self.update_selection_count()
                self.log_auto_view("Available profiles selected via main interface")
            else:
                self.log_auto_view("No profiles available for selection")
        except Exception as e:
            self.log_auto_view(f"Error selecting available profiles: {str(e)}")
    
    def get_selected_profiles_info(self):
        """Get selected profiles information for multiple mode"""
        if not hasattr(self, 'profile_options'):
            return []
        
        if self.profile_mode_var.get() == "single":
            # Single mode
            profile_id, debug_port, status = self.get_selected_profile_info()
            if profile_id:
                return [(profile_id, debug_port, status)]
            return []
        else:
            # Multiple mode - use profile_vars from popup
            selected_profiles = []
            if hasattr(self, 'profile_vars'):
                for option in self.profile_options:
                    profile_id = option[1]
                    if profile_id in self.profile_vars and self.profile_vars[profile_id].get():
                        selected_profiles.append((option[1], option[2], option[3]))  # profile_id, debug_port, status
            return selected_profiles
    
    def log_auto_view(self, message):
        """Add message to auto view log"""
        try:
            if hasattr(self, 'auto_view_log'):
                timestamp = time.strftime("%H:%M:%S")
                self.auto_view_log.insert(tk.END, f"[{timestamp}] {message}\n")
                self.auto_view_log.see(tk.END)
                self.root.update()
            else:
                # Fallback to print if log widget not ready
                print(f"[AUTO_VIEW] {message}")
        except Exception as e:
            print(f"[LOG_ERROR] {message} (Error: {e})")
    
    def start_auto_view(self):
        """Start the auto view process"""
        urls_text = self.url_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter at least one URL")
            return
        
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        if not urls:
            messagebox.showwarning("Warning", "No valid URLs found")
            return
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if url.startswith(('http://', 'https://')):
                valid_urls.append(url)
            else:
                # Try to add https:// if no protocol specified
                if url.startswith('www.') or '.' in url:
                    valid_urls.append(f'https://{url}')
                else:
                    self.log_auto_view(f"Warning: Invalid URL format: {url}")
        
        if not valid_urls:
            messagebox.showerror("Error", "No valid URLs found. URLs must start with http:// or https:// or be a valid domain.")
            return
        
        self.log_auto_view(f"Validated {len(valid_urls)} URLs out of {len(urls)} input")
        
        # Check selected profiles
        if self.use_profile_var.get():
            selected_profiles = self.get_selected_profiles_info()
            if not selected_profiles:
                messagebox.showwarning("Warning", "Please select at least one profile")
                return
            self.log_auto_view(f"Selected {len(selected_profiles)} profiles for auto view")
        else:
            selected_profiles = []
        
        # Validate time range if random interval is enabled
        if self.random_time_interval_var.get():
            min_total_seconds = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
            max_total_seconds = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
            
            if min_total_seconds >= max_total_seconds:
                messagebox.showerror("Error", "Minimum time must be less than maximum time")
                return
            if min_total_seconds < 10:
                messagebox.showerror("Error", "Minimum time must be at least 10 seconds")
                return
            if max_total_seconds > 86400:  # 24 hours
                messagebox.showerror("Error", "Maximum time cannot exceed 24 hours")
                return
                
            self.log_auto_view(f"Time range validated: {self.min_hours_var.get():02d}:{self.min_minutes_var.get():02d}:{self.min_seconds_var.get():02d} - {self.max_hours_var.get():02d}:{self.max_minutes_var.get():02d}:{self.max_seconds_var.get():02d}")
        
        # Validate search keywords if enabled
        if hasattr(self, 'amazon_enable_search_var') and self.amazon_enable_search_var.get():
            # Get keywords from Amazon Search tab
            keywords = self.get_amazon_keywords_list()
            
            if not keywords:
                messagebox.showerror("Error", "Please add at least one Amazon keyword for search in the Amazon Search tab")
                return
            
            # Validate search frequency
            search_frequency = self.amazon_search_frequency_var.get()
            if search_frequency < 1 or search_frequency > 10:
                messagebox.showerror("Error", "Search frequency must be between 1 and 10 URLs")
                return
            
            self.log_auto_view(f"Amazon search validated: {len(keywords)} keywords, search every {search_frequency} URLs")
        
        with self._lock:
            self.auto_view_running = True
        
        # Reset used keywords for new auto view session
        self.used_keywords.clear()
        self.log_auto_view("Reset used keywords for new session")
        
        self.start_auto_view_btn.config(state=tk.DISABLED)
        self.stop_auto_view_btn.config(state=tk.NORMAL)
        self.auto_view_status.config(text="Status: Starting...", foreground="orange")
        
        # Clear log
        self.auto_view_log.delete("1.0", tk.END)
        
        # Start in separate thread with validated URLs
        thread = threading.Thread(target=self.run_auto_view, args=(valid_urls, selected_profiles))
        thread.daemon = True
        thread.start()
    
    def stop_auto_view(self):
        """Stop the auto view process"""
        with self._lock:
            self.auto_view_running = False
        
        self.auto_view_status.config(text="Status: Stopping...", foreground="orange")
        self.log_auto_view("Stop requested by user")
        
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.log_auto_view(f"Error closing driver: {str(e)}")
            self.driver = None
        
        self.start_auto_view_btn.config(state=tk.NORMAL)
        self.stop_auto_view_btn.config(state=tk.DISABLED)
        self.auto_view_status.config(text="Status: Stopped", foreground="red")
    
    def is_auto_view_running(self):
        """Thread-safe check if auto view is running"""
        with self._lock:
            return self.auto_view_running
    
    def run_auto_view(self, urls, selected_profiles):
        """Main auto view process"""
        try:
            self.log_auto_view(f"Starting auto view with {len(urls)} URLs")
            
            if self.use_profile_var.get() and selected_profiles:
                # Multiple profiles mode - open all browsers simultaneously
                self.log_auto_view(f"Setting up {len(selected_profiles)} browsers simultaneously...")
                
                # Step 1: Setup all browsers first
                browsers = []
                for profile_idx, (profile_id, debug_port, status) in enumerate(selected_profiles):
                    if not self.is_auto_view_running():
                        break
                    
                    self.log_auto_view(f"Setting up browser {profile_idx + 1}/{len(selected_profiles)}: {profile_id[:8]}...")
                    
                    driver = self.setup_browser_for_profile(profile_id, debug_port, status)
                    if driver:
                        browsers.append((driver, profile_id))
                        self.log_auto_view(f"✓ Browser {profile_idx + 1} ready: {profile_id[:8]}")
                    else:
                        self.log_auto_view(f"✗ Failed to setup browser {profile_idx + 1}: {profile_id[:8]}")
                
                if not browsers:
                    self.log_auto_view("No browsers available, stopping...")
                    return
                
                self.log_auto_view(f"All {len(browsers)} browsers ready! Starting parallel auto view...")
                
                # Step 2: Run auto view on all browsers in parallel
                import threading
                threads = []
                
                for driver, profile_id in browsers:
                    thread = threading.Thread(
                        target=self.run_auto_view_on_browser, 
                        args=(driver, urls, profile_id)
                    )
                    thread.daemon = True
                    threads.append((thread, driver, profile_id))
                    thread.start()
                    self.log_auto_view(f"Started auto view thread for {profile_id[:8]}")
                
                # Step 3: Wait for all threads to complete
                self.log_auto_view("Waiting for all browsers to complete...")
                completed_browsers = []
                for thread, driver, profile_id in threads:
                    thread.join()
                    try:
                        driver.quit()
                        self.log_auto_view(f"Closed browser {profile_id[:8]}")
                        completed_browsers.append(profile_id[:8])
                        
                        # Show popup for individual browser completion
                        self.show_browser_completion_popup(profile_id[:8])
                        
                    except Exception as e:
                        self.log_auto_view(f"Error closing browser {profile_id[:8]}: {str(e)}")
                
                self.log_auto_view("All browsers completed!")
                
                # Step 4: Cleanup and refresh profile states
                self.cleanup_profiles_after_auto_view(selected_profiles)
                
                # Show final completion popup
                self.show_tools_completion_popup(len(completed_browsers))
            
            else:
                # Fallback to regular Chrome
                self.log_auto_view("Using regular Chrome browser")
                chrome_options = Options()
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                self.driver = webdriver.Chrome(options=chrome_options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                self.auto_view_status.config(text="Status: Running", foreground="green")
                
                for i, url in enumerate(urls):
                    if not self.is_auto_view_running():
                        break
                    
                    self.log_auto_view(f"Visiting URL {i+1}/{len(urls)}: {url}")
                    
                    try:
                        # Navigate to URL with retry mechanism
                        if not self.navigate_with_retry_fallback(url, f"URL {i+1}"):
                            self.log_auto_view(f"Failed to load URL {i+1} after retries, skipping to next URL")
                            continue
                        
                        self.log_auto_view("Page loaded, starting auto scroll")
                        
                        # Auto scroll process
                        self.auto_scroll_page()
                        
                        # Random clicks if enabled
                        if self.random_clicks_var.get():
                            self.random_click_elements()
                        
                        # Check if we should perform keyword search
                        if hasattr(self, 'amazon_enable_search_var') and self.amazon_enable_search_var.get() and (i + 1) % self.amazon_search_frequency_var.get() == 0:
                            self.log_auto_view(f"Performing Amazon keyword search after {i + 1} URLs")
                            self.perform_keyword_search_fallback()
                        
                    except Exception as e:
                        self.log_auto_view(f"Error with URL {url}: {str(e)}")
                        continue
            
            self.log_auto_view("Auto view completed successfully")
            
            # Show completion popup for fallback Chrome
            self.show_tools_completion_popup(1)
            
        except Exception as e:
            self.log_auto_view(f"Auto view error: {str(e)}")
            
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception as e:
                    self.log_auto_view(f"Error closing driver: {str(e)}")
                self.driver = None
            
            if self.is_auto_view_running():
                with self._lock:
                    self.auto_view_running = False
                self.start_auto_view_btn.config(state=tk.NORMAL)
                self.stop_auto_view_btn.config(state=tk.DISABLED)
                self.auto_view_status.config(text="Status: Completed", foreground="blue")
                
                # Refresh profiles after completion to ensure consistent state
                if self.use_profile_var.get():
                    self.refresh_auto_view_profiles()
    
    def auto_scroll_page(self):
        """Automatically scroll the page down and then up - for fallback Chrome"""
        # Use the same smooth scrolling for fallback Chrome
        self.auto_scroll_page_with_driver(self.driver, "Chrome")
    
    def random_click_elements(self):
        """Randomly click on clickable elements - Focus on product images"""
        try:
            # Priority selectors for product-related elements
            priority_selectors = [
                "img[src*='product']",           # Product images
                "img[src*='item']",              # Item images
                "img[src*='goods']",             # Goods images
                ".product img",                   # Product container images
                ".item img",                      # Item container images
                ".goods img",                     # Goods container images
                "[data-product-id]",              # Product data attributes
                "[data-item-id]",                 # Item data attributes
                ".product-card img",              # Product card images
                ".product-thumbnail",             # Product thumbnails
                ".product-image",                 # Product image classes
                ".item-image",                    # Item image classes
            ]
            
            # Secondary selectors for other clickable elements
            secondary_selectors = [
                "a[href]",                       # Links
                "button",                        # Buttons
                "[onclick]",                     # Clickable elements
                ".product",                      # Product containers
                ".item",                         # Item containers
                "[role='button']",               # Button role elements
                ".add-to-cart",                  # Add to cart buttons
                ".buy-now",                      # Buy now buttons
                ".view-details",                 # View details buttons
            ]
            
            all_elements = []
            
            # First, try to find product images (priority)
            for selector in priority_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Check if element is visible and clickable
                        if element.is_displayed() and element.is_enabled():
                            # Get element size to ensure it's clickable
                            size = element.size
                            if size['width'] > 20 and size['height'] > 20:
                                all_elements.append(('priority', element))
                except Exception as e:
                    self.log_auto_view(f"Error finding elements with selector {selector}: {str(e)}")
                    continue
            
            # Then, add secondary elements if not enough priority elements
            if len(all_elements) < 3:
                for selector in secondary_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                size = element.size
                                if size['width'] > 20 and size['height'] > 20:
                                    all_elements.append(('secondary', element))
                    except Exception as e:
                        self.log_auto_view(f"Error finding elements with selector {selector}: {str(e)}")
                        continue
            
            if all_elements and self.is_auto_view_running():
                # Prioritize product images
                priority_elements = [elem for elem_type, elem in all_elements if elem_type == 'priority']
                secondary_elements = [elem for elem_type, elem in all_elements if elem_type == 'secondary']
                
                # Select elements with preference for product images
                selected_elements = []
                if priority_elements:
                    # Select 1-2 priority elements (product images)
                    priority_count = min(2, len(priority_elements))
                    selected_elements.extend(random.sample(priority_elements, priority_count))
                
                if secondary_elements and len(selected_elements) < 3:
                    # Add 1-2 secondary elements if needed
                    remaining_count = min(3 - len(selected_elements), len(secondary_elements))
                    selected_elements.extend(random.sample(secondary_elements, remaining_count))
                
                for element in selected_elements:
                    if not self.is_auto_view_running():
                        break
                    
                    try:
                        # Scroll element into view smoothly
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                        
                        # Human-like pause before clicking
                        pre_click_pause = random.uniform(0.8, 1.5)
                        time.sleep(pre_click_pause)
                        
                        # Get element info for logging
                        tag_name = element.tag_name
                        element_text = element.text[:50] if element.text else "No text"
                        
                        # Get image source if it's an image
                        if tag_name == 'img':
                            src = element.get_attribute('src') or element.get_attribute('data-src') or "No src"
                            alt = element.get_attribute('alt') or "No alt"
                            self.log_auto_view(f"Clicking product image: {alt} ({src[:50]}...)")
                        else:
                            self.log_auto_view(f"Clicking {tag_name}: {element_text}")
                        
                        # Human-like click with slight mouse movement simulation
                        self.human_like_click_fallback(element)
                        
                        # Wait after click (longer for product images)
                        if tag_name == 'img':
                            post_click_pause = random.uniform(2, 4)  # Longer pause for product images
                        else:
                            post_click_pause = random.uniform(1, 3)
                        
                        self.log_auto_view(f"Waiting {post_click_pause:.1f}s after click")
                        time.sleep(post_click_pause)
                        
                    except Exception as e:
                        self.log_auto_view(f"Click failed: {str(e)}")
                        continue
                        
        except Exception as e:
            self.log_auto_view(f"Random click error: {str(e)}")
    
    def human_like_click_fallback(self, element):
        """Fallback human-like click for regular Chrome driver"""
        try:
            # Get element location and size
            location = element.location
            size = element.size
            
            # Calculate center point
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
            
            # Add slight randomness to click position (like human hand tremor)
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            # Use JavaScript to simulate mouse movement and click
            self.driver.execute_script(f"""
                // Create and dispatch mouse events for human-like interaction
                const element = arguments[0];
                const rect = element.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2 + {offset_x};
                const centerY = rect.top + rect.height / 2 + {offset_y};
                
                // Mouse move event
                const moveEvent = new MouseEvent('mousemove', {{
                    bubbles: true,
                    cancelable: true,
                    clientX: centerX,
                    clientY: centerY
                }});
                document.elementFromPoint(centerX, centerY).dispatchEvent(moveEvent);
                
                // Small delay like human
                setTimeout(() => {{
                    // Mouse down event
                    const downEvent = new MouseEvent('mousedown', {{
                        bubbles: true,
                        cancelable: true,
                        clientX: centerX,
                        clientY: centerY,
                        button: 0
                    }});
                    element.dispatchEvent(downEvent);
                    
                    // Mouse up and click events
                    setTimeout(() => {{
                        const upEvent = new MouseEvent('mouseup', {{
                            bubbles: true,
                            cancelable: true,
                            clientX: centerX,
                            clientY: centerY,
                            button: 0
                        }});
                        element.dispatchEvent(upEvent);
                        
                        const clickEvent = new MouseEvent('click', {{
                            bubbles: true,
                            cancelable: true,
                            clientX: centerX,
                            clientY: centerY,
                            button: 0
                        }});
                        element.dispatchEvent(clickEvent);
                    }}, 50);
                }}, 100);
            """, element)
            
        except Exception as e:
            # Fallback to regular click if JavaScript simulation fails
            element.click()
    
    def start_profile_for_auto_view(self, profile_id):
        """Start a profile for auto view use"""
        try:
            self.log_auto_view(f"Starting profile {profile_id}...")
            
            url = f"{self.api_base}/profile/start/{profile_id}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                self.log_auto_view(f"Profile {profile_id} started successfully")
                return True
            else:
                self.log_auto_view(f"Failed to start profile {profile_id}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_auto_view(f"Error starting profile {profile_id}: {str(e)}")
            return False
    
    def setup_browser_for_profile(self, profile_id, debug_port, status):
        """Setup browser for a specific profile"""
        try:
            if status == 'Started' and debug_port:
                # Connect to existing browser
                self.log_auto_view(f"Connecting to profile: {profile_id} on port {debug_port}")
                chrome_options = Options()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                
                # Add retry logic for connection
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        self.log_auto_view("Successfully connected to undetectable browser")
                        return driver
                    except Exception as e:
                        if attempt < max_retries - 1:
                            self.log_auto_view(f"Connection attempt {attempt + 1} failed, retrying... Error: {str(e)}")
                            time.sleep(2)
                        else:
                            self.log_auto_view(f"Failed to connect after {max_retries} attempts: {str(e)}")
                            # Profile might be in inconsistent state, try to reset it
                            self.log_auto_view(f"Attempting to reset profile {profile_id[:8]}...")
                            if self.stop_profile_for_cleanup(profile_id):
                                time.sleep(3)
                                # Try to start it again
                                if self.start_profile_for_auto_view(profile_id):
                                    time.sleep(3)
                                    # Get updated info
                                    self.refresh_auto_view_profiles()
                                    # Try to find the profile again
                                    if hasattr(self, 'profile_options'):
                                        for option in self.profile_options:
                                            if option[1] == profile_id and option[2]:  # found with debug_port
                                                chrome_options = Options()
                                                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{option[2]}")
                                                try:
                                                    driver = webdriver.Chrome(options=chrome_options)
                                                    self.log_auto_view(f"Successfully connected after resetting profile {profile_id[:8]}")
                                                    return driver
                                                except Exception as e2:
                                                    self.log_auto_view(f"Still failed to connect after reset: {str(e2)}")
                                                    return None
                            return None
                
            elif status == 'Available':
                # Start profile first
                self.log_auto_view(f"Starting profile {profile_id}...")
                if self.start_profile_for_auto_view(profile_id):
                    time.sleep(3)
                    # Get updated info after starting
                    self.refresh_auto_view_profiles()
                    # Find the profile in updated list
                    if hasattr(self, 'profile_options'):
                        for option in self.profile_options:
                            if option[1] == profile_id and option[2]:  # found with debug_port
                                chrome_options = Options()
                                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{option[2]}")
                                try:
                                    driver = webdriver.Chrome(options=chrome_options)
                                    self.log_auto_view(f"Connected to newly started profile")
                                    return driver
                                except Exception as e:
                                    self.log_auto_view(f"Failed to connect to newly started profile: {str(e)}")
                                    return None
                    self.log_auto_view(f"Failed to get debug port for started profile")
                    return None
                else:
                    self.log_auto_view(f"Failed to start profile {profile_id}")
                    return None
            else:
                self.log_auto_view(f"Profile {profile_id} status: {status}, cannot use")
                return None
                
        except Exception as e:
            self.log_auto_view(f"Error setting up browser for profile {profile_id}: {str(e)}")
            return None
    
    def run_auto_view_on_browser(self, driver, urls, profile_id):
        """Run auto view process on a specific browser"""
        try:
            self.auto_view_status.config(text=f"Status: Running on {profile_id[:8]}...", foreground="green")
            
            for i, url in enumerate(urls):
                if not self.is_auto_view_running():
                    break
                
                self.log_auto_view(f"[{profile_id[:8]}] Visiting URL {i+1}/{len(urls)}: {url}")
                
                try:
                    # Navigate to URL with retry mechanism
                    if not self.navigate_with_retry(driver, url, profile_id, f"URL {i+1}"):
                        self.log_auto_view(f"[{profile_id[:8]}] Failed to load URL {i+1} after retries, skipping to next URL")
                        continue
                    
                    self.log_auto_view(f"[{profile_id[:8]}] Page loaded, starting auto scroll")
                    
                    # Auto scroll process
                    self.auto_scroll_page_with_driver(driver, profile_id)
                    
                    # Random clicks if enabled
                    if self.random_clicks_var.get():
                        self.random_click_elements_with_driver(driver, profile_id)
                    
                    # Check if we should perform keyword search
                    if hasattr(self, 'amazon_enable_search_var') and self.amazon_enable_search_var.get() and (i + 1) % self.amazon_search_frequency_var.get() == 0:
                        self.log_auto_view(f"[{profile_id[:8]}] Performing Amazon keyword search after {i + 1} URLs")
                        self.perform_keyword_search(driver, profile_id)
                    
                except Exception as e:
                    self.log_auto_view(f"[{profile_id[:8]}] Error with URL {url}: {str(e)}")
                    continue
            
            self.log_auto_view(f"[{profile_id[:8]}] Completed auto view")
            
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Auto view error: {str(e)}")
    
    def detect_product_gallery(self, driver, profile_id):
        """Detect if current page has product gallery and interact with it"""
        try:
            # Look for common product gallery indicators
            gallery_selectors = [
                ".product-gallery",
                ".product-images",
                ".image-gallery",
                ".product-slider",
                ".product-carousel",
                "[data-gallery]",
                ".swiper-container",
                ".slick-slider"
            ]
            
            gallery_found = False
            for selector in gallery_selectors:
                try:
                    gallery = driver.find_element(By.CSS_SELECTOR, selector)
                    if gallery.is_displayed():
                        gallery_found = True
                        self.log_auto_view(f"[{profile_id[:8]}] Found product gallery: {selector}")
                        
                        # Look for navigation arrows/buttons
                        nav_selectors = [
                            ".gallery-nav",
                            ".gallery-arrow",
                            ".gallery-next",
                            ".gallery-prev",
                            ".swiper-button-next",
                            ".swiper-button-prev",
                            ".slick-next",
                            ".slick-prev"
                        ]
                        
                        for nav_selector in nav_selectors:
                            try:
                                nav_elements = driver.find_elements(By.CSS_SELECTOR, nav_selector)
                                if nav_elements:
                                    # Click on a few navigation elements
                                    for i, nav in enumerate(nav_elements[:2]):  # Max 2 clicks
                                        if nav.is_displayed() and nav.is_enabled():
                                            self.log_auto_view(f"[{profile_id[:8]}] Navigating gallery: {nav_selector}")
                                            nav.click()
                                            time.sleep(random.uniform(1.5, 2.5))
                                            break
                            except Exception as e:
                                continue
                        
                        # Look for thumbnail images
                        thumbnail_selectors = [
                            ".gallery-thumbnail",
                            ".product-thumb",
                            ".image-thumb",
                            ".gallery-item img"
                        ]
                        
                        for thumb_selector in thumbnail_selectors:
                            try:
                                thumbnails = driver.find_elements(By.CSS_SELECTOR, thumb_selector)
                                if thumbnails:
                                    # Click on a few thumbnails
                                    for i, thumb in enumerate(thumbnails[:3]):  # Max 3 clicks
                                        if thumb.is_displayed() and thumb.is_enabled():
                                            self.log_auto_view(f"[{profile_id[:8]}] Clicking gallery thumbnail {i+1}")
                                            thumb.click()
                                            time.sleep(random.uniform(1.0, 2.0))
                                            break
                            except Exception as e:
                                continue
                        
                        break
                        
                except Exception as e:
                    continue
            
            return gallery_found
            
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error detecting product gallery: {str(e)}")
            return False
    
    def auto_scroll_page_with_driver(self, driver, profile_id):
        """Auto scroll with specific driver - smooth human-like scrolling with product gallery detection"""
        scroll_speed = self.scroll_speed_var.get()
        time_per_page = self.get_random_time_per_page()
        
        try:
            # Get page dimensions
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            self.log_auto_view(f"[{profile_id[:8]}] Scrolling page (height: {page_height}px, time: {time_per_page}s)")
            
            # Human-like smooth scrolling down
            self.smooth_scroll_down(driver, page_height, viewport_height, profile_id)
            
            if not self.is_auto_view_running():
                return
            
            # Random pause at bottom (like human reading)
            pause_time = random.uniform(1.5, 3.5)
            self.log_auto_view(f"[{profile_id[:8]}] Pausing at bottom for {pause_time:.1f}s")
            time.sleep(pause_time)
            
            if not self.is_auto_view_running():
                return
            
            # Check for product gallery and interact with it
            if self.detect_product_gallery(driver, profile_id):
                self.log_auto_view(f"[{profile_id[:8]}] Interacted with product gallery")
                time.sleep(random.uniform(2, 4))
            
            if not self.is_auto_view_running():
                return
            
            self.log_auto_view(f"[{profile_id[:8]}] Scrolling back to top")
            
            # Human-like smooth scrolling up
            self.smooth_scroll_up(driver, page_height, profile_id)
            
            # Wait remaining time
            used_time = time.time() - getattr(self, '_scroll_start_time', time.time())
            remaining_time = max(0, time_per_page - used_time)
            if remaining_time > 0 and self.is_auto_view_running():
                self.log_auto_view(f"[{profile_id[:8]}] Waiting {remaining_time:.1f}s before next action")
                time.sleep(remaining_time)
                
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Scroll error: {str(e)}")
    
    def smooth_scroll_down(self, driver, page_height, viewport_height, profile_id):
        """Smooth scrolling down like human - More natural movement"""
        self._scroll_start_time = time.time()
        current_position = 0
        
        while current_position < page_height - viewport_height and self.is_auto_view_running():
            # Variable scroll amount (like human - sometimes small, sometimes bigger)
            if random.random() < 0.25:  # 25% chance of small scroll
                scroll_amount = random.randint(40, 120)
            elif random.random() < 0.6:  # 35% chance of medium scroll
                scroll_amount = random.randint(150, 300)
            else:  # 40% chance of larger scroll
                scroll_amount = random.randint(300, 500)
            
            # Add some randomness to make it more human-like
            scroll_amount += random.randint(-15, 25)
            
            # Don't overshoot
            next_position = min(current_position + scroll_amount, page_height - viewport_height)
            
            # Smooth animation with easing
            self.smooth_scroll_to_position(driver, current_position, next_position)
            current_position = next_position
            
            # Human-like pause between scrolls
            pause = self.get_human_pause()
            time.sleep(pause)
            
            # Occasionally pause longer (like reading content)
            if random.random() < 0.12:  # 12% chance to pause longer
                long_pause = random.uniform(1.0, 3.0)
                self.log_auto_view(f"[{profile_id[:8]}] Reading content... ({long_pause:.1f}s)")
                time.sleep(long_pause)
            
            # Sometimes scroll in smaller increments (like reading carefully)
            if random.random() < 0.08:  # 8% chance for careful reading
                micro_scroll = random.randint(20, 60)
                if current_position + micro_scroll < page_height - viewport_height:
                    self.smooth_scroll_to_position(driver, current_position, current_position + micro_scroll)
                    current_position += micro_scroll
                    time.sleep(random.uniform(0.5, 1.2))
    
    def smooth_scroll_up(self, driver, page_height, profile_id):
        """Smooth scrolling up like human - Faster but still natural"""
        current_position = driver.execute_script("return window.pageYOffset")
        
        while current_position > 0 and self.is_auto_view_running():
            # Faster scrolling up (humans usually scroll up faster)
            if random.random() < 0.3:  # 30% chance of fast scroll
                scroll_amount = random.randint(400, 700)
            else:  # 70% chance of normal scroll
                scroll_amount = random.randint(250, 500)
            
            scroll_amount += random.randint(-30, 40)
            
            next_position = max(current_position - scroll_amount, 0)
            
            # Smooth animation
            self.smooth_scroll_to_position(driver, current_position, next_position)
            current_position = next_position
            
            # Shorter pauses when scrolling up
            pause = random.uniform(0.08, 0.3)
            time.sleep(pause)
            
            # Occasionally pause to check something
            if random.random() < 0.05:  # 5% chance to pause
                check_pause = random.uniform(0.3, 0.8)
                time.sleep(check_pause)
    
    def smooth_scroll_to_position(self, driver, start_pos, end_pos):
        """Smooth scroll animation between two positions - More human-like"""
        distance = abs(end_pos - start_pos)
        if distance == 0:
            return
        
        # Calculate number of animation steps (more steps = smoother)
        steps = max(8, min(25, distance // 25))  # Increased steps for smoother animation
        step_size = (end_pos - start_pos) / steps
        
        # Add slight randomness to make it more human-like
        random_offset = random.randint(-2, 2)
        
        for i in range(steps):
            if not self.is_auto_view_running():
                break
                
            # Easing function (starts fast, slows down at end)
            progress = (i + 1) / steps
            eased_progress = self.ease_out_cubic(progress)
            
            # Fixed calculation: remove the extra multiplication by steps
            current_pos = start_pos + (step_size * eased_progress)
            current_pos = int(current_pos + random_offset)
            
            # Use smooth scroll behavior with CSS
            driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_pos},
                    behavior: 'smooth'
                }});
            """)
            
            # Variable delay between animation frames (more human-like)
            if i < steps * 0.3:  # First 30% - faster
                delay = random.uniform(0.015, 0.025)
            elif i < steps * 0.7:  # Middle 40% - medium
                delay = random.uniform(0.02, 0.03)
            else:  # Last 30% - slower
                delay = random.uniform(0.025, 0.035)
            
            time.sleep(delay)
    
    def ease_out_cubic(self, t):
        """Cubic easing out function for natural scroll animation"""
        return 1 - pow(1 - t, 3)
    
    def ease_in_out_quint(self, t):
        """Quintic easing in-out for more natural movement"""
        if t < 0.5:
            return 16 * t * t * t * t * t
        else:
            f = ((2 * t) - 2)
            return 0.5 * f * f * f * f * f + 1
    
    def get_human_pause(self):
        """Get human-like pause duration between scrolls"""
        # Most pauses are short, but occasionally longer
        if random.random() < 0.75:  # 75% short pauses
            return random.uniform(0.15, 0.6)
        elif random.random() < 0.8:  # 20% medium pauses
            return random.uniform(0.6, 1.5)
        else:  # 5% longer pauses (like reading)
            return random.uniform(1.5, 3.0)
    
    def random_click_elements_with_driver(self, driver, profile_id):
        """Random click with specific driver - Focus on product images and human-like behavior"""
        try:
            # Priority selectors for product-related elements
            priority_selectors = [
                "img[src*='product']",           # Product images
                "img[src*='item']",              # Item images
                "img[src*='goods']",             # Goods images
                ".product img",                   # Product container images
                ".item img",                      # Item container images
                ".goods img",                     # Goods container images
                "[data-product-id]",              # Product data attributes
                "[data-item-id]",                 # Item data attributes
                ".product-card img",              # Product card images
                ".product-thumbnail",             # Product thumbnails
                ".product-image",                 # Product image classes
                ".item-image",                    # Item image classes
            ]
            
            # Secondary selectors for other clickable elements
            secondary_selectors = [
                "a[href]",                       # Links
                "button",                        # Buttons
                "[onclick]",                     # Clickable elements
                ".product",                      # Product containers
                ".item",                         # Item containers
                "[role='button']",               # Button role elements
                ".add-to-cart",                  # Add to cart buttons
                ".buy-now",                      # Buy now buttons
                ".view-details",                 # View details buttons
            ]
            
            all_elements = []
            
            # First, try to find product images (priority)
            for selector in priority_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        # Check if element is visible and clickable
                        if element.is_displayed() and element.is_enabled():
                            # Get element size to ensure it's clickable
                            size = element.size
                            if size['width'] > 20 and size['height'] > 20:
                                all_elements.append(('priority', element))
                except Exception as e:
                    self.log_auto_view(f"[{profile_id[:8]}] Error finding elements with selector {selector}: {str(e)}")
                    continue
            
            # Then, add secondary elements if not enough priority elements
            if len(all_elements) < 3:
                for selector in secondary_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                size = element.size
                                if size['width'] > 20 and size['height'] > 20:
                                    all_elements.append(('secondary', element))
                    except Exception as e:
                        self.log_auto_view(f"[{profile_id[:8]}] Error finding elements with selector {selector}: {str(e)}")
                        continue
            
            if all_elements and self.is_auto_view_running():
                # Prioritize product images
                priority_elements = [elem for elem_type, elem in all_elements if elem_type == 'priority']
                secondary_elements = [elem for elem_type, elem in all_elements if elem_type == 'secondary']
                
                # Select elements with preference for product images
                selected_elements = []
                if priority_elements:
                    # Select 1-2 priority elements (product images)
                    priority_count = min(2, len(priority_elements))
                    selected_elements.extend(random.sample(priority_elements, priority_count))
                
                if secondary_elements and len(selected_elements) < 3:
                    # Add 1-2 secondary elements if needed
                    remaining_count = min(3 - len(selected_elements), len(secondary_elements))
                    selected_elements.extend(random.sample(secondary_elements, remaining_count))
                
                for element in selected_elements:
                    if not self.is_auto_view_running():
                        break
                    
                    try:
                        # Scroll element into view smoothly
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                        
                        # Human-like pause before clicking
                        pre_click_pause = random.uniform(0.8, 1.5)
                        time.sleep(pre_click_pause)
                        
                        # Get element info for logging
                        tag_name = element.tag_name
                        element_text = element.text[:50] if element.text else "No text"
                        
                        # Get image source if it's an image
                        if tag_name == 'img':
                            src = element.get_attribute('src') or element.get_attribute('data-src') or "No src"
                            alt = element.get_attribute('alt') or "No alt"
                            self.log_auto_view(f"[{profile_id[:8]}] Clicking product image: {alt} ({src[:50]}...)")
                        else:
                            self.log_auto_view(f"[{profile_id[:8]}] Clicking {tag_name}: {element_text}")
                        
                        # Human-like click with slight mouse movement simulation
                        self.human_like_click(driver, element)
                        
                        # Wait after click (longer for product images)
                        if tag_name == 'img':
                            post_click_pause = random.uniform(2, 4)  # Longer pause for product images
                        else:
                            post_click_pause = random.uniform(1, 3)
                        
                        self.log_auto_view(f"[{profile_id[:8]}] Waiting {post_click_pause:.1f}s after click")
                        time.sleep(post_click_pause)
                        
                    except Exception as e:
                        self.log_auto_view(f"[{profile_id[:8]}] Click failed: {str(e)}")
                        continue
                        
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Random click error: {str(e)}")
    
    def human_like_click(self, driver, element):
        """Perform a human-like click with slight mouse movement simulation"""
        try:
            # Get element location and size
            location = element.location
            size = element.size
            
            # Calculate center point
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
            
            # Add slight randomness to click position (like human hand tremor)
            offset_x = random.randint(-3, 3)
            offset_y = random.randint(-3, 3)
            
            final_x = center_x + offset_x
            final_y = center_y + offset_y
            
            # Use ActionChains for more human-like interaction
            actions = ActionChains(driver)
            
            # Move to element with slight delay
            actions.move_to_element(element)
            actions.pause(random.uniform(0.1, 0.3))
            
            # Click with slight delay
            actions.click()
            actions.perform()
            
        except Exception as e:
            # Fallback to regular click if ActionChains fails
            element.click()
    
    def import_urls_from_file(self):
        """Import URLs from a text file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Text File with URLs",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Clear existing content
                self.url_text.delete("1.0", tk.END)
                
                # Insert new content
                self.url_text.insert("1.0", content)
                
                # Count URLs (excluding comments and empty lines)
                lines = content.split('\n')
                urls = []
                comments = 0
                empty_lines = 0
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('#'):
                        comments += 1
                    elif not line:
                        empty_lines += 1
                    else:
                        urls.append(line)
                
                # Show detailed import summary
                summary = f"Import Summary:\n"
                summary += f"• URLs: {len(urls)}\n"
                summary += f"• Comments: {comments}\n"
                summary += f"• Empty lines: {empty_lines}\n"
                summary += f"• Total lines: {len(lines)}"
                
                messagebox.showinfo("Import Successful", 
                                  f"Imported from: {file_path}\n\n{summary}")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import URLs: {str(e)}")
    
    def clear_urls(self):
        """Clear all URLs from the text area"""
        try:
            # Ask for confirmation
            if messagebox.askyesno("Clear URLs", "Are you sure you want to clear all URLs?"):
                self.url_text.delete("1.0", tk.END)
                messagebox.showinfo("Cleared", "All URLs have been cleared")
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear URLs: {str(e)}")
    
    def create_sample_urls_file(self):
        """Create a sample URLs file for users to test"""
        try:
            import os
            
            # Get desktop path
            desktop = os.path.expanduser("~/Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.expanduser("~")
            
            sample_file = os.path.join(desktop, "sample_urls.txt")
            
            sample_urls = """# Sample URLs file for Auto View Tool
# Add your URLs here, one per line
# Lines starting with # are comments and will be ignored

https://www.example.com
https://www.google.com
https://www.github.com
https://www.stackoverflow.com

# E-commerce examples
https://www.amazon.com
https://www.ebay.com
https://www.aliexpress.com

# Social media examples  
https://www.facebook.com
https://www.twitter.com
https://www.instagram.com

# You can add more URLs below
# Make sure each URL is on a separate line
"""
            
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write(sample_urls)
            
            messagebox.showinfo("Sample File Created", 
                              f"Sample URLs file created at:\n{sample_file}\n\nYou can now use this file to test the import functionality!")
            
        except Exception as e:
            messagebox.showerror("Sample File Error", f"Failed to create sample file: {str(e)}")
    
    def export_urls_to_file(self):
        """Export current URLs to a text file"""
        try:
            # Get current URLs
            urls_text = self.url_text.get("1.0", tk.END).strip()
            
            if not urls_text:
                messagebox.showwarning("No URLs", "There are no URLs to export")
                return
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                title="Save URLs to File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(urls_text)
                
                # Count exported URLs
                urls = [line.strip() for line in urls_text.split('\n') if line.strip() and not line.strip().startswith('#')]
                
                messagebox.showinfo("Export Successful", 
                                  f"Exported {len(urls)} URLs to:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export URLs: {str(e)}")
    
    def show_full_size_log(self):
        """Show Activity Log in full size popup window"""
        try:
            # Create popup window
            log_window = tk.Toplevel(self.root)
            log_window.title("Activity Log - Full Size")
            log_window.geometry("1000x700")
            log_window.resizable(True, True)
            
            # Make popup window modal
            log_window.transient(self.root)
            log_window.grab_set()
            
            # Center the popup window
            log_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
            
            # Create main frame
            main_frame = ttk.Frame(log_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Header with title and refresh button
            header_frame = ttk.Frame(main_frame)
            header_frame.pack(fill=tk.X, pady=(0, 10))
            
            title_label = ttk.Label(header_frame, text="Activity Log - Full Size", font=("Arial", 16, "bold"))
            title_label.pack(side=tk.LEFT)
            
            refresh_btn = ttk.Button(header_frame, text="🔄 Refresh", 
                                   command=lambda: self.refresh_full_log(log_text_widget))
            refresh_btn.pack(side=tk.RIGHT)
            
            # Log text widget with scrollbar
            log_text_widget = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, font=("Consolas", 10))
            log_text_widget.pack(fill=tk.BOTH, expand=True)
            
            # Copy current log content
            current_log = self.auto_view_log.get("1.0", tk.END)
            log_text_widget.insert("1.0", current_log)
            
            # Make text read-only
            log_text_widget.config(state=tk.DISABLED)
            
            # Apply theme
            try:
                log_window.configure(bg=self.current_theme['bg'])
                log_text_widget.configure(
                    bg=self.current_theme['text_bg'],
                    fg=self.current_theme['text_fg'],
                    insertbackground=self.current_theme['fg']
                )
            except Exception as e:
                print(f"Failed to apply theme to log window: {e}")
            
            # Auto-refresh every 2 seconds
            def auto_refresh():
                try:
                    if log_window.winfo_exists():
                        current_log = self.auto_view_log.get("1.0", tk.END)
                        log_text_widget.config(state=tk.NORMAL)
                        log_text_widget.delete("1.0", tk.END)
                        log_text_widget.insert("1.0", current_log)
                        log_text_widget.config(state=tk.DISABLED)
                        log_text_widget.see(tk.END)  # Scroll to bottom
                        log_window.after(2000, auto_refresh)
                except:
                    pass
            
            # Start auto-refresh
            log_window.after(2000, auto_refresh)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open full size log: {str(e)}")
    
    def refresh_full_log(self, log_text_widget):
        """Refresh the full size log window"""
        try:
            current_log = self.auto_view_log.get("1.0", tk.END)
            log_text_widget.config(state=tk.NORMAL)
            log_text_widget.delete("1.0", tk.END)
            log_text_widget.insert("1.0", current_log)
            log_text_widget.config(state=tk.DISABLED)
            log_text_widget.see(tk.END)
        except Exception as e:
            print(f"Error refreshing full log: {e}")
    
    def show_help(self):
        """Show help information and keyboard shortcuts"""
        help_text = """🔧 Auto View Tool - Help & Keyboard Shortcuts

🎨 Theme Management:
• Ctrl+T: Toggle between Light and Dark themes
• Theme preference is automatically saved

📁 URL Management:
• Ctrl+I: Import URLs from text file
• Ctrl+E: Export current URLs to file
• Ctrl+L: Clear all URLs
• 📝 Sample: Create sample URLs file for testing

🚀 Auto View Control:
• Ctrl+S: Start Auto View (when available)
• Ctrl+X: Stop Auto View (when running)
• Ctrl+P: Toggle profile sorting (default: sorted by name)

💡 Tips:
• URLs can be imported from .txt files
• Lines starting with # are treated as comments
• Empty lines are automatically ignored
• Theme changes are applied immediately
• All settings are preserved between sessions
• Profiles are automatically sorted by name (lowest to highest number)
• Use the 🔄 Reset button or Ctrl+P to toggle between sorted and default order
• Multiple profile selection opens in a popup window for better organization

🆘 For more help, check the documentation or contact support.
"""
        
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Help & Keyboard Shortcuts")
        help_window.geometry("600x500")
        help_window.resizable(True, True)
        
        # Make help window modal
        help_window.transient(self.root)
        help_window.grab_set()
        
        # Center the help window
        help_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Create text widget for help content
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, padx=20, pady=20)
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert help text
        help_text_widget.insert("1.0", help_text)
        help_text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Close button
        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(0, 10))
        
        # Apply theme to help window
        try:
            help_window.configure(bg=self.current_theme['bg'])
            help_text_widget.configure(
                bg=self.current_theme['text_bg'],
                fg=self.current_theme['text_fg'],
                insertbackground=self.current_theme['fg']
            )
            
            # Apply theme to close button
            style = ttk.Style()
            style.configure('TButton', 
                          background=self.current_theme['button_bg'],
                          foreground=self.current_theme['button_fg'])
            
        except Exception as e:
            print(f"Failed to apply theme to help window: {e}")
        
        # Handle help window close
        def on_help_close():
            help_window.destroy()
        
        help_window.protocol("WM_DELETE_WINDOW", on_help_close)
    
    def cleanup_profiles_after_auto_view(self, selected_profiles):
        """Cleanup profiles after auto view completion"""
        try:
            self.log_auto_view("Cleaning up profiles after auto view completion...")
            
            # Wait a bit for browsers to fully close
            time.sleep(2)
            
            # Note: Profiles will not be automatically refreshed
            # User should manually refresh using Refresh button when needed
            self.log_auto_view("Profile cleanup completed")
            self.log_auto_view("Note: Use Refresh button to update profile status when needed")
            
        except Exception as e:
            self.log_auto_view(f"Error during profile cleanup: {str(e)}")
    
    def stop_profile_for_cleanup(self, profile_id):
        """Stop a profile for cleanup purposes"""
        try:
            url = f"{self.api_base}/profile/stop/{profile_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.log_auto_view(f"Profile {profile_id[:8]} stopped for cleanup")
                return True
            else:
                self.log_auto_view(f"Failed to stop profile {profile_id[:8]} for cleanup. Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_auto_view(f"Error stopping profile {profile_id[:8]} for cleanup: {str(e)}")
            return False
    
    def on_profile_selection_change(self, event):
        """Handle profile selection change event"""
        try:
            selected_profile = self.profile_combo.get()
            if selected_profile:
                self.log_auto_view(f"Profile selection changed to: {selected_profile}")
                
                # Get current profile info
                profile_id, debug_port, status = self.get_selected_profile_info()
                
                if profile_id:
                    self.log_auto_view(f"Profile ID: {profile_id[:8]}, Status: {status}, Debug Port: {debug_port}")
                    
                    # If profile shows as "Started" but no debug port, it might be inconsistent
                    if status == 'Started' and not debug_port:
                        self.log_auto_view(f"Profile {profile_id[:8]} appears to be in inconsistent state")
                        self.log_auto_view(f"Please use Refresh button to update profile status")
                    
                    # If profile is "Available", we can use it
                    elif status == 'Available':
                        self.log_auto_view(f"Profile {profile_id[:8]} is available and ready to use")
                    
                    # If profile is "Started" with debug port, it's ready
                    elif status == 'Started' and debug_port:
                        self.log_auto_view(f"Profile {profile_id[:8]} is started and ready to use on port {debug_port}")
                    
                    else:
                        self.log_auto_view(f"Profile {profile_id[:8]} status: {status}, may need attention")
                else:
                    self.log_auto_view("Could not get profile info")
                    self.log_auto_view("Please use Refresh button to update profiles")
                    
        except Exception as e:
            self.log_auto_view(f"Error handling profile selection change: {str(e)}")
            self.log_auto_view("Please use Refresh button to update profiles")
    

    def on_random_time_change(self):
        """Handle change in random time interval checkbox"""
        if self.random_time_interval_var.get():
            # Show random time frame
            self.random_time_frame.grid()
            
            # Disable time per page spinbox since random time will be used
            if hasattr(self, 'time_per_page_spinbox'):
                self.time_per_page_spinbox.config(state='disabled')
            
            # Update max time if min time is greater
            min_total = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
            max_total = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
            if min_total >= max_total:
                # Set max time to min time + 10 seconds
                self.max_hours_var.set(self.min_hours_var.get())
                self.max_minutes_var.set(self.min_minutes_var.get())
                self.max_seconds_var.set(min(59, self.min_seconds_var.get() + 10))
            
            self.log_auto_view("Random time interval enabled - Time per page will be ignored")
        else:
            # Hide random time frame
            self.random_time_frame.grid_remove()
            
            # Enable time per page spinbox since fixed time will be used
            if hasattr(self, 'time_per_page_spinbox'):
                self.time_per_page_spinbox.config(state='normal')
            
            self.log_auto_view("Random time interval disabled - Using fixed time per page")
    
    def validate_time_range(self):
        """Validate the time range input and ensure min <= max"""
        try:
            # Convert hh:mm:ss to total seconds
            min_total_seconds = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
            max_total_seconds = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
            
            # Ensure min_time <= max_time
            if min_total_seconds > max_total_seconds:
                # Swap values if min > max
                self.min_hours_var.set(self.max_hours_var.get())
                self.min_minutes_var.set(self.max_minutes_var.get())
                self.min_seconds_var.set(self.max_seconds_var.get())
                self.max_hours_var.set(self.min_hours_var.get())
                self.max_minutes_var.set(self.min_minutes_var.get())
                self.max_seconds_var.set(self.min_seconds_var.get())
                self.log_auto_view(f"Adjusted time range: {self.max_hours_var.get():02d}:{self.max_minutes_var.get():02d}:{self.max_seconds_var.get():02d} - {self.min_hours_var.get():02d}:{self.min_minutes_var.get():02d}:{self.min_seconds_var.get():02d}")
            
            # Ensure reasonable bounds (minimum 10 seconds, maximum 24 hours)
            if min_total_seconds < 10:
                self.min_hours_var.set(0)
                self.min_minutes_var.set(0)
                self.min_seconds_var.set(10)
                self.log_auto_view("Minimum time adjusted to 00:00:10")
            
            if max_total_seconds > 86400:  # 24 hours = 24 * 60 * 60
                self.max_hours_var.set(23)
                self.max_minutes_var.set(59)
                self.max_seconds_var.set(59)
                self.log_auto_view("Maximum time adjusted to 23:59:59")
                
        except Exception as e:
            self.log_auto_view(f"Error validating time range: {str(e)}")
    
    def get_random_time_per_page(self):
        """Get random time per page if enabled, otherwise return fixed time"""
        if self.random_time_interval_var.get():
            # Convert hh:mm:ss to total seconds
            min_total_seconds = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
            max_total_seconds = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
            
            # Ensure min_time <= max_time
            if min_total_seconds > max_total_seconds:
                min_total_seconds, max_total_seconds = max_total_seconds, min_total_seconds
            
            random_seconds = random.randint(min_total_seconds, max_total_seconds)
            
            # Convert back to hh:mm:ss for display
            hours = random_seconds // 3600
            minutes = (random_seconds % 3600) // 60
            seconds = random_seconds % 60
            
            self.log_auto_view(f"Using RANDOM time: {hours:02d}:{minutes:02d}:{seconds:02d} (range: {self.min_hours_var.get():02d}:{self.min_minutes_var.get():02d}:{self.min_seconds_var.get():02d} - {self.max_hours_var.get():02d}:{self.max_minutes_var.get():02d}:{self.max_seconds_var.get():02d})")
            return random_seconds
        else:
            fixed_time = self.time_per_page_var.get()
            self.log_auto_view(f"Using FIXED time: {fixed_time} seconds")
            return fixed_time
    
    def on_search_enable_change(self):
        """Handle change in search enable checkbox"""
        if hasattr(self, 'amazon_enable_search_var') and self.amazon_enable_search_var.get():
            self.log_auto_view("Amazon keyword search enabled from Amazon Search tab")
        else:
            self.log_auto_view("Amazon keyword search disabled")
    
    def on_amazon_search_enable_change(self):
        """Handle change in Amazon search enable checkbox"""
        if self.amazon_enable_search_var.get():
            # Enable all Amazon search controls
            self.amazon_keywords_text.config(state='normal')
            self.amazon_import_keywords_btn.config(state='normal')
            self.amazon_clear_keywords_btn.config(state='normal')
            self.amazon_sample_keywords_btn.config(state='normal')
            self.amazon_status_label.config(text="Status: Amazon search enabled", foreground="green")
        else:
            # Disable Amazon search controls
            self.amazon_keywords_text.config(state='disabled')
            self.amazon_import_keywords_btn.config(state='disabled')
            self.amazon_clear_keywords_btn.config(state='disabled')
            self.amazon_sample_keywords_btn.config(state='disabled')
            self.amazon_status_label.config(text="Status: Amazon search disabled", foreground="red")
    
    def import_keywords_from_file(self):
        """Import keywords from a text file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Text File with Keywords",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                # Clear existing content
                self.keywords_text.delete("1.0", tk.END)
                
                # Insert new content
                self.keywords_text.insert("1.0", content)
                
                # Count keywords
                lines = content.split('\n')
                keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                
                messagebox.showinfo("Import Successful", 
                                  f"Imported {len(keywords)} keywords from: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import keywords: {str(e)}")
    
    def clear_keywords(self):
        """Clear all keywords from the text area"""
        try:
            if messagebox.askyesno("Clear Keywords", "Are you sure you want to clear all keywords?"):
                self.keywords_text.delete("1.0", tk.END)
                messagebox.showinfo("Cleared", "All keywords have been cleared")
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear keywords: {str(e)}")
    
    def import_amazon_keywords_from_file(self):
        """Import Amazon keywords from a text file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Select Text File with Amazon Keywords",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Clear existing content
                self.amazon_keywords_text.delete("1.0", tk.END)
                
                # Insert new content
                self.amazon_keywords_text.insert("1.0", content)
                
                # Count keywords
                lines = content.split('\n')
                keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                
                messagebox.showinfo("Import Successful", 
                                  f"Imported {len(keywords)} Amazon keywords from: {file_path}")
                
        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import Amazon keywords: {str(e)}")
    
    def clear_amazon_keywords(self):
        """Clear all Amazon keywords from the text area"""
        try:
            if messagebox.askyesno("Clear Amazon Keywords", "Are you sure you want to clear all Amazon keywords?"):
                self.amazon_keywords_text.delete("1.0", tk.END)
                messagebox.showinfo("Cleared", "All Amazon keywords have been cleared")
        except Exception as e:
            messagebox.showerror("Clear Error", f"Failed to clear Amazon keywords: {str(e)}")
    
    def create_sample_keywords(self):
        """Create sample Amazon keywords for users to test"""
        try:
            sample_keywords = """# Sample Amazon Keywords for Search
# Add your Amazon keywords here, one per line
# Lines starting with # are comments and will be ignored

laptop
smartphone
headphones
wireless earbuds
gaming mouse
mechanical keyboard
monitor
tablet
smartwatch
bluetooth speaker
webcam
microphone
gaming chair
desk lamp
phone case
"""
            
            # Clear existing content
            self.keywords_text.delete("1.0", tk.END)
            
            # Insert sample keywords
            self.keywords_text.insert("1.0", sample_keywords)
            
            messagebox.showinfo("Sample Keywords", "Sample keywords have been loaded!")
            
        except Exception as e:
            messagebox.showerror("Sample Error", f"Failed to create sample keywords: {str(e)}")
    
    def create_amazon_sample_keywords(self):
        """Create sample Amazon keywords for Amazon Search tab"""
        try:
            sample_keywords = """# Sample Amazon Keywords for Search
# Add your Amazon keywords here, one per line
# Lines starting with # are comments and will be ignored

laptop
smartphone
headphones
wireless earbuds
gaming mouse
mechanical keyboard
monitor
tablet
smartwatch
bluetooth speaker
webcam
microphone
gaming chair
desk lamp
phone case
"""
            
            # Clear existing content
            self.amazon_keywords_text.delete("1.0", tk.END)
            
            # Insert sample keywords
            self.amazon_keywords_text.insert("1.0", sample_keywords)
            
            messagebox.showinfo("Sample Amazon Keywords", "Sample Amazon keywords have been loaded!")
            
        except Exception as e:
            messagebox.showerror("Sample Error", f"Failed to create sample Amazon keywords: {str(e)}")
    
    def get_keywords_list(self):
        """Get list of keywords from text area - now redirects to Amazon Search tab"""
        try:
            # Redirect to Amazon Search tab keywords
            if hasattr(self, 'amazon_keywords_text'):
                content = self.amazon_keywords_text.get("1.0", tk.END).strip()
                if not content:
                    return []
                
                lines = content.split('\n')
                keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                return keywords
            else:
                return []
            
        except Exception as e:
            self.log_auto_view(f"Error getting keywords: {str(e)}")
            return []
    
    def get_enabled_search_engines(self):
        """Get list of enabled search engines"""
        try:
            enabled_engines = []
            for name, var in self.search_engines_vars.items():
                if var.get():
                    enabled_engines.append(name)
            return enabled_engines
            
        except Exception as e:
            self.log_auto_view(f"Error getting search engines: {str(e)}")
            return ["Google"]  # Default fallback
    
    def get_amazon_keywords_list(self):
        """Get list of Amazon keywords from Amazon Search tab"""
        try:
            content = self.amazon_keywords_text.get("1.0", tk.END).strip()
            if not content:
                return []
            
            lines = content.split('\n')
            keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            return keywords
            
        except Exception as e:
            self.amazon_status_label.config(text=f"Error getting keywords: {str(e)}", foreground="red")
            return []
    
    def test_amazon_search(self):
        """Test Amazon search functionality"""
        try:
            if not self.amazon_enable_search_var.get():
                messagebox.showwarning("Warning", "Please enable Amazon search first")
                return
            
            keywords = self.get_amazon_keywords_list()
            if not keywords:
                messagebox.showwarning("Warning", "Please add some Amazon keywords first")
                return
            
            # Select a random keyword for testing
            test_keyword = random.choice(keywords)
            self.amazon_status_label.config(text=f"Testing search for: {test_keyword}", foreground="orange")
            
            # Open Amazon in a new window for testing
            import webbrowser
            search_url = f"https://www.amazon.com/s?k={test_keyword}"
            webbrowser.open(search_url)
            
            self.amazon_status_label.config(text=f"Test search opened for: {test_keyword}", foreground="green")
            
        except Exception as e:
            self.amazon_status_label.config(text=f"Test error: {str(e)}", foreground="red")
            messagebox.showerror("Test Error", f"Failed to test Amazon search: {str(e)}")
    
    def human_like_typing(self, element, text, wpm=65):
        """Simulate human-like typing with specified WPM speed"""
        try:
            # Clear the element first
            element.clear()
            
            # Calculate delay per character based on WPM
            # Average word length is 5 characters, so WPM = characters per minute / 5
            # Therefore, characters per minute = WPM * 5
            # Delay per character = 60 seconds / (WPM * 5)
            delay_per_char = 60.0 / (wpm * 5)
            
            # Add some randomness to make it more human-like
            for char in text:
                if not self.is_auto_view_running():
                    break
                
                # Add the character
                element.send_keys(char)
                
                # Random delay variation (±20%)
                variation = random.uniform(0.8, 1.2)
                actual_delay = delay_per_char * variation
                
                # Add occasional longer pauses (like thinking)
                if random.random() < 0.05:  # 5% chance
                    actual_delay += random.uniform(0.1, 0.3)
                
                time.sleep(actual_delay)
                
        except Exception as e:
            # Fallback to regular typing if simulation fails
            element.clear()
            element.send_keys(text)
    
    def perform_keyword_search(self, driver, profile_id):
        """Perform Amazon keyword search with human-like typing simulation"""
        try:
            if not hasattr(self, 'amazon_enable_search_var') or not self.amazon_enable_search_var.get():
                return
            
            # Get available keywords (excluding used ones)
            all_keywords = self.get_amazon_keywords_list()
            available_keywords = [k for k in all_keywords if k not in self.used_keywords]
            
            if not available_keywords:
                self.log_auto_view(f"[{profile_id[:8]}] No more unused keywords available, continuing with URLs")
                return
            
            # Select random unused keyword
            keyword = random.choice(available_keywords)
            
            # Mark keyword as used
            self.used_keywords.add(keyword)
            self.log_auto_view(f"[{profile_id[:8]}] Selected keyword: '{keyword}' (used keywords: {len(self.used_keywords)}/{len(all_keywords)})")
            
            # Navigate to Amazon homepage with retry mechanism
            self.log_auto_view(f"[{profile_id[:8]}] Going to Amazon homepage like a real shopper")
            if not self.navigate_with_retry(driver, "https://www.amazon.com", profile_id, "Amazon homepage"):
                self.log_auto_view(f"[{profile_id[:8]}] Failed to load Amazon homepage after retries, skipping keyword search")
                return
            time.sleep(random.uniform(2, 4))
            
            # Find search box with retry mechanism
            search_box = self.find_element_with_retry(driver, By.ID, "twotabsearchtextbox", profile_id, "search box")
            if not search_box:
                self.log_auto_view(f"[{profile_id[:8]}] Search box not found after retries, using direct URL")
                # Fallback to direct URL
                search_url = f"https://www.amazon.com/s?k={keyword}"
                if not self.navigate_with_retry(driver, search_url, profile_id, "Amazon search results"):
                    self.log_auto_view(f"[{profile_id[:8]}] Failed to load search results, skipping keyword search")
                    return
                time.sleep(random.uniform(2, 4))
                self.scroll_search_results(driver, profile_id)
                if self.select_random_product(driver, profile_id):
                    self.load_product_page_with_default_time(driver, profile_id)
                return
            
            if search_box.is_displayed() and search_box.is_enabled():
                self.log_auto_view(f"[{profile_id[:8]}] Found search box, typing '{keyword}' with human-like speed")
                
                # Click on search box first (like real user)
                search_box.click()
                time.sleep(random.uniform(0.5, 1.0))
                
                # Get typing speed from Amazon Search tab
                typing_speed = getattr(self, 'typing_speed_var', tk.IntVar(value=65)).get()
                
                # Simulate human-like typing (like real shopper)
                self.human_like_typing(search_box, keyword, typing_speed)
                
                # Wait a bit after typing (like human thinking)
                time.sleep(random.uniform(0.5, 1.5))
                
                # Find and click search button with retry
                search_button = self.find_element_with_retry(driver, By.ID, "nav-search-submit-button", profile_id, "search button")
                if search_button and search_button.is_displayed() and search_button.is_enabled():
                    search_button.click()
                    self.log_auto_view(f"[{profile_id[:8]}] Clicked search button")
                    
                    # Wait for search results
                    time.sleep(random.uniform(3, 5))
                    
                    # Scroll and interact with search results for 4-5 seconds
                    self.log_auto_view(f"[{profile_id[:8]}] Scrolling search results for 4-5 seconds...")
                    self.scroll_search_results(driver, profile_id)
                    
                    # Select and click on a random product
                    self.log_auto_view(f"[{profile_id[:8]}] Selecting random product...")
                    if self.select_random_product(driver, profile_id):
                        # Load product page with default time settings
                        self.log_auto_view(f"[{profile_id[:8]}] Loading product page with default time settings...")
                        self.load_product_page_with_default_time(driver, profile_id)
                    else:
                        self.log_auto_view(f"[{profile_id[:8]}] No product selected, continuing...")
                else:
                    self.log_auto_view(f"[{profile_id[:8]}] Search button not found, using direct URL")
                    # Fallback to direct URL
                    search_url = f"https://www.amazon.com/s?k={keyword}"
                    if not self.navigate_with_retry(driver, search_url, profile_id, "Amazon search results"):
                        self.log_auto_view(f"[{profile_id[:8]}] Failed to load search results, skipping keyword search")
                        return
                    time.sleep(random.uniform(2, 4))
                    self.scroll_search_results(driver, profile_id)
                    if self.select_random_product(driver, profile_id):
                        self.load_product_page_with_default_time(driver, profile_id)
            else:
                self.log_auto_view(f"[{profile_id[:8]}] Search box not accessible, using direct URL")
                # Fallback to direct URL
                search_url = f"https://www.amazon.com/s?k={keyword}"
                if not self.navigate_with_retry(driver, search_url, profile_id, "Amazon search results"):
                    self.log_auto_view(f"[{profile_id[:8]}] Failed to load search results, skipping keyword search")
                    return
                time.sleep(random.uniform(2, 4))
                self.scroll_search_results(driver, profile_id)
                if self.select_random_product(driver, profile_id):
                    self.load_product_page_with_default_time(driver, profile_id)
            
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error during Amazon keyword search: {str(e)}")
    
    def scroll_search_results(self, driver, profile_id):
        """Scroll through Amazon search results for 4-5 seconds"""
        try:
            start_time = time.time()
            scroll_duration = random.uniform(4, 5)
            
            self.log_auto_view(f"[{profile_id[:8]}] Starting scroll for {scroll_duration:.1f} seconds...")
            
            while time.time() - start_time < scroll_duration:
                if not self.is_auto_view_running():
                    break
                
                # Random scroll amount
                scroll_amount = random.randint(200, 600)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
                # Random pause between scrolls
                pause = random.uniform(0.3, 0.8)
                time.sleep(pause)
                
                # Occasionally scroll back up a bit
                if random.random() < 0.2:
                    driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                    time.sleep(random.uniform(0.2, 0.5))
            
            self.log_auto_view(f"[{profile_id[:8]}] Finished scrolling search results")
            
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error scrolling search results: {str(e)}")
    
    def select_random_product(self, driver, profile_id):
        """Select and click on a random product from search results"""
        try:
            # Look for Amazon product links
            product_selectors = [
                "a[href*='/dp/']",
                "a[href*='/gp/product/']",
                ".s-result-item h2 a",
                "[data-component-type='s-search-result'] h2 a"
            ]
            
            selected_product = None
            for selector in product_selectors:
                try:
                    products = driver.find_elements(By.CSS_SELECTOR, selector)
                    if products:
                        # Filter visible and clickable products
                        clickable_products = [p for p in products if p.is_displayed() and p.is_enabled()]
                        if clickable_products:
                            # Select random product (avoid first few)
                            start_idx = min(2, len(clickable_products) // 3)
                            end_idx = min(len(clickable_products), start_idx + 6)
                            
                            if end_idx > start_idx:
                                selected_product = random.choice(clickable_products[start_idx:end_idx])
                                break
                except Exception as e:
                    continue
            
            if selected_product:
                # Get product info
                try:
                    product_title = selected_product.get_attribute('title') or selected_product.text[:50]
                except:
                    product_title = "Product"
                
                self.log_auto_view(f"[{profile_id[:8]}] Selected product: {product_title}")
                
                # Scroll to product
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_product)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Click on product
                selected_product.click()
                self.log_auto_view(f"[{profile_id[:8]}] Clicked on product")
                
                # Wait for product page to load
                time.sleep(random.uniform(2, 4))
                return True
            else:
                self.log_auto_view(f"[{profile_id[:8]}] No clickable products found")
                return False
                
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error selecting product: {str(e)}")
            return False
    
    def load_product_page_with_default_time(self, driver, profile_id):
        """Load product page using default time settings from Auto View tab"""
        try:
            # Get time settings from Auto View tab
            if hasattr(self, 'random_time_interval_var') and self.random_time_interval_var.get():
                # Use random time interval
                min_total = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
                max_total = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
                time_to_spend = random.randint(min_total, max_total)
                self.log_auto_view(f"[{profile_id[:8]}] Using RANDOM time: {time_to_spend} seconds")
            else:
                # Use fixed time
                time_to_spend = self.time_per_page_var.get()
                self.log_auto_view(f"[{profile_id[:8]}] Using FIXED time: {time_to_spend} seconds")
            
            # Auto scroll on product page
            self.log_auto_view(f"[{profile_id[:8]}] Auto scrolling product page for {time_to_spend} seconds...")
            self.auto_scroll_page_with_driver(driver, profile_id)
            
            # Random clicks if enabled
            if hasattr(self, 'random_clicks_var') and self.random_clicks_var.get():
                self.log_auto_view(f"[{profile_id[:8]}] Performing random clicks on product page...")
                self.random_click_elements_with_driver(driver, profile_id)
            
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error loading product page: {str(e)}")
    
    def simulate_amazon_search_behavior(self, driver, profile_id):
        """Simulate human-like Amazon search behavior"""
        try:
            # Random scroll on Amazon search results
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            if page_height > viewport_height:
                # Scroll down a bit to view results
                scroll_amount = random.randint(200, 500)
                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(1, 2))
                
                # Sometimes scroll back up
                if random.random() < 0.3:
                    driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                    time.sleep(random.uniform(0.5, 1))
            
            # Occasionally click on a product (15% chance)
            if random.random() < 0.15:
                try:
                    # Look for Amazon product links
                    product_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/dp/'], a[href*='/gp/product/']")
                    
                    if product_links:
                        # Select a random product (avoid first few)
                        start_idx = min(2, len(product_links) // 3)
                        end_idx = min(len(product_links), start_idx + 4)
                        
                        if end_idx > start_idx:
                            selected_product = random.choice(product_links[start_idx:end_idx])
                            
                            if selected_product.is_displayed() and selected_product.is_enabled():
                                # Get product title if available
                                try:
                                    product_title = selected_product.get_attribute('title') or selected_product.text[:50]
                                except:
                                    product_title = "Product"
                                
                                self.log_auto_view(f"[{profile_id[:8]}] Clicking Amazon product: {product_title}...")
                                
                                # Scroll to product
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_product)
                                time.sleep(random.uniform(0.5, 1))
                                
                                # Click product
                                selected_product.click()
                                
                                # Wait on product page
                                time.sleep(random.uniform(2, 4))
                                
                                # Go back to search results
                                driver.back()
                                time.sleep(random.uniform(1, 2))
                                
                except Exception as e:
                    self.log_auto_view(f"[{profile_id[:8]}] Error clicking Amazon product: {str(e)}")
                    
        except Exception as e:
            self.log_auto_view(f"[{profile_id[:8]}] Error simulating Amazon search behavior: {str(e)}")
    
    def perform_keyword_search_fallback(self):
        """Perform Amazon keyword search for fallback Chrome with human-like typing"""
        try:
            if not hasattr(self, 'amazon_enable_search_var') or not self.amazon_enable_search_var.get():
                return
            
            # Get available keywords (excluding used ones)
            all_keywords = self.get_amazon_keywords_list()
            available_keywords = [k for k in all_keywords if k not in self.used_keywords]
            
            if not available_keywords:
                self.log_auto_view("No more unused keywords available, continuing with URLs")
                return
            
            # Select random unused keyword
            keyword = random.choice(available_keywords)
            
            # Mark keyword as used
            self.used_keywords.add(keyword)
            self.log_auto_view(f"Selected keyword: '{keyword}' (used keywords: {len(self.used_keywords)}/{len(all_keywords)})")
            
            # Navigate to Amazon homepage with retry mechanism
            self.log_auto_view("Going to Amazon homepage like a real shopper")
            if not self.navigate_with_retry_fallback("https://www.amazon.com", "Amazon homepage"):
                self.log_auto_view("Failed to load Amazon homepage after retries, skipping keyword search")
                return
            time.sleep(random.uniform(2, 4))
            
            # Find search box with retry mechanism
            search_box = self.find_element_with_retry_fallback(By.ID, "twotabsearchtextbox", "search box")
            if not search_box:
                self.log_auto_view("Search box not found after retries, using direct URL")
                # Fallback to direct URL
                search_url = f"https://www.amazon.com/s?k={keyword}"
                if not self.navigate_with_retry_fallback(search_url, "Amazon search results"):
                    self.log_auto_view("Failed to load search results, skipping keyword search")
                    return
                time.sleep(random.uniform(2, 4))
                self.scroll_search_results_fallback()
                if self.select_random_product_fallback():
                    self.load_product_page_with_default_time_fallback()
                return
            
            if search_box.is_displayed() and search_box.is_enabled():
                self.log_auto_view(f"Found search box, typing '{keyword}' with human-like speed")
                
                # Click on search box first
                search_box.click()
                time.sleep(random.uniform(0.5, 1.0))
                
                # Get typing speed from Amazon Search tab if available
                typing_speed = getattr(self, 'typing_speed_var', tk.IntVar(value=65)).get()
                
                # Simulate human-like typing
                self.human_like_typing(search_box, keyword, typing_speed)
                
                # Wait a bit after typing (like human thinking)
                time.sleep(random.uniform(0.5, 1.5))
                
                # Find and click search button with retry
                search_button = self.find_element_with_retry_fallback(By.ID, "nav-search-submit-button", "search button")
                if search_button and search_button.is_displayed() and search_button.is_enabled():
                    search_button.click()
                    self.log_auto_view("Clicked search button")
                    
                    # Wait for search results
                    time.sleep(random.uniform(3, 5))
                    
                    # Scroll and interact with search results for 4-5 seconds
                    self.log_auto_view("Scrolling search results for 4-5 seconds...")
                    self.scroll_search_results_fallback()
                    
                    # Select and click on a random product
                    self.log_auto_view("Selecting random product...")
                    if self.select_random_product_fallback():
                        # Load product page with default time settings
                        self.log_auto_view("Loading product page with default time settings...")
                        self.load_product_page_with_default_time_fallback()
                    else:
                        self.log_auto_view("No product selected, continuing...")
                else:
                    self.log_auto_view("Search button not found, using direct URL")
                    # Fallback to direct URL
                    search_url = f"https://www.amazon.com/s?k={keyword}"
                    if not self.navigate_with_retry_fallback(search_url, "Amazon search results"):
                        self.log_auto_view("Failed to load search results, skipping keyword search")
                        return
                    time.sleep(random.uniform(2, 4))
                    self.scroll_search_results_fallback()
                    if self.select_random_product_fallback():
                        self.load_product_page_with_default_time_fallback()
            else:
                self.log_auto_view("Search box not accessible, using direct URL")
                # Fallback to direct URL
                search_url = f"https://www.amazon.com/s?k={keyword}"
                if not self.navigate_with_retry_fallback(search_url, "Amazon search results"):
                    self.log_auto_view("Failed to load search results, skipping keyword search")
                    return
                time.sleep(random.uniform(2, 4))
                self.scroll_search_results_fallback()
                if self.select_random_product_fallback():
                    self.load_product_page_with_default_time_fallback()
            
        except Exception as e:
            self.log_auto_view(f"Error during Amazon keyword search: {str(e)}")
    
    def scroll_search_results_fallback(self):
        """Scroll through Amazon search results for 4-5 seconds (fallback)"""
        try:
            start_time = time.time()
            scroll_duration = random.uniform(4, 5)
            
            self.log_auto_view(f"Starting scroll for {scroll_duration:.1f} seconds...")
            
            while time.time() - start_time < scroll_duration:
                if not self.is_auto_view_running():
                    break
                
                # Random scroll amount
                scroll_amount = random.randint(200, 600)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                
                # Random pause between scrolls
                pause = random.uniform(0.3, 0.8)
                time.sleep(pause)
                
                # Occasionally scroll back up a bit
                if random.random() < 0.2:
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                    time.sleep(random.uniform(0.2, 0.5))
            
            self.log_auto_view(f"Finished scrolling search results")
            
        except Exception as e:
            self.log_auto_view(f"Error scrolling search results: {str(e)}")
    
    def select_random_product_fallback(self):
        """Select and click on a random product from search results (fallback)"""
        try:
            # Look for Amazon product links
            product_selectors = [
                "a[href*='/dp/']",
                "a[href*='/gp/product/']",
                ".s-result-item h2 a",
                "[data-component-type='s-search-result'] h2 a"
            ]
            
            selected_product = None
            for selector in product_selectors:
                try:
                    products = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if products:
                        # Filter visible and clickable products
                        clickable_products = [p for p in products if p.is_displayed() and p.is_enabled()]
                        if clickable_products:
                            # Select random product (avoid first few)
                            start_idx = min(2, len(clickable_products) // 3)
                            end_idx = min(len(clickable_products), start_idx + 6)
                            
                            if end_idx > start_idx:
                                selected_product = random.choice(clickable_products[start_idx:end_idx])
                                break
                except Exception as e:
                    continue
            
            if selected_product:
                # Get product info
                try:
                    product_title = selected_product.get_attribute('title') or selected_product.text[:50]
                except:
                    product_title = "Product"
                
                self.log_auto_view(f"Selected product: {product_title}")
                
                # Scroll to product
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_product)
                time.sleep(random.uniform(0.5, 1.0))
                
                # Click on product
                selected_product.click()
                self.log_auto_view(f"Clicked on product")
                
                # Wait for product page to load
                time.sleep(random.uniform(2, 4))
                return True
            else:
                self.log_auto_view(f"No clickable products found")
                return False
                
        except Exception as e:
            self.log_auto_view(f"Error selecting product: {str(e)}")
            return False
    
    def load_product_page_with_default_time_fallback(self):
        """Load product page using default time settings from Auto View tab (fallback)"""
        try:
            # Get time settings from Auto View tab
            if hasattr(self, 'random_time_interval_var') and self.random_time_interval_var.get():
                # Use random time interval
                min_total = self.min_hours_var.get() * 3600 + self.min_minutes_var.get() * 60 + self.min_seconds_var.get()
                max_total = self.max_hours_var.get() * 3600 + self.max_minutes_var.get() * 60 + self.max_seconds_var.get()
                time_to_spend = random.randint(min_total, max_total)
                self.log_auto_view(f"Using RANDOM time: {time_to_spend} seconds")
            else:
                # Use fixed time
                time_to_spend = self.time_per_page_var.get()
                self.log_auto_view(f"Using FIXED time: {time_to_spend} seconds")
            
            # Auto scroll on product page
            self.log_auto_view(f"Auto scrolling product page for {time_to_spend} seconds...")
            self.auto_scroll_page()
            
            # Random clicks if enabled
            if hasattr(self, 'random_clicks_var') and self.random_clicks_var.get():
                self.log_auto_view(f"Performing random clicks on product page...")
                self.random_click_elements()
            
        except Exception as e:
            self.log_auto_view(f"Error loading product page: {str(e)}")
    
    def simulate_amazon_search_behavior_fallback(self):
        """Simulate human-like Amazon search behavior for fallback Chrome"""
        try:
            # Random scroll on Amazon search results
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            if page_height > viewport_height:
                # Scroll down a bit to view results
                scroll_amount = random.randint(200, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(1, 2))
                
                # Sometimes scroll back up
                if random.random() < 0.3:
                    self.driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                    time.sleep(random.uniform(0.5, 1))
            
            # Occasionally click on a product (15% chance)
            if random.random() < 0.15:
                try:
                    # Look for Amazon product links
                    product_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/dp/'], a[href*='/gp/product/']")
                    
                    if product_links:
                        # Select a random product (avoid first few)
                        start_idx = min(2, len(product_links) // 3)
                        end_idx = min(len(product_links), start_idx + 4)
                        
                        if end_idx > start_idx:
                            selected_product = random.choice(product_links[start_idx:end_idx])
                            
                            if selected_product.is_displayed() and selected_product.is_enabled():
                                # Get product title if available
                                try:
                                    product_title = selected_product.get_attribute('title') or selected_product.text[:50]
                                except:
                                    product_title = "Product"
                                
                                self.log_auto_view(f"Clicking Amazon product: {product_title}...")
                                
                                # Scroll to product
                                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selected_product)
                                time.sleep(random.uniform(0.5, 1))
                                
                                # Click product
                                selected_product.click()
                                
                                # Wait on product page
                                time.sleep(random.uniform(2, 4))
                                
                                # Go back to search results
                                self.driver.back()
                                time.sleep(random.uniform(1, 2))
                                
                except Exception as e:
                    self.log_auto_view(f"Error clicking Amazon product: {str(e)}")
                    
        except Exception as e:
            self.log_auto_view(f"Error simulating Amazon search behavior: {str(e)}")

    def navigate_with_retry(self, driver, url, profile_id, page_name):
        """Navigate to URL with retry mechanism for undetectable browser"""
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                if not self.is_auto_view_running():
                    self.log_auto_view(f"[{profile_id[:8]}] Auto view stopped, skipping navigation to {page_name}")
                    return False
                
                self.log_auto_view(f"[{profile_id[:8]}] Attempt {attempt + 1}/{max_retries}: Navigating to {page_name}")
                driver.get(url)
                
                # Wait for page to load
                time.sleep(random.uniform(2, 4))
                
                # Check if page loaded successfully
                try:
                    # Simple check: if we can get page title, page is loaded
                    title = driver.title
                    if title and title.strip():
                        self.log_auto_view(f"[{profile_id[:8]}] Successfully loaded {page_name}: {title[:50]}...")
                        return True
                except Exception as e:
                    self.log_auto_view(f"[{profile_id[:8]}] Page load check failed: {str(e)}")
                
                # If we reach here, page might not be fully loaded
                if attempt < max_retries - 1:
                    self.log_auto_view(f"[{profile_id[:8]}] Page {page_name} may not be fully loaded, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10s
                else:
                    self.log_auto_view(f"[{profile_id[:8]}] Failed to load {page_name} after {max_retries} attempts")
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_auto_view(f"[{profile_id[:8]}] Navigation error (attempt {attempt + 1}): {str(e)}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)
                else:
                    self.log_auto_view(f"[{profile_id[:8]}] Failed to navigate to {page_name} after {max_retries} attempts: {str(e)}")
                    return False
        
        return False
    
    def find_element_with_retry(self, driver, by, selector, profile_id, element_name):
        """Find element with retry mechanism for undetectable browser"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                if not self.is_auto_view_running():
                    self.log_auto_view(f"[{profile_id[:8]}] Auto view stopped, skipping element search for {element_name}")
                    return None
                
                self.log_auto_view(f"[{profile_id[:8]}] Attempt {attempt + 1}/{max_retries}: Finding {element_name}")
                element = driver.find_element(by, selector)
                
                if element and element.is_displayed():
                    self.log_auto_view(f"[{profile_id[:8]}] Successfully found {element_name}")
                    return element
                else:
                    if attempt < max_retries - 1:
                        self.log_auto_view(f"[{profile_id[:8]}] {element_name} found but not visible, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.2, 8)
                    else:
                        self.log_auto_view(f"[{profile_id[:8]}] {element_name} not visible after {max_retries} attempts")
                        return None
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_auto_view(f"[{profile_id[:8]}] Element search error (attempt {attempt + 1}): {str(e)}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.2, 8)
                else:
                    self.log_auto_view(f"[{profile_id[:8]}] Failed to find {element_name} after {max_retries} attempts: {str(e)}")
                    return None
        
        return None
    
    def navigate_with_retry_fallback(self, url, page_name):
        """Navigate to URL with retry mechanism for fallback Chrome"""
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                if not self.is_auto_view_running():
                    self.log_auto_view(f"Auto view stopped, skipping navigation to {page_name}")
                    return False
                
                self.log_auto_view(f"Attempt {attempt + 1}/{max_retries}: Navigating to {page_name}")
                self.driver.get(url)
                
                # Wait for page to load
                time.sleep(random.uniform(2, 4))
                
                # Check if page loaded successfully
                try:
                    # Simple check: if we can get page title, page is loaded
                    title = self.driver.title
                    if title and title.strip():
                        self.log_auto_view(f"Successfully loaded {page_name}: {title[:50]}...")
                        return True
                except Exception as e:
                    self.log_auto_view(f"Page load check failed: {str(e)}")
                
                # If we reach here, page might not be fully loaded
                if attempt < max_retries - 1:
                    self.log_auto_view(f"Page {page_name} may not be fully loaded, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10s
                else:
                    self.log_auto_view(f"Failed to load {page_name} after {max_retries} attempts")
                    return False
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_auto_view(f"Navigation error (attempt {attempt + 1}): {str(e)}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.5, 10)
                else:
                    self.log_auto_view(f"Failed to navigate to {page_name} after {max_retries} attempts: {str(e)}")
                    return False
        
        return False
    
    def find_element_with_retry_fallback(self, by, selector, element_name):
        """Find element with retry mechanism for fallback Chrome"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                if not self.is_auto_view_running():
                    self.log_auto_view(f"Auto view stopped, skipping element search for {element_name}")
                    return None
                
                self.log_auto_view(f"Attempt {attempt + 1}/{max_retries}: Finding {element_name}")
                element = self.driver.find_element(by, selector)
                
                if element and element.is_displayed():
                    self.log_auto_view(f"Successfully found {element_name}")
                    return element
                else:
                    if attempt < max_retries - 1:
                        self.log_auto_view(f"{element_name} found but not visible, retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 1.2, 8)
                    else:
                        self.log_auto_view(f"{element_name} not visible after {max_retries} attempts")
                        return None
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    self.log_auto_view(f"Element search error (attempt {attempt + 1}): {str(e)}, retrying in {retry_delay}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 1.2, 8)
                else:
                    self.log_auto_view(f"Failed to find {element_name} after {max_retries} attempts: {str(e)}")
                    return None
        
        return None
    
    def show_browser_completion_popup(self, profile_id):
        """Show popup notification when individual browser completes"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("Browser Completed")
            popup.geometry("400x200")
            popup.resizable(False, False)
            
            # Make popup modal and center it
            popup.transient(self.root)
            popup.grab_set()
            popup.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
            
            # Configure popup style
            popup.configure(bg=self.current_theme['bg'])
            
            # Main frame
            main_frame = ttk.Frame(popup, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Success icon and message
            icon_label = ttk.Label(main_frame, text="✅", font=("Arial", 48))
            icon_label.pack(pady=(0, 10))
            
            title_label = ttk.Label(main_frame, text="Browser Hoàn Thành!", font=("Arial", 16, "bold"))
            title_label.pack(pady=(0, 5))
            
            message_label = ttk.Label(main_frame, text=f"Browser '{profile_id}' đã xong", font=("Arial", 12))
            message_label.pack(pady=(0, 20))
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Đóng", command=popup.destroy)
            close_btn.pack()
            
            # Auto-close after 5 seconds
            popup.after(5000, popup.destroy)
            
            # Apply theme
            try:
                popup.configure(bg=self.current_theme['bg'])
                main_frame.configure(style='TFrame')
            except Exception as e:
                print(f"Failed to apply theme to browser completion popup: {e}")
                
        except Exception as e:
            print(f"Error showing browser completion popup: {e}")
    
    def show_tools_completion_popup(self, browser_count):
        """Show popup notification when all tools complete"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("Tools Completed")
            popup.geometry("500x250")
            popup.resizable(False, False)
            
            # Make popup modal and center it
            popup.transient(self.root)
            popup.grab_set()
            popup.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
            
            # Configure popup style
            popup.configure(bg=self.current_theme['bg'])
            
            # Main frame
            main_frame = ttk.Frame(popup, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Success icon and message
            icon_label = ttk.Label(main_frame, text="🎉", font=("Arial", 48))
            icon_label.pack(pady=(0, 10))
            
            title_label = ttk.Label(main_frame, text="Đã Hoàn Tất!", font=("Arial", 18, "bold"))
            title_label.pack(pady=(0, 5))
            
            if browser_count > 1:
                message_label = ttk.Label(main_frame, text=f"Tất cả {browser_count} browsers đã hoàn thành", font=("Arial", 12))
            else:
                message_label = ttk.Label(main_frame, text="Chrome browser đã hoàn thành", font=("Arial", 12))
            message_label.pack(pady=(0, 10))
            
            status_label = ttk.Label(main_frame, text="Auto View Tools đã hoàn tất thành công!", font=("Arial", 12, "bold"), foreground="green")
            status_label.pack(pady=(0, 20))
            
            # Close button
            close_btn = ttk.Button(main_frame, text="Đóng", command=popup.destroy)
            close_btn.pack()
            
            # Auto-close after 8 seconds
            popup.after(8000, popup.destroy)
            
            # Apply theme
            try:
                popup.configure(bg=self.current_theme['bg'])
                main_frame.configure(style='TFrame')
            except Exception as e:
                print(f"Failed to apply theme to tools completion popup: {e}")
                
        except Exception as e:
            print(f"Error showing tools completion popup: {e}")

def main():
    root = tk.Tk()
    app = BrowserProfileManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
