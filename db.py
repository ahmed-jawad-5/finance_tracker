import mysql.connector
from tkinter import messagebox
from datetime import datetime

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
    def delete_budget(self, category):
        try:
            query = "DELETE FROM budgets WHERE category = %s"
            self.cursor.execute(query, (category,))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete budget: {err}")
            return False
        
    def close(self):
        if hasattr(self, 'cursor') and self.cursor:
            self.cursor.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()