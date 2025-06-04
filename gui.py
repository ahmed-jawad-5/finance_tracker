import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import calendar as cal
import os
import time
import shutil
from db import DatabaseHandler


import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict


DARK_BG_COLOR = "#1a1a1a"            # Slightly softer than pure black
DARK_TEXT_COLOR = "#FFD700"           # Your signature gold text
DARK_ENTRY_BG = "#2d2d2d"            # Dark gray input fields
DARK_ENTRY_FG = "#FFD700"             # Gold text in inputs to match theme
DARK_BUTTON_BG = "#333333"           # Charcoal buttons (neutral base)
DARK_BUTTON_FG = "#FFD700"            # Gold text on buttons

# Light theme (blue-cohesive)  
LIGHT_BG_COLOR = "#f5f9ff"             # Very light blue background  
LIGHT_TEXT_COLOR = "#1a365d"           # Deep navy for text (matches button)  
LIGHT_ENTRY_BG = "#ffffff"             # Clean white fields  
LIGHT_ENTRY_FG = "#2c5282"            # Medium blue-gray text (softer than navy)  
LIGHT_ENTRY_BORDER = "#bee3f8"        # Light blue border for inputs  
LIGHT_BUTTON_BG = "#3182ce"           # Primary blue button  
LIGHT_BUTTON_FG = "#ffffff"           # White text  
LIGHT_ALT_BUTTON_BG = "#ebf8ff"        # Pale blue secondary button  

# Initialize with dark theme
BG_COLOR = LIGHT_BG_COLOR
TEXT_COLOR = LIGHT_TEXT_COLOR
ENTRY_BG = LIGHT_ENTRY_BG
ENTRY_FG = LIGHT_ENTRY_FG
BUTTON_BG = LIGHT_BUTTON_BG
BUTTON_FG = LIGHT_BUTTON_FG

class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Tracker")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.dark_theme = tk.BooleanVar(value=True)  # Start with dark theme
        self.set_theme()
        self.db = DatabaseHandler()
        self.create_widgets()
        self.load_transactions()
        self.root.after(1000, self.check_alerts)        
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.theme_button = ttk.Button(self.root, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.place(relx=0.95, rely=0.02, anchor="ne")
        
        self.add_frame = ttk.Frame(self.notebook)
        self.view_frame = ttk.Frame(self.notebook)
        self.budget_frame = ttk.Frame(self.notebook)
        self.calendar_frame = ttk.Frame(self.notebook)  # New calendar frame


        self.add_frame.configure(style="TFrame")
        self.view_frame.configure(style="TFrame")
        self.budget_frame.configure(style="TFrame")
        self.calendar_frame.configure(style="TFrame")  # Configure calendar frame

        self.notebook.add(self.view_frame, text="View Transactions")
        self.notebook.add(self.add_frame, text="Add Transaction")
        self.notebook.add(self.budget_frame, text="Budgets")
        self.notebook.add(self.calendar_frame, text="Calendar")  # Add calendar tab

        self.setup_add_transaction_tab()
        self.setup_view_transactions_tab()
        self.setup_budget_tab()
        self.setup_calendar_tab()  # Set up calendar UI
    
        self.analysis_frame = ttk.Frame(self.notebook)
        self.analysis_frame.configure(style="TFrame")
        self.notebook.add(self.analysis_frame, text="Analysis")
        self.setup_analysis_tab()

    def toggle_theme(self):
        # Toggle the theme value
        self.dark_theme.set(not self.dark_theme.get())
        self.set_theme()

        # Update tree colors for income/expense tags
        if hasattr(self, 'tree'):
            if self.dark_theme.get():
                self.tree.tag_configure('income', foreground='lightgreen')
                self.tree.tag_configure('expense', foreground='salmon')
            else:
                self.tree.tag_configure('income', foreground='green')
                self.tree.tag_configure('expense', foreground='red')

        # Update calendar tree tag colors
        if hasattr(self, 'calendar_tree'):
            if self.dark_theme.get():
                self.calendar_tree.tag_configure('income', foreground='lightgreen')
                self.calendar_tree.tag_configure('expense', foreground='salmon')
            else:
                self.calendar_tree.tag_configure('income', foreground='green')
                self.calendar_tree.tag_configure('expense', foreground='red')

        # Update calendar day colors if calendar exists
        if hasattr(self, 'calendar_buttons'):
            self.update_calendar_display()

        # Refresh the analysis tab if it's present
        if hasattr(self, 'setup_analysis_tab'):
            self.setup_analysis_tab()

    

    def setup_add_transaction_tab(self):
        # Custom fonts for a premium look
        heading_font = ("Segoe UI", 11, "bold")
        label_font = ("Segoe UI", 10)
        button_font = ("Segoe UI", 10)
        
        # Configure ttk styles for a premium look
        self.style = ttk.Style()
        self.style.configure("TLabel", font=label_font)
        self.style.configure("TButton", font=button_font)
        self.style.configure("TEntry", font=label_font)
        self.style.configure("TCombobox", font=label_font)
        self.style.configure("TRadiobutton", font=label_font)
        
        # Custom style for section frames
        self.style.configure("Section.TLabelframe", font=heading_font)
        self.style.configure("Section.TLabelframe.Label", font=heading_font)
        
        # Custom style for the primary action button
        self.style.configure("Primary.TButton", font=(button_font[0], button_font[1], "bold"))
        
        # Main container frame with two columns and proper padding
        main_frame = ttk.Frame(self.add_frame, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure the main frame to have two equal columns
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Left side - Transaction Information with premium styling
        left_frame = ttk.LabelFrame(main_frame, text="Transaction Information", style="Section.TLabelframe")
        left_frame.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")
        
        # Right side - Receipt Management with premium styling
        right_frame = ttk.LabelFrame(main_frame, text="Receipt Management", style="Section.TLabelframe")
        right_frame.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")
        
        # Configure both frames for proper spacing
        for frame in [left_frame, right_frame]:
            frame.columnconfigure(0, weight=0, minsize=120)  # Wider label column
            frame.columnconfigure(1, weight=1)
            for i in range(6):
                frame.rowconfigure(i, weight=0, minsize=60)  # Taller rows for more space
        
        # ===== LEFT SIDE: TRANSACTION INFORMATION =====
        
        # Date input with calendar popup - increased spacing and font size
        date_label = ttk.Label(left_frame, text="Date:", anchor="w")
        date_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        date_frame = ttk.Frame(left_frame)
        date_frame.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        
        self.date_entry = ttk.Entry(date_frame, width=15, font=label_font)
        self.date_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        
        # Calendar button with better icon and spacing
        self.cal_button = ttk.Button(date_frame, text="📅", width=4, 
                                command=self.show_calendar)
        self.cal_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Description input - increased spacing and font size
        desc_label = ttk.Label(left_frame, text="Description:", anchor="w")
        desc_label.grid(row=1, column=0, padx=15, pady=15, sticky="w")
        
        self.desc_entry = ttk.Entry(left_frame, font=label_font)
        self.desc_entry.grid(row=1, column=1, padx=15, pady=15, sticky="ew")
        
        # Amount input - increased spacing and font size
        amount_label = ttk.Label(left_frame, text="Amount:", anchor="w")
        amount_label.grid(row=2, column=0, padx=15, pady=15, sticky="w")
        
        self.amount_entry = ttk.Entry(left_frame, font=label_font)
        self.amount_entry.grid(row=2, column=1, padx=15, pady=15, sticky="ew")
        
        # Category dropdown - increased spacing and font size
        category_label = ttk.Label(left_frame, text="Category:", anchor="w")
        category_label.grid(row=3, column=0, padx=15, pady=15, sticky="w")
        
        self.category_entry = ttk.Combobox(left_frame, font=label_font)
        self.category_entry['values'] = [""] + self.db.get_categories()
        self.category_entry.grid(row=3, column=1, padx=15, pady=15, sticky="ew")
        
        # Transaction type radio buttons - increased spacing and better layout
        type_label = ttk.Label(left_frame, text="Type:", anchor="w")
        type_label.grid(row=4, column=0, padx=15, pady=15, sticky="w")
        
        type_frame = ttk.Frame(left_frame)
        type_frame.grid(row=4, column=1, padx=15, pady=15, sticky="w")
        
        self.type_var = tk.StringVar(value="expense")
        expense_rb = ttk.Radiobutton(type_frame, text="Expense", variable=self.type_var, value="expense")
        expense_rb.pack(side=tk.LEFT, padx=(0, 40))  # More space between options
        income_rb = ttk.Radiobutton(type_frame, text="Income", variable=self.type_var, value="income")
        income_rb.pack(side=tk.LEFT)
        
        # ===== RIGHT SIDE: RECEIPT MANAGEMENT =====
        
        # Receipt path display - increased spacing and font size
        path_label = ttk.Label(right_frame, text="File Path:", anchor="w")
        path_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        self.receipt_path_var = tk.StringVar()
        self.receipt_path_entry = ttk.Entry(right_frame, textvariable=self.receipt_path_var, state="readonly", font=label_font)
        self.receipt_path_entry.grid(row=0, column=1, padx=15, pady=15, sticky="ew")
        
        # Receipt action buttons with better spacing and styling
        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=15, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # Custom button styles for receipt buttons
        self.style.configure("Action.TButton", font=button_font)
        
        self.upload_btn = ttk.Button(button_frame, text="Upload Receipt", width=15, 
                                command=self.upload_receipt, style="Action.TButton")
        self.upload_btn.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.view_btn = ttk.Button(button_frame, text="View Receipt", width=15, 
                            command=self.view_receipt, state="disabled", style="Action.TButton")
        self.view_btn.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Receipt", width=15, 
                            command=self.clear_receipt, style="Action.TButton")
        self.clear_btn.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Receipt preview area (larger) with better styling
        preview_frame = ttk.LabelFrame(right_frame, text="Receipt Preview", style="Section.TLabelframe")
        preview_frame.grid(row=2, column=0, columnspan=2, rowspan=3, padx=15, pady=15, sticky="nsew")
        right_frame.rowconfigure(2, weight=1)  # Make the preview expandable
        
        # Canvas for image display (better than label for images)
        preview_canvas_frame = ttk.Frame(preview_frame)
        preview_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.receipt_canvas = tk.Canvas(preview_canvas_frame, bg="white", 
                                    highlightthickness=1, highlightbackground="#cccccc")
        self.receipt_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add a label on the canvas for the "no image" text
        self.receipt_canvas.create_text(
            self.receipt_canvas.winfo_reqwidth() // 2,
            self.receipt_canvas.winfo_reqheight() // 2,
            text="No receipt image uploaded",
            font=("Segoe UI", 11),
            fill="#999999"
        )
        
        # ===== BOTTOM SECTION: ADD TRANSACTION BUTTON =====
        
        # Add transaction button at the bottom with premium styling
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=1, column=0, columnspan=2, pady=20)
        
        self.add_transaction_btn = ttk.Button(
            action_frame, 
            text="Add Transaction", 
            command=self.add_transaction,
            style="Primary.TButton",
            width=25
        )
        
        # Apply custom styling to make the button more prominent
        self.style.configure("Primary.TButton", 
                        font=("Segoe UI", 11, "bold"),
                        padding=(20, 12))
        
        self.add_transaction_btn.pack(pady=10)

    def show_calendar(self):
        """
        Enhanced calendar implementation with premium visuals
        """
        import calendar
        from datetime import datetime
        
        # Custom styles for calendar
        cal_font = ("Segoe UI", 10)
        cal_header_font = ("Segoe UI", 11, "bold")
        
        # Variables needed for the calendar
        self.cal_top = tk.Toplevel(self.add_frame)
        self.cal_top.title("Select Date")
        self.cal_top.geometry("340x360")  # Larger size for premium feel
        self.cal_top.transient(self.add_frame.winfo_toplevel())
        self.cal_top.grab_set()
        
        # Make the dialog modal and position it near the date entry
        x = self.date_entry.winfo_rootx()
        y = self.date_entry.winfo_rooty() + self.date_entry.winfo_height()
        self.cal_top.geometry(f"+{x}+{y}")
        
        # Get current date from entry or use today
        try:
            current_date = datetime.strptime(self.date_entry.get(), '%Y-%m-%d')
        except ValueError:
            current_date = datetime.today()
        
        self.cal_year = current_date.year
        self.cal_month = current_date.month
        self.cal_day = current_date.day
        
        # Main frame for calendar with padding
        cal_frame = ttk.Frame(self.cal_top, padding=15)
        cal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Month navigation frame with premium styling
        nav_frame = ttk.Frame(cal_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Previous month button - using a nicer symbol and styling
        prev_btn = ttk.Button(nav_frame, text="◀", width=4, command=self.prev_month)
        prev_btn.pack(side=tk.LEFT)
        
        # Month and year label - more prominent with larger font
        self.month_label = ttk.Label(nav_frame, text=f"{calendar.month_name[self.cal_month]} {self.cal_year}", 
                                font=cal_header_font)
        self.month_label.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Next month button - using a nicer symbol and styling
        next_btn = ttk.Button(nav_frame, text="▶", width=4, command=self.next_month)
        next_btn.pack(side=tk.RIGHT)
        
        # Days header with premium styling
        days_frame = ttk.Frame(cal_frame)
        days_frame.pack(fill=tk.X, pady=(0, 10))
        
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for i, day in enumerate(days):
            day_label = ttk.Label(days_frame, text=day, width=4, anchor="center", font=cal_font)
            if i == 0 or i == 6:  # Weekend styling
                day_label.configure(foreground="#D04A02")  # weekend days in red/orange
            day_label.grid(row=0, column=i, padx=3)
        
        # Calendar days frame with better spacing
        self.days_frame = ttk.Frame(cal_frame)
        self.days_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create custom styles for calendar buttons
        self.style = ttk.Style()
        
        # Normal day button - larger with better padding
        self.style.configure("Calendar.TButton", 
                        padding=8,
                        font=cal_font)
        
        # Today's date style
        self.style.configure("CalendarToday.TButton", 
                        padding=8,
                        background="#4C8BF5",  # Google blue
                        foreground="white",
                        font=cal_font)
        
        # Selected date style
        self.style.configure("CalendarSelected.TButton", 
                        padding=8,
                        background="#0F9D58",  # Google green
                        foreground="white",
                        font=cal_font)
        
        # Weekend style
        self.style.configure("CalendarWeekend.TButton", 
                        padding=8,
                        foreground="#D04A02",  # Orange/red for weekends
                        font=cal_font)
        
        # Draw the calendar
        self.draw_calendar()
        
        # Bottom buttons frame with premium spacing
        button_frame = ttk.Frame(self.cal_top)
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Today button (jumps to today) with premium styling
        today_btn = ttk.Button(
            button_frame, 
            text="Today", 
            command=self.go_to_today,
            width=12,
            style="Calendar.TButton"
        )
        today_btn.pack(side=tk.LEFT, padx=(0, 8))
        
        # OK button with premium styling
        ok_btn = ttk.Button(
            button_frame, 
            text="Select", 
            command=self.close_calendar,
            width=12,
            style="Primary.TButton"
        )
        ok_btn.pack(side=tk.RIGHT)

    def draw_calendar(self):
        """Draw the calendar for the current month/year with premium visuals"""
        import calendar
        from datetime import datetime
        
        # Clear any existing day buttons
        for widget in self.days_frame.winfo_children():
            widget.destroy()
        
        # Get the calendar for current month/year
        cal = calendar.monthcalendar(self.cal_year, self.cal_month)
        
        # Update the month/year label
        self.month_label.config(text=f"{calendar.month_name[self.cal_month]} {self.cal_year}")
        
        # Get today's date for highlighting
        today = datetime.today().date()
        
        # Create day buttons with proper styling
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    # Empty day (not part of this month)
                    empty_frame = ttk.Frame(self.days_frame, width=40, height=40)  # Larger for premium feel
                    empty_frame.grid(row=week_idx, column=day_idx, padx=3, pady=3)
                    # This makes the empty cells maintain the same size as buttons
                    empty_frame.grid_propagate(False)
                else:
                    # Determine button style based on conditions
                    btn_style = "Calendar.TButton"
                    
                    # Check if it's today
                    is_today = (today.year == self.cal_year and 
                            today.month == self.cal_month and 
                            today.day == day)
                    
                    # Check if it's the selected date
                    is_selected = (self.cal_day == day)
                    
                    # Check if it's a weekend
                    is_weekend = (day_idx == 0 or day_idx == 6)
                    
                    # Apply appropriate style
                    if is_selected:
                        btn_style = "CalendarSelected.TButton"
                    elif is_today:
                        btn_style = "CalendarToday.TButton"
                    elif is_weekend:
                        btn_style = "CalendarWeekend.TButton"
                    
                    # Create button with consistent size and premium padding
                    btn = ttk.Button(
                        self.days_frame, 
                        text=str(day), 
                        width=4,  # Wider for premium feel
                        style=btn_style,
                        command=lambda d=day: self.select_date(d)
                    )
                    
                    btn.grid(row=week_idx, column=day_idx, padx=3, pady=3)

    def prev_month(self):
        """Go to previous month"""
        self.cal_month -= 1
        if self.cal_month < 1:
            self.cal_month = 12
            self.cal_year -= 1
        self.draw_calendar()

    def next_month(self):
        """Go to next month"""
        self.cal_month += 1
        if self.cal_month > 12:
            self.cal_month = 1
            self.cal_year += 1
        self.draw_calendar()

    def go_to_today(self):
        """Jump to today's date"""
        today = datetime.today()
        self.cal_year = today.year
        self.cal_month = today.month
        self.cal_day = today.day
        self.draw_calendar()

    def select_date(self, day):
        """Select a date and update the calendar display"""
        # Update the selected day
        self.cal_day = day
        
        # Refresh the calendar to show the selection
        self.draw_calendar()
        
        # Update the entry field
        date_str = f"{self.cal_year}-{self.cal_month:02d}-{day:02d}"
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, date_str)

    def close_calendar(self):
        """Close the calendar popup"""
        if hasattr(self, 'cal_top') and self.cal_top:
            self.cal_top.destroy()

    # Additional methods for receipt handling

    def upload_receipt(self):
        """Upload and display a receipt image with premium presentation"""
        from PIL import Image, ImageTk
        import os
        
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff")]
        )
        
        if file_path:
            # Store the path
            self.receipt_path_var.set(file_path)
            
            try:
                # Load and resize the image for preview
                image = Image.open(file_path)
                
                # Calculate the best size to fit in the preview area while maintaining aspect ratio
                canvas_width = self.receipt_canvas.winfo_width()
                canvas_height = self.receipt_canvas.winfo_height()
                
                # If canvas hasn't been rendered yet, use estimated size
                if canvas_width <= 1:
                    canvas_width = 400
                if canvas_height <= 1:
                    canvas_height = 300
                
                # Calculate scale factor
                img_width, img_height = image.size
                width_ratio = canvas_width / img_width
                height_ratio = canvas_height / img_height
                scale_factor = min(width_ratio, height_ratio) * 0.9  # 90% of available space
                
                # Resize image
                new_width = int(img_width * scale_factor)
                new_height = int(img_height * scale_factor)
                resized_image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(resized_image)
                
                # Store reference to prevent garbage collection
                self.receipt_photo = photo
                
                # Clear canvas and display image
                self.receipt_canvas.delete("all")
                self.receipt_canvas.create_image(
                    canvas_width // 2, 
                    canvas_height // 2, 
                    image=photo,
                    anchor="center"
                )
                
                # Enable the view button
                self.view_btn.config(state="normal")
                
            except Exception as e:
                # Show error message with professional styling
                self.receipt_canvas.delete("all")
                self.receipt_canvas.create_text(
                    self.receipt_canvas.winfo_reqwidth() // 2,
                    self.receipt_canvas.winfo_reqheight() // 2,
                    text=f"Error loading image:\n{str(e)}",
                    font=("Segoe UI", 10),
                    fill="#D04A02",
                    justify="center"
                )

    def view_receipt(self):
        """Open the receipt image in the system's default image viewer"""
        import os
        import platform
        import subprocess
        
        file_path = self.receipt_path_var.get()
        
        if file_path and os.path.exists(file_path):
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', file_path))
            else:  # Linux variants
                subprocess.call(('xdg-open', file_path))

    def clear_receipt(self):
        """Clear the receipt image and reset the interface"""
        self.receipt_path_var.set("")
        self.view_btn.config(state="disabled")
        
        # Clear canvas and display default message
        self.receipt_canvas.delete("all")
        self.receipt_canvas.create_text(
            self.receipt_canvas.winfo_reqwidth() // 2,
            self.receipt_canvas.winfo_reqheight() // 2,
            text="No receipt image uploaded",
            font=("Segoe UI", 11),
            fill="#999999"
        )

    def add_transaction(self):
        """Add transaction with enhanced validation and feedback"""
        # Get values from form
        date_str = self.date_entry.get()
        description = self.desc_entry.get()
        amount_str = self.amount_entry.get()
        category = self.category_entry.get()
        trans_type = self.type_var.get()
        receipt_path = self.receipt_path_var.get()
        
        # Validate inputs with premium error messages
        errors = []
        
        # Date validation
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            errors.append("• Date must be in YYYY-MM-DD format")
        
        # Amount validation
        try:
            amount = float(amount_str)
            if amount <= 0:
                errors.append("• Amount must be greater than zero")
        except ValueError:
            errors.append("• Amount must be a valid number")
        
        # Description validation
        if not description:
            errors.append("• Description cannot be empty")
        
        # Display errors if any
        if errors:
            error_message = "Please correct the following errors:\n\n" + "\n".join(errors)
            messagebox.showerror("Validation Error", error_message)
            return
        
        # Process the transaction (implementation depends on your database structure)
        try:
            # Code to add transaction to database would go here
            
            # Show success message
            messagebox.showinfo("Success", "Transaction added successfully!")
            
            # Clear form fields
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

    def clear_form(self):
        """Clear all form fields"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.set("")
        self.type_var.set("expense")
        self.clear_receipt()
    def upload_receipt(self):
        # Open file dialog to select an image
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=filetypes
        )
        
        if filepath:
            # Store the path
            self.receipt_path_var.set(filepath)
            
            # Enable the view button
            self.view_btn.config(state="normal")
            
            # Show thumbnail preview
            self.display_receipt_thumbnail(filepath)

    def view_receipt(self):
        filepath = self.receipt_path_var.get()
        if filepath and os.path.exists(filepath):
            # Open the image with the default image viewer
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == 'Windows':
                    os.startfile(filepath)
                elif system == 'Darwin':  # macOS
                    subprocess.call(['open', filepath])
                else:  # Linux and other Unix-like
                    subprocess.call(['xdg-open', filepath])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the image: {str(e)}")
        else:
            messagebox.showinfo("Info", "No valid receipt image to display")

    def clear_receipt(self):
    # Clear the path
        self.receipt_path_var.set("")

        # Disable the view button if available
        if hasattr(self, 'view_btn'):
            self.view_btn.config(state="disabled")

        # Clear preview using receipt_canvas (only if it exists)
        if hasattr(self, 'receipt_canvas'):
            self.receipt_canvas.delete("all")
            self.receipt_canvas.create_text(
                self.receipt_canvas.winfo_reqwidth() // 2,
                self.receipt_canvas.winfo_reqheight() // 2,
                text="No receipt image uploaded",
                font=("Segoe UI", 11),
                fill="#999999"
            )



    def display_receipt_thumbnail(self, filepath):
        try:
            from PIL import Image, ImageTk

            # Open image and resize for thumbnail
            image = Image.open(filepath)

            # Calculate new dimensions to fit in the preview area (max 300x200)
            max_width, max_height = 300, 200
            width, height = image.size

            # Calculate aspect ratio
            aspect_ratio = width / height

            if width > max_width:
                width = max_width
                height = int(width / aspect_ratio)

            if height > max_height:
                height = max_height
                width = int(height * aspect_ratio)

            # Resize and convert image for display
            image = image.resize((width, height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            # Store reference to prevent garbage collection
            self.thumbnail_image = photo

            # Display in canvas instead of non-existent label
            if hasattr(self, 'receipt_canvas'):
                self.receipt_canvas.delete("all")
                self.receipt_canvas.create_image(
                    self.receipt_canvas.winfo_width() // 2,
                    self.receipt_canvas.winfo_height() // 2,
                    image=photo,
                    anchor="center"
                )

        except Exception as e:
            if hasattr(self, 'receipt_canvas'):
                self.receipt_canvas.delete("all")
                self.receipt_canvas.create_text(
                    self.receipt_canvas.winfo_reqwidth() // 2,
                    self.receipt_canvas.winfo_reqheight() // 2,
                    text=f"Could not load preview:\n{str(e)}",
                    font=("Segoe UI", 10),
                    fill="#D04A02",
                    justify="center"
                )

    def calendar_view_transaction(self, event):
        selected_item = self.calendar_tree.selection()
        if not selected_item:
            return
        
        # Get the date and description from the selected item
        values = self.calendar_tree.item(selected_item[0])['values']
        date_str = values[0]  # Date column
        description = values[1]  # Description column
        
        # Find the transaction ID by querying the database
        transaction_id = self.db.get_transaction_id_by_date_desc(date_str, description)
        
        if transaction_id:
            # Now get the full transaction details including receipt
            transaction = self.db.get_transaction(transaction_id)
            if transaction:
                # Create a view/edit window similar to edit_transaction
                self.show_transaction_details(transaction)
        else:
            messagebox.showinfo("Info", "Could not find transaction details")

# Show transaction details with receipt (used from calendar view)
    def show_transaction_details(self, transaction):
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title("Transaction Details")
        details_window.configure(bg=BG_COLOR)
        details_window.geometry("500x500")
        details_window.resizable(False, False)
        
        # Make the window modal
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Extract transaction details
        id, date, description, amount, category, ttype, receipt_path = transaction
        
        # Create form with transaction details
        ttk.Label(details_window, text="Date:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(details_window, text=date.strftime('%Y-%m-%d')).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(details_window, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(details_window, text=description).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(details_window, text="Amount:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(details_window, text=f"${float(amount):.2f}").grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(details_window, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(details_window, text=category or "").grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(details_window, text="Type:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(details_window, text=ttype.capitalize()).grid(row=4, column=1, padx=10, pady=10, sticky="w")
        
        # Receipt display section
        receipt_frame = ttk.LabelFrame(details_window, text="Receipt Image")
        receipt_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        # Variable to store photo reference
        details_window.thumbnail_image = None
        
        # Show receipt preview or placeholder
        if receipt_path and os.path.exists(receipt_path):
            try:
                # Import PIL for image handling
                from PIL import Image, ImageTk
                
                # Open and resize image for preview
                image = Image.open(receipt_path)
                
                # Calculate dimensions for the preview
                max_width, max_height = 400, 250
                width, height = image.size
                
                # Maintain aspect ratio
                aspect_ratio = width / height
                
                if width > max_width:
                    width = max_width
                    height = int(width / aspect_ratio)
                    
                if height > max_height:
                    height = max_height
                    width = int(height * aspect_ratio)
                    
                # Resize and convert for display
                image = image.resize((width, height), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                
                # Store reference to prevent garbage collection
                details_window.thumbnail_image = photo
                
                # Display in label
                receipt_preview = ttk.Label(receipt_frame, image=photo)
                receipt_preview.pack(pady=10)
                
                # Add View button
                ttk.Button(receipt_frame, text="View Full Image", 
                        command=lambda: self.view_receipt_from_path(receipt_path)).pack(pady=5)
                        
            except Exception as e:
                receipt_preview = ttk.Label(receipt_frame, text=f"Error loading image: {str(e)}")
                receipt_preview.pack(pady=20)
        else:
            receipt_preview = ttk.Label(receipt_frame, text="No receipt image available")
            receipt_preview.pack(pady=20)
        
        # Button frame
        button_frame = ttk.Frame(details_window)
        button_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=10)
        
        # Close button
        ttk.Button(button_frame, text="Close", command=details_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Edit button to open the actual edit transaction window
        ttk.Button(button_frame, text="Edit Transaction", 
                command=lambda: self.edit_transaction_by_id(id, details_window)).pack(side=tk.LEFT, padx=5)
        
        # Center the window on the screen
        details_window.update_idletasks()
        width = details_window.winfo_width()
        height = details_window.winfo_height()
        x = (details_window.winfo_screenwidth() // 2) - (width // 2)
        y = (details_window.winfo_screenheight() // 2) - (height // 2)
        details_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # Edit transaction by ID (used from calendar view)
    def edit_transaction_by_id(self, transaction_id, parent_window=None):
        transaction = self.db.get_transaction(transaction_id)
        
        if not transaction:
            messagebox.showerror("Error", "Could not retrieve transaction details")
            return
        
        # Close parent window if provided
        if parent_window:
            parent_window.destroy()
        
        # Create a "fake" event to pass to edit_transaction
        class FakeEvent:
            def __init__(self):
                pass
        
        # Set the tree selection to the transaction with this ID
        for item in self.tree.get_children():
            if self.tree.item(item)['values'][0] == transaction_id:
                self.tree.selection_set(item)
                self.edit_transaction(FakeEvent())
                return
        
        # If not found in the tree, directly edit using modified edit_transaction logic
        self.edit_transaction(FakeEvent())

    # Calendar tab setup
    def setup_calendar_tab(self):
        # Existing calendar setup code...
        self.calendar_controls_frame = ttk.Frame(self.calendar_frame)
        self.calendar_controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Month and year navigation
        self.prev_month_btn = ttk.Button(self.calendar_controls_frame, text="←", width=3, command=self.prev_month)
        self.prev_month_btn.pack(side=tk.LEFT, padx=5)
        
        self.month_year_label = ttk.Label(self.calendar_controls_frame, text="", font=("Arial", 12, "bold"))
        self.month_year_label.pack(side=tk.LEFT, padx=10)
        
        self.next_month_btn = ttk.Button(self.calendar_controls_frame, text="→", width=3, command=self.next_month)
        self.next_month_btn.pack(side=tk.LEFT, padx=5)
        
        # "Today" button
        self.today_btn = ttk.Button(self.calendar_controls_frame, text="Today", command=self.go_to_today)
        self.today_btn.pack(side=tk.RIGHT, padx=10)
        
        # Calendar grid frame
        self.calendar_grid_frame = ttk.Frame(self.calendar_frame)
        self.calendar_grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Transactions display frame
        self.transactions_frame = ttk.LabelFrame(self.calendar_frame, text="Transactions")
        self.transactions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for transactions
        columns = ('date', 'description', 'amount', 'category', 'type')
        self.calendar_tree = ttk.Treeview(self.transactions_frame, columns=columns, show='headings')
        
        for col in columns:
            self.calendar_tree.heading(col, text=col.capitalize())
        self.calendar_tree.column('date', width=100, anchor=tk.CENTER)
        self.calendar_tree.column('amount', width=100, anchor=tk.E)
        
        scrollbar = ttk.Scrollbar(self.transactions_frame, orient=tk.VERTICAL, command=self.calendar_tree.yview)
        self.calendar_tree.configure(yscroll=scrollbar.set)
        self.calendar_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize calendar
        self.selected_date = datetime.now()
        self.calendar_buttons = []
        self.create_calendar()
        
        # Configure tag colors for the calendar tree
        if self.dark_theme.get():
            self.calendar_tree.tag_configure('income', foreground='lightgreen')
            self.calendar_tree.tag_configure('expense', foreground='salmon')
        else:
            self.calendar_tree.tag_configure('income', foreground='green')
            self.calendar_tree.tag_configure('expense', foreground='red')
        
        # Bind double-click to view/edit transaction
        self.calendar_tree.bind("<Double-1>", self.calendar_view_transaction)

    def create_calendar(self):
        # Set the month-year label
        self.month_year_label.config(text=f"{self.selected_date.strftime('%B %Y')}")
        
        # Clear previous calendar buttons if they exist
        for widget in self.calendar_grid_frame.winfo_children():
            widget.destroy()
        
        # Create day labels (Monday-Sunday)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            lbl = ttk.Label(self.calendar_grid_frame, text=day, anchor="center")
            lbl.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            
        # Get the calendar data for the selected month
        year = self.selected_date.year
        month = self.selected_date.month
        cal_month = cal.monthcalendar(year, month)
        
        # Get transaction data for indicators
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')
        
        transactions_by_day = self.db.get_transactions_by_day(start_date, end_date)
        
        # Create calendar buttons
        self.calendar_buttons = []
        for week_idx, week in enumerate(cal_month):
            for day_idx, day in enumerate(week):
                if day == 0:
                    # Empty cell for days not in this month
                    empty_frame = ttk.Frame(self.calendar_grid_frame)
                    empty_frame.grid(row=week_idx + 1, column=day_idx, sticky="nsew", padx=1, pady=1)
                else:
                    # Day button with frame to hold transaction indicators
                    day_frame = ttk.Frame(self.calendar_grid_frame)
                    day_frame.grid(row=week_idx + 1, column=day_idx, sticky="nsew", padx=1, pady=1)
                    
                    btn = ttk.Button(day_frame, text=str(day), 
                                     command=lambda d=day: self.show_day_transactions(d))
                    btn.pack(fill=tk.BOTH, expand=True)
                    
                    self.calendar_buttons.append((day, btn))
                    
                    # Add indicators if there are transactions on this day
                    date_str = f"{year}-{month:02d}-{day:02d}"
                    if date_str in transactions_by_day:
                        indicator_frame = ttk.Frame(day_frame)
                        indicator_frame.pack(fill=tk.X)
                        
                        # Check if there are incomes and expenses
                        has_income = any(t[5] == 'income' for t in transactions_by_day[date_str])
                        has_expense = any(t[5] == 'expense' for t in transactions_by_day[date_str])
                        
                        if has_income:
                            income_ind = ttk.Label(indicator_frame, text="↑", foreground="green", font=("Arial", 8))
                            income_ind.pack(side=tk.LEFT, padx=1)
                        
                        if has_expense:
                            expense_ind = ttk.Label(indicator_frame, text="↓", foreground="red", font=("Arial", 8))
                            expense_ind.pack(side=tk.LEFT, padx=1)
                        
                        # Add total amount indicator
                        total = sum(float(t[3]) for t in transactions_by_day[date_str])
                        amount_label = ttk.Label(indicator_frame, 
                                               text=f"${abs(total):.1f}", 
                                               foreground="green" if total >= 0 else "red",
                                               font=("Arial", 7))
                        amount_label.pack(side=tk.RIGHT, padx=1)
        
        # Configure grid to expand properly
        for i in range(7):  # 7 columns for days of the week
            self.calendar_grid_frame.columnconfigure(i, weight=1, uniform="calendar")
        for i in range(7):  # Up to 6 rows for weeks + 1 for day headers
            self.calendar_grid_frame.rowconfigure(i, weight=1, uniform="calendar")
        
        # Highlight today if it's in the current month view
        if self.selected_date.year == datetime.now().year and self.selected_date.month == datetime.now().month:
            today = datetime.now().day
            for day, btn in self.calendar_buttons:
                if day == today:
                    btn.configure(style="Today.TButton")
                    break
    
    def show_day_transactions(self, day):
        # Clear the tree
        for item in self.calendar_tree.get_children():
            self.calendar_tree.delete(item)
        
        # Format the date for the selected day
        selected_date = datetime(self.selected_date.year, self.selected_date.month, day)
        date_str = selected_date.strftime('%Y-%m-%d')
        
        # Get transactions for this date
        transactions = self.db.get_transactions(date_str, date_str)
        
        # Update the transactions list frame title
        self.transactions_frame.configure(text=f"Transactions for {selected_date.strftime('%B %d, %Y')}")
        
        # Add transactions to the tree
        for t in transactions:
            # Modify this line to handle the additional receipt_path field
            id, date, description, amount, category, ttype, receipt_path = t  # Now expecting 7 values
            
            # Format the date and amount
            formatted_date = date.strftime('%Y-%m-%d')
            formatted_amount = f"${float(amount):.2f}"
            
            # Insert into treeview with tag based on transaction type
            tag = 'income' if ttype == 'income' else 'expense'
            self.calendar_tree.insert('', tk.END, values=(
                formatted_date, description, formatted_amount, 
                category or "", ttype.capitalize()
            ), tags=(tag,))
    
    def prev_month(self):
        # Go to previous month
        year, month = self.selected_date.year, self.selected_date.month
        if month == 1:
            self.selected_date = datetime(year - 1, 12, 1)
        else:
            self.selected_date = datetime(year, month - 1, 1)
        self.create_calendar()
        
        # Clear the transactions view
        for item in self.calendar_tree.get_children():
            self.calendar_tree.delete(item)
        self.transactions_frame.configure(text="Transactions")
    
    def next_month(self):
        # Go to next month
        year, month = self.selected_date.year, self.selected_date.month
        if month == 12:
            self.selected_date = datetime(year + 1, 1, 1)
        else:
            self.selected_date = datetime(year, month + 1, 1)
        self.create_calendar()
        
        # Clear the transactions view
        for item in self.calendar_tree.get_children():
            self.calendar_tree.delete(item)
        self.transactions_frame.configure(text="Transactions")
    
    def go_to_today(self):
        # Go to current month and highlight today
        self.selected_date = datetime.now()
        self.create_calendar()
        
        # Show today's transactions
        self.show_day_transactions(self.selected_date.day)
    
    def update_calendar_display(self):
        # Re-create the calendar with updated theme
        if hasattr(self, 'selected_date'):
            self.create_calendar()

    def setup_view_transactions_tab(self):
        # Create a single scrollable frame for all elements
        self.scrollable_frame = ttk.Frame(self.view_frame)
        self.scrollable_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a vertical scrollbar
        self.main_canvas = tk.Canvas(self.scrollable_frame)
        self.main_scrollbar = ttk.Scrollbar(self.scrollable_frame, orient="vertical", command=self.main_canvas.yview)
        self.main_scrollable_content = ttk.Frame(self.main_canvas)
        
        # Configure the canvas
        self.main_scrollable_content.bind(
            "<Configure>",
            lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        )
        
        # Create a window inside the canvas that contains the scrollable content
        self.main_frame = self.main_canvas.create_window((0, 0), window=self.main_scrollable_content, anchor="nw")
        
        # Configure canvas to expand with window
        self.main_canvas.bind("<Configure>", self.on_main_canvas_configure)
        
        # Pack the canvas and scrollbar
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.main_scrollbar.pack(side="right", fill="y")
        
        # Connect scrollbar to canvas
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Add mousewheel scrolling
        self.main_canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # Add a welcome banner at the top
        welcome_frame = ttk.Frame(self.main_scrollable_content)
        welcome_frame.pack(fill=tk.X, padx=10, pady=(15, 5))
        
        welcome_font = ('Helvetica', 16, 'bold')
        welcome_label = ttk.Label(welcome_frame, text="Welcome to Your Financial Dashboard", font=welcome_font)
        welcome_label.pack(anchor=tk.CENTER, pady=5)
        
        # Current date display
        import datetime
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        date_label = ttk.Label(welcome_frame, text=f"Today: {current_date}", font=('Helvetica', 10))
        date_label.pack(anchor=tk.CENTER)
        
        # Move summary frame to the top and enhance its visibility
        summary_frame = ttk.LabelFrame(self.main_scrollable_content, text="FINANCIAL SUMMARY")
        summary_frame.pack(fill=tk.X, padx=5, pady=(15, 10), expand=True)
        
        # Create a frame inside summary_frame for better layout control
        summary_content = ttk.Frame(summary_frame)
        summary_content.pack(fill=tk.BOTH, padx=5, pady=15, expand=True)
        
        # Configure a larger font for summary labels
        summary_font = ('Helvetica', 16, 'bold')
        summary_value_font = ('Helvetica', 15, 'bold')
        
        # Create a gradient-like effect with frames of different colors
        income_frame = ttk.Frame(summary_content, padding=(15, 10))
        income_frame.grid(row=0, column=0, padx=15, pady=10, sticky=tk.NSEW)
        
        expense_frame = ttk.Frame(summary_content, padding=(15, 10))
        expense_frame.grid(row=0, column=1, padx=15, pady=10, sticky=tk.NSEW)
        
        balance_frame = ttk.Frame(summary_content, padding=(15, 10))
        balance_frame.grid(row=0, column=2, padx=15, pady=10, sticky=tk.NSEW)
        
        # Configure equal width columns
        summary_content.columnconfigure(0, weight=1, uniform="summary")
        summary_content.columnconfigure(1, weight=1, uniform="summary")
        summary_content.columnconfigure(2, weight=1, uniform="summary")
        
        # Labels for each metric
        ttk.Label(income_frame, text="Total Income", font=summary_font).pack(anchor=tk.CENTER)
        ttk.Label(expense_frame, text="Total Expenses", font=summary_font).pack(anchor=tk.CENTER)
        ttk.Label(balance_frame, text="Balance", font=summary_font).pack(anchor=tk.CENTER)
        
        # Value labels with larger font
        self.income_label = ttk.Label(income_frame, text="$0.00", font=summary_value_font)
        self.income_label.pack(anchor=tk.CENTER, pady=5)
        
        self.expense_label = ttk.Label(expense_frame, text="$0.00", font=summary_value_font)
        self.expense_label.pack(anchor=tk.CENTER, pady=5)
        
        self.balance_label = ttk.Label(balance_frame, text="$0.00", font=summary_value_font)
        self.balance_label.pack(anchor=tk.CENTER, pady=5)
        
        # Apply style based on theme
        if self.dark_theme.get():
            self.income_label.configure(foreground='lightgreen')
            self.expense_label.configure(foreground='salmon')
            # Change balance color from white to cyan for better visibility in dark mode
            self.balance_label.configure(foreground='cyan')
            
            # Apply different background colors to the frames in dark mode
            if hasattr(income_frame, 'configure'):  # Check if the method exists
                income_frame.configure(style='Income.TFrame')
                expense_frame.configure(style='Expense.TFrame')
                balance_frame.configure(style='Balance.TFrame')
        else:
            self.income_label.configure(foreground='green')
            self.expense_label.configure(foreground='red')
            self.balance_label.configure(foreground='blue')
            
            # Apply different background colors to the frames in light mode
            if hasattr(income_frame, 'configure'):  # Check if the method exists
                income_frame.configure(style='Income.TFrame')
                expense_frame.configure(style='Expense.TFrame')
                balance_frame.configure(style='Balance.TFrame')
                
        # Add a statistics section
        stats_frame = ttk.LabelFrame(self.main_scrollable_content, text="Quick Stats")
        stats_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)
        
        stats_content = ttk.Frame(stats_frame)
        stats_content.pack(fill=tk.BOTH, padx=5, pady=10, expand=True)
        
        # Create columns for stats
        stats_content.columnconfigure(0, weight=1)
        stats_content.columnconfigure(1, weight=1)
        stats_content.columnconfigure(2, weight=1)
        
        # Top spending categories
        top_categories_frame = ttk.Frame(stats_content)
        top_categories_frame.grid(row=0, column=0, padx=10, pady=5, sticky=tk.NSEW)
        
        ttk.Label(top_categories_frame, text="Top Categories", font=('Helvetica', 11, 'bold')).pack(anchor=tk.CENTER)
        self.top_categories_label = ttk.Label(top_categories_frame, text="accessory", justify=tk.CENTER)
        self.top_categories_label.pack(anchor=tk.CENTER, pady=5)
        
        # Recent activity
        recent_activity_frame = ttk.Frame(stats_content)
        recent_activity_frame.grid(row=0, column=1, padx=10, pady=5, sticky=tk.NSEW)
        
        ttk.Label(recent_activity_frame, text="Recent Activity", font=('Helvetica', 11, 'bold')).pack(anchor=tk.CENTER)
        self.recent_activity_label = ttk.Label(recent_activity_frame, text="100$ ⬆️", justify=tk.CENTER)
        self.recent_activity_label.pack(anchor=tk.CENTER, pady=5)
        
        # Month-to-Month change
        monthly_change_frame = ttk.Frame(stats_content)
        monthly_change_frame.grid(row=0, column=2, padx=10, pady=5, sticky=tk.NSEW)
        
        ttk.Label(monthly_change_frame, text="Monthly Change", font=('Helvetica', 11, 'bold')).pack(anchor=tk.CENTER)
        self.monthly_change_label = ttk.Label(monthly_change_frame, text="$12280.00", justify=tk.CENTER)
        self.monthly_change_label.pack(anchor=tk.CENTER, pady=5)

        # Filter frame now comes after summary and stats
        filter_frame = ttk.LabelFrame(self.main_scrollable_content, text="Transaction Filters")
        filter_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Add search functionality with better organization
        search_frame = ttk.Frame(filter_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Search field with icon-like prefix
        search_container = ttk.Frame(search_frame)
        search_container.pack(side=tk.LEFT, padx=10)
        ttk.Label(search_container, text="🔍").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_container, width=25)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        
        # Date range with better layout
        date_container = ttk.Frame(search_frame)
        date_container.pack(side=tk.LEFT, padx=15)
        ttk.Label(date_container, text="Date Range:").pack(side=tk.LEFT)
        ttk.Label(date_container, text="From").pack(side=tk.LEFT, padx=(10, 2))
        self.start_date_entry = ttk.Entry(date_container, width=12)
        self.start_date_entry.pack(side=tk.LEFT)
        ttk.Label(date_container, text="To").pack(side=tk.LEFT, padx=(10, 2))
        self.end_date_entry = ttk.Entry(date_container, width=12)
        self.end_date_entry.pack(side=tk.LEFT)

        # Category and type filters with better organization
        filter_options = ttk.Frame(filter_frame)
        filter_options.pack(fill=tk.X, padx=5, pady=5)
        
        category_container = ttk.Frame(filter_options)
        category_container.pack(side=tk.LEFT, padx=10)
        ttk.Label(category_container, text="Category:").pack(side=tk.LEFT)
        self.filter_category = ttk.Combobox(category_container, width=15)
        self.filter_category['values'] = ["All"] + self.db.get_categories()
        self.filter_category.current(0)
        self.filter_category.pack(side=tk.LEFT, padx=5)
        
        type_container = ttk.Frame(filter_options)
        type_container.pack(side=tk.LEFT, padx=15)
        ttk.Label(type_container, text="Type:").pack(side=tk.LEFT)
        self.filter_type = ttk.Combobox(type_container, width=10)
        self.filter_type['values'] = ["All", "Income", "Expense"]
        self.filter_type.current(0)
        self.filter_type.pack(side=tk.LEFT, padx=5)
        
        # Filter action buttons with better positioning
        button_container = ttk.Frame(filter_options)
        button_container.pack(side=tk.RIGHT, padx=10)
        ttk.Button(button_container, text="Clear Filters", command=self.clear_filters).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_container, text="Apply Filters", command=self.load_transactions).pack(side=tk.LEFT, padx=5)
        
        # Add a separator to visually divide the interface
        ttk.Separator(self.main_scrollable_content, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=10)

        # Transaction list section with a more descriptive label
        transactions_frame = ttk.LabelFrame(self.main_scrollable_content, text="Transaction History")
        transactions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Create a container for the tree and scrollbar
        tree_container = ttk.Frame(transactions_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('id', 'date', 'description', 'amount', 'category', 'type')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings')

        # Enhanced column configuration
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('description', width=200, anchor=tk.W)
        self.tree.column('amount', width=100, anchor=tk.E)
        self.tree.column('category', width=100, anchor=tk.CENTER)
        self.tree.column('type', width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click event to edit transaction
        self.tree.bind("<Double-1>", self.edit_transaction)
        
        # Button frame for action buttons at the bottom
        button_frame = ttk.Frame(self.main_scrollable_content)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)

        # Action buttons
        ttk.Button(button_frame, text="Select All", command=self.select_all_transactions).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Download CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=5)
        
        # Bind the Enter key to the search function
        self.search_entry.bind('<Return>', lambda event: self.load_transactions())
        
        if self.dark_theme.get():
            self.tree.tag_configure('income', foreground='lightgreen')
            self.tree.tag_configure('expense', foreground='salmon')
        else:
            self.tree.tag_configure('income', foreground='green')
            self.tree.tag_configure('expense', foreground='red')
            
    def on_main_canvas_configure(self, event):
        """Resize the canvas window when the canvas is resized"""
        # Update the width of the canvas window to match the canvas width
        self.main_canvas.itemconfig(self.main_frame, width=event.width)

    def on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # Scroll up/down (-/+)
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    def select_all_transactions(self):
        """Select all items in the transaction tree"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)


    def setup_budget_tab(self):
        # Add a prominent header for the Budget tab
        header_frame = ttk.Frame(self.budget_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        header_label = ttk.Label(header_frame, text="Budget Management", font=('Helvetica', 14, 'bold'))
        header_label.pack(side=tk.LEFT)
        
        # Add a small info button beside the header for help
        info_button = ttk.Button(header_frame, text="?", width=2, command=self.show_budget_help)
        info_button.pack(side=tk.RIGHT)
        
        # Budget entry section with interactive elements
        entry_frame = ttk.LabelFrame(self.budget_frame, text="Add/Edit Budget")
        entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Grid layout with more visible and interactive form fields
        category_label = ttk.Label(entry_frame, text="Category:", font=('Helvetica', 10, 'bold'))
        category_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.budget_category = ttk.Combobox(entry_frame, width=20)
        self.budget_category['values'] = self.db.get_categories()
        self.budget_category.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        amount_label = ttk.Label(entry_frame, text="Monthly Limit:", font=('Helvetica', 10, 'bold'))
        amount_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        
        # Currency input frame with $ symbol
        amount_frame = ttk.Frame(entry_frame)
        amount_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        currency_label = ttk.Label(amount_frame, text="$")
        currency_label.pack(side=tk.LEFT)
        
        self.budget_amount = ttk.Entry(amount_frame, width=19)
        self.budget_amount.pack(side=tk.LEFT)
        
        # Button frame with more interactive buttons
        button_frame = ttk.Frame(entry_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        set_budget_button = ttk.Button(button_frame, text="Set Budget", command=self.set_budget, width=15)
        set_budget_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear Form", command=self.clear_budget_form, width=15)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # Remove summary section (total budget and remaining budget)
        
        # Budget display section with more interactive features
        view_frame = ttk.LabelFrame(self.budget_frame, text="Current Budgets")
        view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add filter options for better interaction
        filter_frame = ttk.Frame(view_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Show:", font=('Helvetica', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="All")
        all_radio = ttk.Radiobutton(filter_frame, text="All", variable=self.filter_var, value="All", command=self.apply_filter)
        all_radio.pack(side=tk.LEFT, padx=5)
        
        over_radio = ttk.Radiobutton(filter_frame, text="Over Budget", variable=self.filter_var, value="Over", command=self.apply_filter)
        over_radio.pack(side=tk.LEFT, padx=5)
        
        under_radio = ttk.Radiobutton(filter_frame, text="Under Budget", variable=self.filter_var, value="Under", command=self.apply_filter)
        under_radio.pack(side=tk.LEFT, padx=5)
        
        # Create a container for the treeview and scrollbar
        tree_frame = ttk.Frame(view_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Setup treeview with better column proportions
        columns = ('category', 'budget', 'spent', 'remaining', 'status')
        self.budget_tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configure column headings with more visible text
        self.budget_tree.heading('category', text='Category')
        self.budget_tree.heading('budget', text='Budget')
        self.budget_tree.heading('spent', text='Spent')
        self.budget_tree.heading('remaining', text='Remaining')
        self.budget_tree.heading('status', text='Status')
        
        # Configure column widths with better proportions
        self.budget_tree.column('category', width=150)
        self.budget_tree.column('budget', width=100, anchor=tk.E)
        self.budget_tree.column('spent', width=100, anchor=tk.E)
        self.budget_tree.column('remaining', width=100, anchor=tk.E)
        self.budget_tree.column('status', width=100, anchor=tk.CENTER)
        
        # Create vertical scrollbar and associate with treeview
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        self.budget_tree.configure(yscroll=v_scrollbar.set)
        
        # Create horizontal scrollbar for better navigation
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.budget_tree.xview)
        self.budget_tree.configure(xscroll=h_scrollbar.set)
        
        # Position the scrollbars and treeview correctly
        self.budget_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights for proper expansion
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # Interactive buttons with clear labels
        button_frame = ttk.Frame(view_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        edit_btn = ttk.Button(button_frame, text="Edit Selected", command=self.edit_budget, width=15)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_budget, width=15)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Remove budget report button
        
        # Bind events for interactivity
        self.budget_tree.bind("<Double-1>", lambda event: self.edit_budget())
        self.budget_tree.bind("<<TreeviewSelect>>", self.on_budget_select)
        
        # Load current budgets
        self.load_budgets()

    def clear_budget_form(self):
        """Clear the budget entry form"""
        self.budget_category.set('')
        self.budget_amount.delete(0, tk.END)

    def on_budget_select(self, event):
        """Handle selection in the treeview"""
        # Placeholder for selection handling
        pass

    def apply_filter(self):
        """Apply filter to budget view"""
        self.load_budgets()

    def show_budget_help(self):
        """Show help information for the budget tab"""
        help_window = tk.Toplevel(self.budget_frame)
        help_window.title("Budget Help")
        help_window.geometry("400x300")
        help_window.transient(self.budget_frame)
        
        text = ttk.Label(help_window, text="Budget Management Help", font=('Helvetica', 12, 'bold'))
        text.pack(pady=10)
        
        help_text = """
        • To create a budget: Select a category, enter a monthly limit, and click 'Set Budget'.
        
        • To edit a budget: Select an existing budget from the list and click 'Edit Selected', or double-click on the budget item.
        
        • To delete a budget: Select a budget and click 'Delete Selected'.
        
        • Use the filter options to show specific budget categories.
        """
        
        msg = ttk.Label(help_window, text=help_text, justify=tk.LEFT, wraplength=380)
        msg.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def load_budgets(self):
        """Load budgets with filtering"""
        # Clear current treeview
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
        
        # Get budgets from database
        budgets = self.db.get_budgets()
        
        # Apply filtering based on selected filter option
        filter_value = self.filter_var.get()
        
        for budget in budgets:
            # Extract values from tuple
            category = budget[0]
            budget_amount = float(budget[1]) if budget[1] not in (None, '') and isinstance(budget[1], (int, float, str)) else 0
            spent_amount = float(budget[2]) if budget[2] not in (None, '') and isinstance(budget[2], (int, float, str)) else 0
            remaining_amount = float(budget[3]) if budget[3] not in (None, '') and isinstance(budget[3], (int, float, str)) else 0
            
            # Apply filter logic
            if filter_value == "All":
                pass  # Include all budgets
            elif filter_value == "Over" and spent_amount <= budget_amount:
                continue  # Skip this budget as it's not over budget
            elif filter_value == "Under" and spent_amount > budget_amount:
                continue  # Skip this budget as it's not under budget
            
            # Format values for display
            budget_formatted = f"${budget_amount:.2f}"
            spent_formatted = f"${spent_amount:.2f}"
            remaining_formatted = f"${remaining_amount:.2f}"
            
            # Determine status
            if spent_amount > budget_amount:
                status = "Over Budget"
            else:
                percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
                if percentage >= 80:
                    status = "Warning"
                else:
                    status = "Good"
            
            # Insert into treeview
            self.budget_tree.insert('', tk.END, values=(
                category,
                budget_formatted,
                spent_formatted,
                remaining_formatted,
                status
            ))




    def setup_analysis_tab(self):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        from collections import defaultdict
        import matplotlib.ticker as ticker

        # Clear previous content
        for widget in self.analysis_frame.winfo_children():
            widget.destroy()
            
        # Create a canvas with scrollbar for scrollable content
        self.analysis_canvas = tk.Canvas(self.analysis_frame)
        self.analysis_scrollbar = ttk.Scrollbar(self.analysis_frame, orient="vertical", command=self.analysis_canvas.yview)
        self.analysis_scrollable_content = ttk.Frame(self.analysis_canvas)
        
        # Configure the canvas
        self.analysis_scrollable_content.bind(
            "<Configure>",
            lambda e: self.analysis_canvas.configure(scrollregion=self.analysis_canvas.bbox("all"))
        )
        
        # Create a window inside the canvas that contains the scrollable content
        self.analysis_content_window = self.analysis_canvas.create_window((0, 0), window=self.analysis_scrollable_content, anchor="nw")
        
        # Configure canvas to expand with window
        self.analysis_canvas.bind("<Configure>", self.on_analysis_canvas_configure)
        
        # Pack the canvas and scrollbar
        self.analysis_canvas.pack(side="left", fill="both", expand=True)
        self.analysis_scrollbar.pack(side="right", fill="y")
        
        # Connect scrollbar to canvas
        self.analysis_canvas.configure(yscrollcommand=self.analysis_scrollbar.set)
        
        # Add mousewheel scrolling
        self.analysis_canvas.bind_all("<MouseWheel>", self.on_analysis_mousewheel)

        # Fetch data
        data = self.db.get_all_transactions()
        expense_time_series = defaultdict(float)
        income_time_series = defaultdict(float)
        category_totals = defaultdict(float)
        income_total, expense_total = 0, 0

        for t in data:
            _, date, _, amount, category, ttype, _ = t
            date_str = date.strftime('%Y-%m-%d')
            amount = float(amount)
            if ttype == 'expense':
                expense_time_series[date_str] += amount
                category_totals[category or "Uncategorized"] += amount
                expense_total += amount
            else:
                income_time_series[date_str] += amount
                income_total += amount

        dates_sorted = sorted(set(list(expense_time_series.keys()) + list(income_time_series.keys())))
        expenses_over_time = [expense_time_series.get(d, 0) for d in dates_sorted]
        incomes_over_time = [income_time_series.get(d, 0) for d in dates_sorted]

        # Add a title/header for the analysis section
        header_frame = ttk.Frame(self.analysis_scrollable_content)
        header_frame.pack(fill=tk.X, padx=10, pady=(15, 5))
        
        header_font = ('Helvetica', 16, 'bold')
        header_label = ttk.Label(header_frame, text="Financial Analysis Dashboard", font=header_font)
        header_label.pack(anchor=tk.CENTER, pady=5)
        
        # Add current date
        import datetime
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        date_label = ttk.Label(header_frame, text=f"Generated: {current_date}", font=('Helvetica', 10))
        date_label.pack(anchor=tk.CENTER)

        # Theme awareness
        is_dark = self.dark_theme.get()
        bg_color = "#1e1e1e" if is_dark else "white"
        text_color = "#FFD700" if is_dark else "black"

        # Create a frame for the charts
        charts_frame = ttk.Frame(self.analysis_scrollable_content)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        fig = Figure(figsize=(11, 7), facecolor=bg_color)
        axs = fig.subplots(2, 2)

        # Add more padding between plots to make room for category labels
        fig.subplots_adjust(
            left=0.09,    # distance from left side of figure
            right=0.93,   # distance from right side
            top=0.92,     # distance from top
            bottom=0.15,  # Increased bottom margin for category labels
            hspace=0.7,   # vertical space between rows
            wspace=0.4    # horizontal space between columns
        )

        # Line chart: Expenses Over Time
        axs[0, 0].plot(dates_sorted, expenses_over_time, color='red', marker='o', linestyle='-')
        axs[0, 0].set_title("Expenses Over Time", color=text_color, pad=15)
        axs[0, 0].tick_params(axis='x', labelrotation=45, labelcolor=text_color)
        axs[0, 0].tick_params(axis='y', labelcolor=text_color)
        axs[0, 0].yaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
        axs[0, 0].set_facecolor(bg_color)

        # Line chart: Income Over Time
        axs[0, 1].plot(dates_sorted, incomes_over_time, color='lime', marker='o', linestyle='-')
        axs[0, 1].set_title("Income Over Time", color=text_color, pad=15)
        axs[0, 1].tick_params(axis='x', labelrotation=45, labelcolor=text_color)
        axs[0, 1].tick_params(axis='y', labelcolor=text_color)
        axs[0, 1].yaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
        axs[0, 1].set_facecolor(bg_color)

        # Bar chart: Expenses by Category - Adjusted for better label visibility
        # Rotate the subplot to have horizontal bars for better label visibility
        categories = list(category_totals.keys())
        values = list(category_totals.values())
        axs[1, 0].barh(categories, values, color='steelblue')  # Use horizontal bars
        axs[1, 0].set_title("Expenses by Category", color=text_color, pad=15)
        axs[1, 0].tick_params(axis='y', labelcolor=text_color)  # y-axis now has the categories
        axs[1, 0].tick_params(axis='x', labelcolor=text_color)
        axs[1, 0].xaxis.set_major_locator(ticker.MaxNLocator(nbins=6))
        axs[1, 0].set_facecolor(bg_color)

        # Pie chart: Income vs Expenses
        axs[1, 1].pie(
            [income_total, expense_total],
            labels=['Income', 'Expenses'],
            autopct='%1.1f%%',
            colors=['green', 'orange'],
            textprops={'color': text_color}
        )
        axs[1, 1].set_title("Income vs Expenses", color=text_color, pad=15)

        # Clean look: remove top/right spines on all but pie
        for ax in [axs[0,0], axs[0,1], axs[1,0]]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # Embed the figure
        chart_canvas = FigureCanvasTkAgg(fig, master=charts_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add spacing before summary section to ensure category labels are visible
        spacer_frame = ttk.Frame(self.analysis_scrollable_content, height=30)
        spacer_frame.pack(fill=tk.X, pady=10)
        
        # Add a summary section below the charts
        summary_frame = ttk.LabelFrame(self.analysis_scrollable_content, text="Analysis Summary")
        summary_frame.pack(fill=tk.X, padx=20, pady=15)
        
        summary_content = ttk.Frame(summary_frame)
        summary_content.pack(fill=tk.BOTH, padx=10, pady=10)
        
        # Calculate some basic statistics
        avg_expense = expense_total / len(expense_time_series) if expense_time_series else 0
        avg_income = income_total / len(income_time_series) if income_time_series else 0
        top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else "None"
        
        # Create a grid for summary statistics
        stats_grid = ttk.Frame(summary_content)
        stats_grid.pack(fill=tk.X, pady=5)
        
        # Configure grid columns
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
        stats_grid.columnconfigure(2, weight=1)
        
        # Add statistics labels
        ttk.Label(stats_grid, text="Total Income:", font=('Helvetica', 11)).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=f"${income_total:.2f}", font=('Helvetica', 11, 'bold')).grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Total Expenses:", font=('Helvetica', 11)).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=f"${expense_total:.2f}", font=('Helvetica', 11, 'bold')).grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Average Daily Expense:", font=('Helvetica', 11)).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=f"${avg_expense:.2f}", font=('Helvetica', 11, 'bold')).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Average Daily Income:", font=('Helvetica', 11)).grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=f"${avg_income:.2f}", font=('Helvetica', 11, 'bold')).grid(row=3, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="Top Spending Category:", font=('Helvetica', 11)).grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Label(stats_grid, text=f"{top_category}", font=('Helvetica', 11, 'bold')).grid(row=4, column=1, sticky=tk.W, pady=2)
        
        # Add export buttons at the bottom
        button_frame = ttk.Frame(self.analysis_scrollable_content)
        button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        ttk.Button(button_frame, text="Export Analysis as PDF", command=self.export_analysis).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Refresh Data", command=self.setup_analysis_tab).pack(side=tk.RIGHT, padx=5)

    def on_analysis_canvas_configure(self, event):
        """Resize the canvas window when the canvas is resized"""
        # Update the width of the canvas window to match the canvas width
        self.analysis_canvas.itemconfig(self.analysis_content_window, width=event.width)

    def on_analysis_mousewheel(self, event):
        """Handle mousewheel scrolling for analysis tab"""
        # Scroll up/down (-/+)
        self.analysis_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
    def export_analysis(self):
        """Export the analysis as a PDF file"""
        from tkinter import filedialog, messagebox
        import matplotlib.pyplot as plt
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        import os
        import tempfile
        
        try:
            # Ask user where to save the PDF
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                title="Save Analysis as PDF"
            )
            
            if not file_path:  # User canceled
                return
                
            # Create a PDF document
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            elements = []
            
            # Add title
            styles = getSampleStyleSheet()
            elements.append(Paragraph("Financial Analysis Report", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Add date
            import datetime
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            elements.append(Paragraph(f"Generated: {current_date}", styles['Normal']))
            elements.append(Spacer(1, 24))
            
            # Save plots to temporary files
            with tempfile.TemporaryDirectory() as tmpdirname:
                # Re-fetch data to ensure consistency
                data = self.db.get_all_transactions()
                expense_time_series = defaultdict(float)
                income_time_series = defaultdict(float)
                category_totals = defaultdict(float)
                income_total, expense_total = 0, 0

                for t in data:
                    _, date, _, amount, category, ttype, _ = t
                    date_str = date.strftime('%Y-%m-%d')
                    amount = float(amount)
                    if ttype == 'expense':
                        expense_time_series[date_str] += amount
                        category_totals[category or "Uncategorized"] += amount
                        expense_total += amount
                    else:
                        income_time_series[date_str] += amount
                        income_total += amount
                        
                dates_sorted = sorted(set(list(expense_time_series.keys()) + list(income_time_series.keys())))
                expenses_over_time = [expense_time_series.get(d, 0) for d in dates_sorted]
                incomes_over_time = [income_time_series.get(d, 0) for d in dates_sorted]
                
                # Calculate statistics for report
                avg_expense = expense_total / len(expense_time_series) if expense_time_series else 0
                avg_income = income_total / len(income_time_series) if income_time_series else 0
                top_category = max(category_totals.items(), key=lambda x: x[1])[0] if category_totals else "None"
                
                # Create and save charts for PDF
                # Create a figure with 2x2 subplots
                fig = plt.figure(figsize=(10, 8))
                
                # Expenses Over Time
                ax1 = fig.add_subplot(221)
                ax1.plot(dates_sorted, expenses_over_time, color='red', marker='o', linestyle='-')
                ax1.set_title("Expenses Over Time")
                plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
                
                # Income Over Time
                ax2 = fig.add_subplot(222)
                ax2.plot(dates_sorted, incomes_over_time, color='green', marker='o', linestyle='-')
                ax2.set_title("Income Over Time")
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
                
                # Expenses by Category
                ax3 = fig.add_subplot(223)
                y_pos = range(len(category_totals))
                ax3.barh(y_pos, list(category_totals.values()), align='center')
                ax3.set_yticks(y_pos)
                ax3.set_yticklabels(list(category_totals.keys()))
                ax3.set_title("Expenses by Category")
                
                # Income vs Expenses Pie
                ax4 = fig.add_subplot(224)
                ax4.pie([income_total, expense_total], labels=['Income', 'Expenses'], 
                    autopct='%1.1f%%', colors=['green', 'orange'])
                ax4.set_title("Income vs Expenses")
                
                plt.tight_layout()
                
                # Save the figure to a temporary file
                chart_path = os.path.join(tmpdirname, 'charts.png')
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Add charts to PDF
                elements.append(Paragraph("Financial Charts", styles['Heading2']))
                elements.append(Spacer(1, 12))
                
                # Import the image into the PDF
                from reportlab.platypus import Image
                img = Image(chart_path)
                img.drawHeight = 400
                img.drawWidth = 500
                elements.append(img)
                elements.append(Spacer(1, 24))
                
                # Add summary statistics to PDF
                elements.append(Paragraph("Analysis Summary", styles['Heading2']))
                elements.append(Spacer(1, 12))
                
                # Create a table for the summary statistics
                data = [
                    ["Total Income:", f"${income_total:.2f}"],
                    ["Total Expenses:", f"${expense_total:.2f}"],
                    ["Average Daily Expense:", f"${avg_expense:.2f}"],
                    ["Average Daily Income:", f"${avg_income:.2f}"],
                    ["Top Spending Category:", top_category]
                ]
                
                t = Table(data, colWidths=[200, 200])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, 4), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (0, 4), colors.black),
                    ('ALIGN', (0, 0), (0, 4), 'LEFT'),
                    ('ALIGN', (1, 0), (1, 4), 'RIGHT'),
                    ('FONTNAME', (0, 0), (0, 4), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, 4), 'Helvetica'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(t)
                
                # Build the PDF
                doc.build(elements)
                
                messagebox.showinfo("Export Successful", f"Analysis has been exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export PDF: {str(e)}")
    
    def edit_budget(self):
        selected_item = self.budget_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a budget to edit")
            return
            
        # Get the category of the selected budget
        category = self.budget_tree.item(selected_item[0])['values'][0]
        
        # Get all budgets
        budgets = self.db.get_budgets()
        
        # Find the budget for this category
        budget_amount = None
        for cat, amount in budgets:
            if cat == category:
                budget_amount = float(amount)
                break
                
        if budget_amount is None:
            messagebox.showerror("Error", "Could not retrieve budget details")
            return
            
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Budget")
        edit_window.configure(bg=BG_COLOR)
        edit_window.geometry("400x200")
        edit_window.resizable(False, False)
        
        # Make the edit window modal
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Set up the edit form
        ttk.Label(edit_window, text="Category:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        category_label = ttk.Label(edit_window, text=category)
        category_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(edit_window, text="Monthly Limit:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        edit_amount = ttk.Entry(edit_window, width=15)
        edit_amount.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        edit_amount.insert(0, budget_amount)
        
        def save_changes():
            try:
                amount = edit_amount.get()
                
                if not amount:
                    messagebox.showerror("Error", "Please enter an amount!", parent=edit_window)
                    return
                    
                try:
                    amount = float(amount)
                    if amount <= 0:
                        messagebox.showerror("Error", "Budget amount must be positive!", parent=edit_window)
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid amount format!", parent=edit_window)
                    return
                    
                if self.db.add_budget(category, amount):  # Using the existing add_budget which has ON DUPLICATE KEY UPDATE
                    messagebox.showinfo("Success", f"Budget for {category} updated to ${amount:.2f}", parent=edit_window)
                    edit_window.destroy()
                    self.load_budgets()
                    self.check_alerts()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=edit_window)
        
        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=2, column=0, columnspan=2, padx=10, pady=20)
        
        # Center the window on the screen
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def delete_budget(self):
        selected_item = self.budget_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a budget to delete")
            return
        
        # Get the category of the selected budget
        category = self.budget_tree.item(selected_item[0])['values'][0]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete the budget for '{category}'?")
        if not confirm:
            return
        
        # Add the delete_budget method to the DatabaseHandler class
        if self.db.delete_budget(category):
            messagebox.showinfo("Success", f"Budget for '{category}' deleted successfully!")
            self.load_budgets()
            self.check_alerts()  # Add this line to update alerts after deletion
    
    # Add the export to CSV function
    def export_to_csv(self):
        # Get the currently filtered transactions
        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        category = self.filter_category.get() if self.filter_category.get() != "All" else None
        transaction_type = self.filter_type.get() if self.filter_type.get() != "All" else None
        search_keyword = self.search_entry.get() or None
        
        transactions = self.db.get_transactions(start_date, end_date, category, transaction_type, search_keyword)
        
        if not transactions:
            messagebox.showinfo("Export Info", "No transactions to export.")
            return
            
        # Ask user for save location
        default_filename = f"finance_tracker_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not file_path: 
            return
            
        try:
            with open(file_path, "w", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)
                
                # Write headers
                csv_writer.writerow(["ID", "Date", "Description", "Amount", "Category", "Type"])
                
                # Write data
                for t in transactions:
                    id, date, description, amount, category, ttype = t
                    csv_writer.writerow([
                        id, 
                        date.strftime('%Y-%m-%d'), 
                        description, 
                        f"{float(amount):.2f}", 
                        category or "", 
                        ttype.capitalize()
                    ])
                    
            messagebox.showinfo("Export Success", f"Successfully exported {len(transactions)} transactions to {file_path}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting to CSV: {str(e)}")
    def edit_transaction(self, event):
        from PIL import Image, ImageTk
        import time, shutil

        # 1) Fetch selection
        selected = self.tree.selection()
        if not selected:
            return
        transaction_id = self.tree.item(selected[0])['values'][0]
        txn = self.db.get_transaction(transaction_id)
        if not txn:
            messagebox.showerror("Error", "Could not retrieve transaction details")
            return

        # 2) Create & configure the edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transaction")
        edit_window.configure(bg=BG_COLOR)
        edit_window.geometry("500x500")
        edit_window.resizable(True, True)

        # **Make it modal** so it won't close when another dialog opens
        edit_window.transient(self.root)
        edit_window.grab_set()

        # 3) Build a scrollable frame
        canvas = tk.Canvas(edit_window, borderwidth=0, background=BG_COLOR)
        frame = ttk.Frame(canvas)
        vsb = ttk.Scrollbar(edit_window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=frame, anchor="nw")
        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # 4) Populate fields with existing data
        ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        edit_date = ttk.Entry(frame, width=15)
        edit_date.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        edit_date.insert(0, txn[1].strftime('%Y-%m-%d'))

        ttk.Label(frame, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        edit_desc = ttk.Entry(frame, width=30)
        edit_desc.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        edit_desc.insert(0, txn[2])

        ttk.Label(frame, text="Amount:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        edit_amount = ttk.Entry(frame, width=15)
        edit_amount.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        edit_amount.insert(0, txn[3])

        ttk.Label(frame, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        edit_cat = ttk.Combobox(frame, width=15, values=[""] + self.db.get_categories())
        edit_cat.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        edit_cat.set(txn[4] or "")

        ttk.Label(frame, text="Type:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        edit_type = tk.StringVar(value=txn[5])
        ttk.Radiobutton(frame, text="Expense", variable=edit_type, value="expense")\
        .grid(row=4, column=1, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(frame, text="Income", variable=edit_type, value="income")\
        .grid(row=4, column=2, padx=10, pady=10, sticky="w")

        # 5) Receipt controls
        ttk.Label(frame, text="Receipt Image:").grid(row=5, column=0, padx=10, pady=10, sticky="w")
        receipt_var = tk.StringVar(value=txn[6] or "")
        receipt_entry = ttk.Entry(frame, width=40, textvariable=receipt_var, state="readonly")
        receipt_entry.grid(row=5, column=1, columnspan=2, padx=10, pady=10, sticky="w")

        thumb_lbl = ttk.Label(frame, text="No receipt")
        thumb_lbl.grid(row=6, column=0, columnspan=3, padx=10, pady=5)

        def load_thumb(path):
            try:
                img = Image.open(path)
                img.thumbnail((300, 200), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                thumb_lbl.config(image=photo, text="")
                thumb_lbl.image = photo
            except Exception as e:
                thumb_lbl.config(text=f"Load error: {e}", image="")

        def upload_receipt():
            path = filedialog.askopenfilename(
                parent=edit_window,
                title="Select Receipt Image",
                filetypes=[("Image files","*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if path:
                receipt_var.set(path)
                load_thumb(path)

        def view_receipt():
            path = receipt_var.get()
            if path and os.path.exists(path):
                import subprocess, platform
                sys = platform.system()
                try:
                    if sys=="Windows":    os.startfile(path)
                    elif sys=="Darwin":   subprocess.call(["open", path])
                    else:                 subprocess.call(["xdg-open", path])
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot open image: {e}")

        def clear_receipt():
            receipt_var.set("")
            thumb_lbl.config(image="", text="No receipt")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=3, pady=5)
        ttk.Button(btn_frame, text="Upload", command=upload_receipt).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="View",   command=view_receipt).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear",  command=clear_receipt).pack(side="left", padx=5)

        # show existing thumbnail if present
        if txn[6] and os.path.exists(txn[6]):
            load_thumb(txn[6])

        # 6) Save
        def save_changes():
            d = edit_date.get()
            desc = edit_desc.get()
            amt = edit_amount.get()
            cat = edit_cat.get()
            ttype = edit_type.get()
            new_path = receipt_var.get()

            if not (d and desc and amt):
                messagebox.showerror("Error", "Fill all required fields", parent=edit_window)
                return
            try:
                datetime.strptime(d, '%Y-%m-%d')
                famt = float(amt)
            except:
                messagebox.showerror("Error", "Bad date or amount", parent=edit_window)
                return
            if hasattr(self, 'setup_analysis_tab'):
                self.setup_analysis_tab()


            # copy new receipt if changed
            stored = txn[6]
            if new_path and new_path != txn[6]:
                receipts_dir = os.path.join(os.path.dirname(__file__), "receipts")
                os.makedirs(receipts_dir, exist_ok=True)
                ext = os.path.splitext(new_path)[1]
                fname = f"receipt_{transaction_id}_{int(time.time())}{ext}"
                dest  = os.path.join(receipts_dir, fname)
                try:
                    shutil.copy2(new_path, dest)
                    stored = dest
                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not save receipt: {e}", parent=edit_window)

            if not new_path:
                stored = None

            # update DB (make sure your db method signature matches)
            if self.db.update_transaction(transaction_id, d, desc, famt, cat, ttype, stored):
                messagebox.showinfo("Success", "Transaction updated", parent=edit_window)
                edit_window.destroy()
                self.load_transactions()
                self.load_budgets()
                self.check_alerts()

        ttk.Button(frame, text="Save Changes", command=save_changes)\
        .grid(row=8, column=0, columnspan=3, pady=20)

        # 7) Center & focus
        edit_window.update_idletasks()
        w,h = edit_window.winfo_width(), edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth()//2) - (w//2)
        y = (edit_window.winfo_screenheight()//2) - (h//2)
        edit_window.geometry(f"{w}x{h}+{x}+{y}")
        edit_window.focus_force()

    def clear_filters(self):
        self.search_entry.delete(0, tk.END)
        self.start_date_entry.delete(0, tk.END)
        self.end_date_entry.delete(0, tk.END)
        self.filter_category.current(0)
        self.filter_type.current(0)
        self.load_transactions()

    def add_transaction(self):
        try:
            date = self.date_entry.get()
            description = self.desc_entry.get()
            amount = self.amount_entry.get()
            category = self.category_entry.get()
            transaction_type = self.type_var.get()
            receipt_path = self.receipt_path_var.get()  # Get receipt path

            if not date or not description or not amount:
                messagebox.showerror("Error", "Please fill all required fields!")
                return
           


            try:
                datetime.strptime(date, '%Y-%m-%d')
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format or amount!")
                return


            # Handle receipt file - copy to app directory if needed
            stored_receipt_path = None
            if receipt_path:
                # Create receipts directory if it doesn't exist
                receipts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipts")
                os.makedirs(receipts_dir, exist_ok=True)
                
                # Copy file to receipts directory with unique name
                filename = f"receipt_{date}_{int(time.time())}{os.path.splitext(receipt_path)[1]}"
                destination = os.path.join(receipts_dir, filename)
                
                try:
                    import shutil
                    shutil.copy2(receipt_path, destination)
                    stored_receipt_path = destination
                except Exception as e:
                    messagebox.showwarning("Warning", f"Could not save receipt image: {e}")
                    # Continue without receipt if copy fails

            # Pass the receipt path to the database method
            if self.db.add_transaction(date, description, amount, category, transaction_type, stored_receipt_path):
                messagebox.showinfo("Success", "Transaction added successfully!")
                self.desc_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                self.category_entry['values'] = [""] + self.db.get_categories()
                self.filter_category['values'] = ["All"] + self.db.get_categories()
                self.budget_category['values'] = self.db.get_categories()
                self.clear_receipt()  # Clear receipt field
                self.load_transactions()
                
                # Check budget alerts after adding an expense
                if transaction_type == "expense":
                    self.check_alerts()
        except Exception as e:
            messagebox.showerror("Error", str(e))
        if hasattr(self, 'setup_analysis_tab'):
            self.setup_analysis_tab()
    def set_budget(self):
        try:
            category = self.budget_category.get()
            amount = self.budget_amount.get()
            
            if not category or not amount:
                messagebox.showerror("Error", "Please enter both category and amount!")
                return
                
            try:
                amount = float(amount)
                if amount <= 0:
                    messagebox.showerror("Error", "Budget amount must be positive!")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid amount format!")
                return
                
            if self.db.add_budget(category, amount):
                messagebox.showinfo("Success", f"Budget for {category} set to ${amount:.2f}")
                self.budget_amount.delete(0, tk.END)
                self.load_budgets()
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_receipt_from_path(self, filepath):
        if filepath and os.path.exists(filepath):
            # Open the image with the default image viewer
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == 'Windows':
                    os.startfile(filepath)
                elif system == 'Darwin':  # macOS
                    subprocess.call(['open', filepath])
                else:  # Linux and other Unix-like
                    subprocess.call(['xdg-open', filepath])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open the image: {str(e)}")
        else:
            messagebox.showinfo("Info", "No valid receipt image to display")

    def replace_receipt(self, edit_window):
        # Open file dialog to select an image
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=filetypes,
            parent=edit_window
        )
        
        if filepath:
            # Create receipts directory if it doesn't exist
            receipts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "receipts")
            os.makedirs(receipts_dir, exist_ok=True)
            
            # Copy file to receipts directory with unique name
            date_str = datetime.now().strftime('%Y-%m-%d')
            filename = f"receipt_{date_str}_{int(time.time())}{os.path.splitext(filepath)[1]}"
            destination = os.path.join(receipts_dir, filename)
            
            try:
                shutil.copy2(filepath, destination)
                # Update the receipt path in the edit window
                edit_window.receipt_path = destination
                
                # Update the preview
                self.update_receipt_preview(edit_window, destination)
                
            except Exception as e:
                messagebox.showwarning("Warning", f"Could not save receipt image: {e}", parent=edit_window)

    # Remove the receipt in edit mode
    def remove_receipt(self, edit_window, preview_label):
        edit_window.receipt_path = None
        preview_label.config(text="No receipt image available", image="")
        edit_window.thumbnail_image = None

    # Update the receipt preview in edit window
    def update_receipt_preview(self, edit_window, filepath):
        # Find the receipt frame in edit_window's children
        receipt_frame = None
        for child in edit_window.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Receipt Image":
                receipt_frame = child
                break
        
        if not receipt_frame:
            return
        
        # Clear existing content
        for widget in receipt_frame.winfo_children():
            widget.destroy()
        
        try:
            # Import PIL for image handling
            from PIL import Image, ImageTk
            
            # Open and resize image for preview
            image = Image.open(filepath)
            
            # Calculate dimensions for the preview
            max_width, max_height = 400, 250
            width, height = image.size
            
            # Maintain aspect ratio
            aspect_ratio = width / height
            
            if width > max_width:
                width = max_width
                height = int(width / aspect_ratio)
                
            if height > max_height:
                height = max_height
                width = int(height * aspect_ratio)
                
            # Resize and convert for display
            image = image.resize((width, height), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Store reference to prevent garbage collection
            edit_window.thumbnail_image = photo
            
            # Display in label
            receipt_preview = ttk.Label(receipt_frame, image=photo)
            receipt_preview.pack(pady=10)
            
        except Exception as e:
            receipt_preview = ttk.Label(receipt_frame, text=f"Error loading image: {str(e)}")
            receipt_preview.pack(pady=20)


    def load_budgets(self):
        # Clear current items
        for i in self.budget_tree.get_children():
            self.budget_tree.delete(i)
        
        if self.dark_theme.get():
            self.tree.tag_configure('income', foreground='lightgreen')
            self.tree.tag_configure('expense', foreground='salmon')
        else:
            self.tree.tag_configure('income', foreground='green')
            self.tree.tag_configure('expense', foreground='red')    
        # Get all budgets
        budgets = self.db.get_budgets()
        
        # Get current month's spending
        spending = self.db.get_monthly_spending_by_category()
        
        # Add to tree
        for category, budget in budgets:
            spent = spending.get(category, 0)
            remaining = float(budget) - spent
            status = "✅" if remaining >= 0 else "❌ OVER BUDGET"
            
            self.budget_tree.insert('', tk.END, values=(
                category,
                f"${float(budget):.2f}",
                f"${spent:.2f}",
                f"${remaining:.2f}",
                status
            ))
            
    def check_alerts(self):
        self.alerts = self.db.check_budget_alerts()
    
        if self.alerts:
            alert_msg = "Budget Alert!\n\n"
            for category, budget, spent in self.alerts:
                over_amount = spent - budget
                alert_msg += f"Category '{category}' is over budget by ${over_amount:.2f}\n"
                alert_msg += f"Budget: ${budget:.2f}, Spent: ${spent:.2f}\n\n"
            
            messagebox.showwarning
            
    def check_alerts(self):
        self.alerts = self.db.check_budget_alerts()
    
        if self.alerts:
            alert_msg = "Budget Alert!\n\n"
            for category, budget, spent in self.alerts:
                over_amount = spent - budget
                alert_msg += f"Category '{category}' is over budget by ${over_amount:.2f}\n"
                alert_msg += f"Budget: ${budget:.2f}, Spent: ${spent:.2f}\n\n"
            
            messagebox.showwarning("Budget Alert", alert_msg)
        
        # Also update the budget view
        self.load_budgets()

    def load_transactions(self):
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Get filter values
        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        category = self.filter_category.get() if self.filter_category.get() != "All" else None
        transaction_type = self.filter_type.get() if self.filter_type.get() != "All" else None
        search_keyword = self.search_entry.get() or None
        
        transactions = self.db.get_transactions(start_date, end_date, category, transaction_type, search_keyword)
        
        # Variables for summary
        total_income = 0
        total_expense = 0
        
        # Populate the treeview
        for t in transactions:
            id, date, description, amount, category, ttype, receipt_path = t
            
            # Update totals
            if ttype == 'income':
                total_income += float(amount)
                tag = 'income'
            else:
                total_expense += float(amount)
                tag = 'expense'
                
            # Format the date and amount
            formatted_date = date.strftime('%Y-%m-%d')
            formatted_amount = f"${float(amount):.2f}"
            
            # Insert into treeview
            self.tree.insert('', tk.END, values=(
                id, formatted_date, description, formatted_amount, 
                category or "", ttype.capitalize()
            ), tags=(tag,))
        
        # Update summary labels
        balance = total_income - total_expense
        
        self.income_label.config(text=f"Total Income: ${total_income:.2f}")
        self.expense_label.config(text=f"Total Expenses: ${total_expense:.2f}")
        self.balance_label.config(text=f"Balance: ${balance:.2f}")
        
        # Configure tag colors
        self.tree.tag_configure('income', foreground='green')
        self.tree.tag_configure('expense', foreground='red')

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a transaction to delete")
            return
        
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?")
        if not confirm:
            return
        
        transaction_id = self.tree.item(selected_item[0])['values'][0]
        if self.db.delete_transaction(transaction_id):
            messagebox.showinfo("Success", "Transaction deleted successfully!")
            self.load_transactions()
            self.load_budgets()  # Update budget status after deletion
            self.check_alerts()
            self.setup_analysis_tab() 

    def error_control(self):
        try:
            self.load_transaction()
        except:
            return KeyError

    def set_theme(self):
        # Set the color variables based on the current theme
        global BG_COLOR, TEXT_COLOR, ENTRY_BG, ENTRY_FG, BUTTON_BG, BUTTON_FG
        
        if self.dark_theme.get():
            BG_COLOR = DARK_BG_COLOR
            TEXT_COLOR = DARK_TEXT_COLOR
            ENTRY_BG = DARK_ENTRY_BG
            ENTRY_FG = DARK_ENTRY_FG
            BUTTON_BG = DARK_BUTTON_BG
            BUTTON_FG = DARK_BUTTON_FG
        else:
            BG_COLOR = LIGHT_BG_COLOR
            TEXT_COLOR = LIGHT_TEXT_COLOR
            ENTRY_BG = LIGHT_ENTRY_BG
            ENTRY_FG = LIGHT_ENTRY_FG
            BUTTON_BG = LIGHT_BUTTON_BG
            BUTTON_FG = LIGHT_BUTTON_FG
        
        # Configure the main window and the style
        self.root.configure(bg=BG_COLOR)
        
        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, fieldbackground=ENTRY_BG)
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG)
        style.map("TButton", background=[('active', BUTTON_BG)], foreground=[('active', BUTTON_FG)])
        
        # Update frames if they exist
        if hasattr(self, 'add_frame'):
            self.add_frame.configure(style="TFrame")
            self.view_frame.configure(style="TFrame")
            self.budget_frame.configure(style="TFrame")


    def on_closing(self):
        if hasattr(self, 'db'):
            self.db.close()
        self.root.destroy()