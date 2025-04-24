import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
from db import DatabaseHandler


DARK_BG_COLOR = "#1e1e1e"
DARK_TEXT_COLOR = "#FFD700"
DARK_ENTRY_BG = "#2a2a2a"
DARK_ENTRY_FG = "white"
DARK_BUTTON_BG = "#000000"
DARK_BUTTON_FG = "#FFD700"

# Light theme (new)
LIGHT_BG_COLOR = "#f0f0f0"
LIGHT_TEXT_COLOR = "#000000"
LIGHT_ENTRY_BG = "#ffffff"
LIGHT_ENTRY_FG = "#000000"
LIGHT_BUTTON_BG = "#e0e0e0"
LIGHT_BUTTON_FG = "#000000"

# Initialize with dark theme
BG_COLOR = DARK_BG_COLOR
TEXT_COLOR = DARK_TEXT_COLOR
ENTRY_BG = DARK_ENTRY_BG
ENTRY_FG = DARK_ENTRY_FG
BUTTON_BG = DARK_BUTTON_BG
BUTTON_FG = DARK_BUTTON_FG

class FinanceTrackerApp:
    def __init__(self, root, user_id=None):
        self.root = root
        self.user_id = user_id  # Store the user ID
        self.root.title(f"Finance Tracker - User {user_id}" if user_id else "Finance Tracker")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Add a theme toggle variable
        self.dark_theme = tk.BooleanVar(value=True)  # Start with dark theme
        
        # Initialize database with user_id
        self.db = DatabaseHandler(user_id)

        # Apply initial theme
        self.set_theme()
        
        self.db = DatabaseHandler()
        self.create_widgets()
        
        # Move this line after create_widgets so that self.tree exists
        self.load_transactions()
        
        # Check for budget alerts on startup
        self.root.after(1000, self.check_alerts)        
    
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.theme_button = ttk.Button(self.root, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.place(relx=0.95, rely=0.02, anchor="ne")
        
        self.add_frame = ttk.Frame(self.notebook)
        self.view_frame = ttk.Frame(self.notebook)  # <--- Add this line
        self.budget_frame = ttk.Frame(self.notebook)  # <--- Also prepare budget frame

        self.add_frame.configure(style="TFrame")
        self.view_frame.configure(style="TFrame")  # <--- Add this line
        self.budget_frame.configure(style="TFrame")  # <--- Configure budget frame too

        self.notebook.add(self.add_frame, text="Add Transaction")
        self.notebook.add(self.view_frame, text="View Transactions")  # <--- Add this tab
        self.notebook.add(self.budget_frame, text="Budgets")  # <--- Add this tab too

        self.setup_add_transaction_tab()
        self.setup_view_transactions_tab()  # <--- Call it so self.tree is defined
        self.setup_budget_tab()             # <--- Set up budget UI too
    
    def toggle_theme(self):
        # Toggle the theme value
        self.dark_theme.set(not self.dark_theme.get())
        # Apply the new theme
        self.set_theme()
        
        # Update tree colors for income/expense tags
        if hasattr(self, 'tree'):
            # Configure tag colors based on theme
            if self.dark_theme.get():
                self.tree.tag_configure('income', foreground='lightgreen')
                self.tree.tag_configure('expense', foreground='salmon')
            else:
                self.tree.tag_configure('income', foreground='green')
                self.tree.tag_configure('expense', foreground='red')
                
    def setup_add_transaction_tab(self):
        ttk.Label(self.add_frame, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = ttk.Entry(self.add_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
        
        ttk.Label(self.add_frame, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.desc_entry = ttk.Entry(self.add_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.add_frame, text="Amount:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = ttk.Entry(self.add_frame, width=15)
        self.amount_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.add_frame, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.category_entry = ttk.Combobox(self.add_frame, width=15)
        self.category_entry['values'] = [""] + self.db.get_categories()
        self.category_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(self.add_frame, text="Type:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.type_var = tk.StringVar(value="expense")
        ttk.Radiobutton(self.add_frame, text="Expense", variable=self.type_var, value="expense").grid(row=4, column=1, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(self.add_frame, text="Income", variable=self.type_var, value="income").grid(row=4, column=2, padx=10, pady=10, sticky="w")
        
        ttk.Button(self.add_frame, text="Add Transaction", command=self.add_transaction).grid(row=5, column=0, columnspan=3, padx=10, pady=20)
        
    def setup_view_transactions_tab(self):
        filter_frame = ttk.LabelFrame(self.view_frame, text="Filters")
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Add search functionality
        ttk.Label(filter_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(filter_frame, width=20)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="From:").grid(row=0, column=2, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=4, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(filter_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, width=15)
        self.filter_category['values'] = ["All"] + self.db.get_categories()
        self.filter_category.current(0)
        self.filter_category.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="Type:").grid(row=1, column=2, padx=5, pady=5)
        self.filter_type = ttk.Combobox(filter_frame, width=10)
        self.filter_type['values'] = ["All", "Income", "Expense"]
        self.filter_type.current(0)
        self.filter_type.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(filter_frame, text="Apply Filters", command=self.load_transactions).grid(row=1, column=5, padx=10, pady=5)
        ttk.Button(filter_frame, text="Clear Filters", command=self.clear_filters).grid(row=1, column=4, padx=10, pady=5)

        columns = ('id', 'date', 'description', 'amount', 'category', 'type')
        self.tree = ttk.Treeview(self.view_frame, columns=columns, show='headings')

        for col in columns:
            self.tree.heading(col, text=col.capitalize())
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('amount', anchor=tk.E)

        scrollbar = ttk.Scrollbar(self.view_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click event to edit transaction
        self.tree.bind("<Double-1>", self.edit_transaction)

        # Button frame for Delete and Export buttons
        button_frame = ttk.Frame(self.view_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=5)
        
        # Add Export to CSV button
        ttk.Button(button_frame, text="Download CSV", command=self.export_to_csv).pack(side=tk.RIGHT, padx=5)

        summary_frame = ttk.LabelFrame(self.view_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        self.income_label = ttk.Label(summary_frame, text="Total Income: $0.00")
        self.income_label.grid(row=0, column=0, padx=20, pady=5)

        self.expense_label = ttk.Label(summary_frame, text="Total Expenses: $0.00")
        self.expense_label.grid(row=0, column=1, padx=20, pady=5)

        self.balance_label = ttk.Label(summary_frame, text="Balance: $0.00")
        self.balance_label.grid(row=0, column=2, padx=20, pady=5)
        
        # Bind the Enter key to the search function
        self.search_entry.bind('<Return>', lambda event: self.load_transactions())
        
        if self.dark_theme.get():
            self.tree.tag_configure('income', foreground='lightgreen')
            self.tree.tag_configure('expense', foreground='salmon')
        else:
            self.tree.tag_configure('income', foreground='green')
            self.tree.tag_configure('expense', foreground='red')
    
    def setup_budget_tab(self):
        # Budget entry section
        entry_frame = ttk.LabelFrame(self.budget_frame, text="Add/Edit Budget")
        entry_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(entry_frame, text="Category:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.budget_category = ttk.Combobox(entry_frame, width=15)
        self.budget_category['values'] = self.db.get_categories()
        self.budget_category.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Label(entry_frame, text="Monthly Limit:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.budget_amount = ttk.Entry(entry_frame, width=15)
        self.budget_amount.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Button(entry_frame, text="Set Budget", command=self.set_budget).grid(row=2, column=0, columnspan=2, padx=10, pady=10)
        
        # Budget display section
        view_frame = ttk.LabelFrame(self.budget_frame, text="Current Budgets")
        view_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('category', 'budget', 'spent', 'remaining', 'status')
        self.budget_tree = ttk.Treeview(view_frame, columns=columns, show='headings')
        
        self.budget_tree.heading('category', text='Category')
        self.budget_tree.heading('budget', text='Budget')
        self.budget_tree.heading('spent', text='Spent')
        self.budget_tree.heading('remaining', text='Remaining')
        self.budget_tree.heading('status', text='Status')
        
        self.budget_tree.column('category', width=150)
        self.budget_tree.column('budget', width=100, anchor=tk.E)
        self.budget_tree.column('spent', width=100, anchor=tk.E)
        self.budget_tree.column('remaining', width=100, anchor=tk.E)
        self.budget_tree.column('status', width=100, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(view_frame, orient=tk.VERTICAL, command=self.budget_tree.yview)
        self.budget_tree.configure(yscroll=scrollbar.set)
        self.budget_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add buttons for Edit and Delete operations
        button_frame = ttk.Frame(view_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Edit Selected", command=self.edit_budget).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_budget).pack(side=tk.LEFT, padx=5)
        
        # Bind double-click event to edit budget
        self.budget_tree.bind("<Double-1>", lambda event: self.edit_budget())
        
        # Load current budgets
        self.load_budgets()
    
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
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        transaction_id = self.tree.item(selected_item[0])['values'][0]
        transaction = self.db.get_transaction(transaction_id)
        
        if not transaction:
            messagebox.showerror("Error", "Could not retrieve transaction details")
            return
            
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Transaction")
        edit_window.configure(bg=BG_COLOR)
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        
        # Make the edit window modal
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Set up the edit form
        ttk.Label(edit_window, text="Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        edit_date = ttk.Entry(edit_window, width=15)
        edit_date.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        edit_date.insert(0, transaction[1].strftime('%Y-%m-%d'))
        
        ttk.Label(edit_window, text="Description:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        edit_desc = ttk.Entry(edit_window, width=30)
        edit_desc.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        edit_desc.insert(0, transaction[2])
        
        ttk.Label(edit_window, text="Amount:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        edit_amount = ttk.Entry(edit_window, width=15)
        edit_amount.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        edit_amount.insert(0, transaction[3])
        
        ttk.Label(edit_window, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        edit_category = ttk.Combobox(edit_window, width=15)
        edit_category['values'] = [""] + self.db.get_categories()
        edit_category.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        edit_category.set(transaction[4] or "")
        
        ttk.Label(edit_window, text="Type:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        edit_type_var = tk.StringVar(value=transaction[5])
        ttk.Radiobutton(edit_window, text="Expense", variable=edit_type_var, value="expense").grid(row=4, column=1, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(edit_window, text="Income", variable=edit_type_var, value="income").grid(row=4, column=2, padx=10, pady=10, sticky="w")
        
        # Save button
        def save_changes():
            try:
                date = edit_date.get()
                description = edit_desc.get()
                amount = edit_amount.get()
                category = edit_category.get()
                transaction_type = edit_type_var.get()

                if not date or not description or not amount:
                    messagebox.showerror("Error", "Please fill all required fields!", parent=edit_window)
                    return

                try:
                    datetime.strptime(date, '%Y-%m-%d')
                    amount = float(amount)
                except ValueError:
                    messagebox.showerror("Error", "Invalid date format or amount!", parent=edit_window)
                    return

                if self.db.update_transaction(transaction_id, date, description, amount, category, transaction_type):
                    messagebox.showinfo("Success", "Transaction updated successfully!", parent=edit_window)
                    edit_window.destroy()
                    self.load_transactions()
                    self.load_budgets()
                    self.check_alerts()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=edit_window)
                
        ttk.Button(edit_window, text="Save Changes", command=save_changes).grid(row=5, column=0, columnspan=3, padx=10, pady=20)
        
        # Center the window on the screen
        edit_window.update_idletasks()
        width = edit_window.winfo_width()
        height = edit_window.winfo_height()
        x = (edit_window.winfo_screenwidth() // 2) - (width // 2)
        y = (edit_window.winfo_screenheight() // 2) - (height // 2)
        edit_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))

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

            if not date or not description or not amount:
                messagebox.showerror("Error", "Please fill all required fields!")
                return

            try:
                datetime.strptime(date, '%Y-%m-%d')
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format or amount!")
                return

            if self.db.add_transaction(date, description, amount, category, transaction_type):
                messagebox.showinfo("Success", "Transaction added successfully!")
                self.desc_entry.delete(0, tk.END)
                self.amount_entry.delete(0, tk.END)
                self.category_entry['values'] = [""] + self.db.get_categories()
                self.filter_category['values'] = ["All"] + self.db.get_categories()
                self.budget_category['values'] = self.db.get_categories()
                self.load_transactions()
                
                # Check budget alerts after adding an expense
                if transaction_type == "expense":
                    self.check_alerts()
        except Exception as e:
            messagebox.showerror("Error", str(e))

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
            id, date, description, amount, category, ttype = t
            
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