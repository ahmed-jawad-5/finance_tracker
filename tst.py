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
                password="Ahmed@1220",  # Replace with your MySQL password
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

    def get_transactions(self, start_date=None, end_date=None, category=None, transaction_type=None):
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
        
    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.add_frame = ttk.Frame(self.notebook)
        self.add_frame.configure(style="TFrame")
        self.notebook.add(self.add_frame, text="Add Transaction")
        
        self.view_frame = ttk.Frame(self.notebook)
        self.view_frame.configure(style="TFrame")
        self.notebook.add(self.view_frame, text="View Transactions")
        
        self.setup_add_transaction_tab()
        self.setup_view_transactions_tab()
        
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

        ttk.Label(filter_frame, text="From:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame, width=12)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(filter_frame, text="To:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame, width=12)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="Category:").grid(row=0, column=4, padx=5, pady=5)
        self.filter_category = ttk.Combobox(filter_frame, width=15)
        self.filter_category['values'] = ["All"] + self.db.get_categories()
        self.filter_category.current(0)
        self.filter_category.grid(row=0, column=5, padx=5, pady=5)

        ttk.Label(filter_frame, text="Type:").grid(row=0, column=6, padx=5, pady=5)
        self.filter_type = ttk.Combobox(filter_frame, width=10)
        self.filter_type['values'] = ["All", "Income", "Expense"]
        self.filter_type.current(0)
        self.filter_type.grid(row=0, column=7, padx=5, pady=5)

        ttk.Button(filter_frame, text="Apply Filters", command=self.load_transactions).grid(row=0, column=8, padx=10, pady=5)

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

        ttk.Button(self.view_frame, text="Delete Selected", command=self.delete_selected).pack(pady=5, anchor=tk.E, padx=10)

        summary_frame = ttk.LabelFrame(self.view_frame, text="Summary")
        summary_frame.pack(fill=tk.X, padx=10, pady=10)

        self.income_label = ttk.Label(summary_frame, text="Total Income: $0.00")
        self.income_label.grid(row=0, column=0, padx=20, pady=5)

        self.expense_label = ttk.Label(summary_frame, text="Total Expenses: $0.00")
        self.expense_label.grid(row=0, column=1, padx=20, pady=5)

        self.balance_label = ttk.Label(summary_frame, text="Balance: $0.00")
        self.balance_label.grid(row=0, column=2, padx=20, pady=5)

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
                self.load_transactions()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_transactions(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        start_date = self.start_date_entry.get() or None
        end_date = self.end_date_entry.get() or None
        category = self.filter_category.get() if self.filter_category.get() != "All" else None
        transaction_type = self.filter_type.get() if self.filter_type.get() != "All" else None

        transactions = self.db.get_transactions(start_date, end_date, category, transaction_type)

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

    def on_closing(self):
        self.db.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
