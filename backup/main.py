import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# Define theme colors
BG_COLOR = "#1e1e1e"
TEXT_COLOR = "#FFD700"
ENTRY_BG = "#2a2a2a"
ENTRY_FG = "white"
BUTTON_BG = "#000000"
BUTTON_FG = "#FFD700"

class DatabaseHandler:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Ahmed@1220",  
                database="finance_tracker",
                auth_plugin='mysql_native_password'
            )
            self.cursor = self.conn.cursor()
            self.create_tables()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to connect to database: {err}")
            raise

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                date DATE NOT NULL,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(100),
                transaction_type ENUM('income', 'expense') NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(100) NOT NULL UNIQUE,
                amount DECIMAL(10, 2) NOT NULL
            )
        """)
        self.conn.commit()

    def add_transaction(self, date, description, amount, category, transaction_type):
        try:
            query = """INSERT INTO transactions 
                    (date, description, amount, category, transaction_type) 
                    VALUES (%s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (date, description, amount, category, transaction_type))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add transaction: {err}")
            return False

    def update_transaction(self, transaction_id, date, description, amount, category, transaction_type):
        try:
            query = """UPDATE transactions 
                    SET date = %s, description = %s, amount = %s, category = %s, transaction_type = %s
                    WHERE id = %s"""
            self.cursor.execute(query, (date, description, amount, category, transaction_type, transaction_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update transaction: {err}")
            return False

    def get_transaction(self, transaction_id):
        try:
            self.cursor.execute("SELECT * FROM transactions WHERE id = %s", (transaction_id,))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch transaction: {err}")
            return None

    def get_transactions(self, start_date=None, end_date=None, category=None, transaction_type=None, search_keyword=None):
        try:
            conditions = []
            params = []
            
            if start_date:
                conditions.append("date >= %s")
                params.append(start_date)
            
            if end_date:
                conditions.append("date <= %s")
                params.append(end_date)
            
            if category and category != "All":
                conditions.append("category = %s")
                params.append(category)
            
            if transaction_type and transaction_type != "All":
                conditions.append("transaction_type = %s")
                params.append(transaction_type.lower())
            
            if search_keyword:
                conditions.append("description LIKE %s")
                params.append(f"%{search_keyword}%")
            
            query = "SELECT * FROM transactions"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY date DESC"
            
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch transactions: {err}")
            return []
            
    def get_categories(self):
        try:
            self.cursor.execute("SELECT DISTINCT category FROM transactions")
            categories = [category[0] for category in self.cursor.fetchall() if category[0]]
            return categories
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch categories: {err}")
            return []
            
    def delete_transaction(self, transaction_id):
        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete transaction: {err}")
            return False
    
    def add_budget(self, category, amount):
        try:
            query = """INSERT INTO budgets (category, amount) 
                    VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE amount = %s"""
            self.cursor.execute(query, (category, amount, amount))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add budget: {err}")
            return False

    def get_budgets(self):
        try:
            self.cursor.execute("SELECT category, amount FROM budgets")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch budgets: {err}")
            return []
            
    def get_monthly_spending_by_category(self, year=None, month=None):
        try:
            if year is None or month is None:
                today = datetime.today()
                year = today.year
                month = today.month
                
            query = """
                SELECT category, SUM(amount) as total
                FROM transactions 
                WHERE transaction_type = 'expense'
                AND YEAR(date) = %s AND MONTH(date) = %s
                GROUP BY category
            """
            self.cursor.execute(query, (year, month))
            return {category: float(total) for category, total in self.cursor.fetchall()}
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch monthly spending: {err}")
            return {}

    def check_budget_alerts(self):
        # Get all budgets
        budgets = {category: float(amount) for category, amount in self.get_budgets()}
        if not budgets:
            return []
            
        # Get current month's spending
        monthly_spending = self.get_monthly_spending_by_category()
        
        # Check which categories exceed budget
        alerts = []
        for category, budget in budgets.items():
            if category in monthly_spending and monthly_spending[category] > budget:
                alerts.append((category, budget, monthly_spending[category]))
                
        return alerts
    
    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Tracker")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        self.root.configure(bg=BG_COLOR)

        style = ttk.Style()
        style.theme_use("default")
        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR, fieldbackground=ENTRY_BG)
        style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        style.configure("TCombobox", fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure("TButton", background=BUTTON_BG, foreground=BUTTON_FG)
        style.map("TButton", background=[('active', BUTTON_BG)], foreground=[('active', BUTTON_FG)])

        self.db = DatabaseHandler()
        self.create_widgets()
        self.load_transactions()
        
        # Check for budget alerts on startup
        self.root.after(1000, self.check_alerts)
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_frame = ttk.Frame(self.notebook)
        self.add_frame.configure(style="TFrame")
        self.notebook.add(self.add_frame, text="Add Transaction")
        
        self.view_frame = ttk.Frame(self.notebook)
        self.view_frame.configure(style="TFrame")
        self.notebook.add(self.view_frame, text="View Transactions")
        
        # Add budget tab
        self.budget_frame = ttk.Frame(self.notebook)
        self.budget_frame.configure(style="TFrame")
        self.notebook.add(self.budget_frame, text="Budgets")
        
        self.setup_add_transaction_tab()
        self.setup_view_transactions_tab()
        self.setup_budget_tab()
        
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

        ttk.Button(self.view_frame, text="Delete Selected", command=self.delete_selected).pack(pady=5, anchor=tk.E, padx=10)

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
        
        # Load current budgets
        self.load_budgets()

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
        edit_amount.insert(0, float(transaction[3]))
        
        ttk.Label(edit_window, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        edit_category = ttk.Combobox(edit_window, width=15)
        edit_category['values'] = [""] + self.db.get_categories()
        edit_category.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        if transaction[4]:
            edit_category.set(transaction[4])
        
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
        alerts = self.db.check_budget_alerts()
        
        if alerts:
            alert_msg = "Budget Alert!\n\n"
            for category, budget, spent in alerts:
                over_amount = spent - budget
                alert_msg += f"• {category}: Over budget by ${over_amount:.2f}\n"
                
            messagebox.showwarning("Budget Alert", alert_msg)
            
        # Also update budget display
        self.load_budgets()

    def load_transactions(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        category = self.filter_category.get() if self.filter_category.get() != "All" else None
        transaction_type = self.filter_type.get() if self.filter_type.get() != "All" else None
        search_keyword = self.search_entry.get() or None

        transactions = self.db.get_transactions(start_date, end_date, category, transaction_type, search_keyword)

        total_income = 0
        total_expenses = 0

        for t in transactions:
            id, date, description, amount, category, ttype = t
            if ttype == 'income':
                total_income += float(amount)
            else:
                total_expenses += float(amount)
            self.tree.insert('', tk.END, values=(id, date.strftime('%Y-%m-%d'), description, f"${amount:.2f}", category, ttype.capitalize()))

        self.income_label.config(text=f"Total Income: ${total_income:.2f}")
        self.expense_label.config(text=f"Total Expenses: ${total_expenses:.2f}")
        self.balance_label.config(text=f"Balance: ${total_income - total_expenses:.2f}")

    def delete_selected(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a transaction to delete")
            return

        transaction_id = self.tree.item(selected_item[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            if self.db.delete_transaction(transaction_id):
                messagebox.showinfo("Success", "Transaction deleted successfully!")
                self.load_transactions()
                self.load_budgets()  # Refresh budget display after deletion

    def on_closing(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()