import mysql.connector
from tkinter import messagebox
from datetime import datetime
import hashlib

class DatabaseHandler:
    def __init__(self , user_id = None):
        self.user_id = user_id
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
        # Create users table if not exists
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create transactions table with user_id foreign key
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                date DATE NOT NULL,
                description VARCHAR(255) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                category VARCHAR(100),
                transaction_type ENUM('income', 'expense') NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create budgets table with user_id foreign key
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                category VARCHAR(100) NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE (user_id, category)
            )
        """)
        self.conn.commit()

    def add_user(self, username, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            self.cursor.execute(query, (username, hashed_password))
            self.conn.commit()
            return self.cursor.lastrowid
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add user: {err}")
            return None

    def authenticate_user(self, username, password):
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            query = "SELECT id FROM users WHERE username = %s AND password = %s"
            self.cursor.execute(query, (username, hashed_password))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to authenticate user: {err}")
            return None

    def username_exists(self, username):
        try:
            query = "SELECT COUNT(*) FROM users WHERE username = %s"
            self.cursor.execute(query, (username,))
            return self.cursor.fetchone()[0] > 0
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to check username: {err}")
            return False

    def add_transaction(self, user_id, date, description, amount, category, transaction_type):
        try:
            query = """INSERT INTO transactions 
                    (user_id, date, description, amount, category, transaction_type) 
                    VALUES (%s, %s, %s, %s, %s, %s)"""
            self.cursor.execute(query, (user_id, date, description, amount, category, transaction_type))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add transaction: {err}")
            return False

    def update_transaction(self, user_id, transaction_id, date, description, amount, category, transaction_type):
        try:
            query = """UPDATE transactions 
                    SET date = %s, description = %s, amount = %s, category = %s, transaction_type = %s
                    WHERE id = %s AND user_id = %s"""
            self.cursor.execute(query, (date, description, amount, category, transaction_type, transaction_id, user_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to update transaction: {err}")
            return False

    def get_transaction(self, user_id, transaction_id):
        try:
            self.cursor.execute("SELECT * FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, user_id))
            return self.cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch transaction: {err}")
            return None

    def get_transactions(self, user_id, start_date=None, end_date=None, category=None, transaction_type=None, search_keyword=None):
        try:
            conditions = ["user_id = %s"]
            params = [user_id]
            
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
            
    def get_categories(self, user_id=None):
        try:
            # Use the passed user_id or fall back to self.user_id
            user_id_to_use = user_id if user_id is not None else self.user_id
            
            if user_id_to_use is None:
                messagebox.showerror("Error", "No user ID provided")
                return []
                
            self.cursor.execute("SELECT DISTINCT category FROM transactions WHERE user_id = %s", (user_id_to_use,))
            categories = [category[0] for category in self.cursor.fetchall() if category[0]]
            return categories
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch categories: {err}")
            return []
            
    def delete_transaction(self, user_id, transaction_id):
        try:
            self.cursor.execute("DELETE FROM transactions WHERE id = %s AND user_id = %s", (transaction_id, user_id))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to delete transaction: {err}")
            return False
    
    def add_budget(self, user_id, category, amount):
        try:
            query = """INSERT INTO budgets (user_id, category, amount) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE amount = %s"""
            self.cursor.execute(query, (user_id, category, amount, amount))
            self.conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to add budget: {err}")
            return False

    def get_budgets(self, user_id):
        try:
            self.cursor.execute("SELECT category, amount FROM budgets WHERE user_id = %s", (user_id,))
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch budgets: {err}")
            return []
            
    def get_monthly_spending_by_category(self, user_id, year=None, month=None):
        try:
            if year is None or month is None:
                today = datetime.today()
                year = today.year
                month = today.month
                
            query = """
                SELECT category, SUM(amount) as total
                FROM transactions 
                WHERE transaction_type = 'expense'
                AND user_id = %s
                AND YEAR(date) = %s AND MONTH(date) = %s
                GROUP BY category
            """
            self.cursor.execute(query, (user_id, year, month))
            return {category: float(total) for category, total in self.cursor.fetchall()}
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to fetch monthly spending: {err}")
            return {}

    def check_budget_alerts(self, user_id):
        # Get all budgets
        budgets = {category: float(amount) for category, amount in self.get_budgets(user_id)}
        if not budgets:
            return []
            
        # Get current month's spending
        monthly_spending = self.get_monthly_spending_by_category(user_id)
        
        # Check which categories exceed budget
        alerts = []
        for category, budget in budgets.items():
            if category in monthly_spending and monthly_spending[category] > budget:
                alerts.append((category, budget, monthly_spending[category]))
                
        return alerts
        
    def delete_budget(self, user_id, category):
        try:
            query = "DELETE FROM budgets WHERE user_id = %s AND category = %s"
            self.cursor.execute(query, (user_id, category))
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