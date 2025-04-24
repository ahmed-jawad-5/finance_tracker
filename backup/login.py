from tkinter import *
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from PIL.Image import Resampling
from tkinter import messagebox
import mysql.connector
import re
import os
import sys
from pathlib import Path

def main():
    root = Tk()
    app = window(root)
    root.mainloop()

class signup:
    def __init__(self, root):
        self.root = root
        self.root.title("Signup")
        self.root.geometry('1920x1080')

        # Theme colors
        frame_bg = "#1e1e1e"
        text_fg = "#FFD700"
        entry_bg = "#2a2a2a"
        entry_fg = "white"
        btn_bg = "#000000"
        btn_fg = "#FFD700"

        # Database Configuration
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_password = 'Ahmed@1220'
        self.db_name = 'finance_tracker'  # Changed to finance_tracker for unified database
        
        # Initialize database
        self.initialize_database()

        # Variables
        self.var_fname = StringVar()
        self.var_lname = StringVar()
        self.var_contact = StringVar()
        self.var_email = StringVar()
        self.var_securityQ = StringVar()
        self.var_SecurityA = StringVar()
        self.var_pass = StringVar()
        self.var_confpass = StringVar()
        self.terms_var = IntVar()
    
        # Background
        try:
            self.bg = ImageTk.PhotoImage(file="E:/program to warr gya/codes/python/python_projects/tkinter/background.jpg")
            bg_lbl = Label(self.root, image=self.bg)
            bg_lbl.place(x=0, y=0)
        except Exception as e:
            bg_lbl = Label(self.root, bg="#333333")
            bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        frame = Frame(self.root, bg=frame_bg)
        frame.place(x=350, y=50, height=650, width=600)

        reg_lbl = Label(frame, text="Signup", font=('times new roman', 22, 'bold'), bg=frame_bg, fg=text_fg)
        reg_lbl.place(x=240, y=20)

        # First Name
        f_lbl = Label(frame, text="First Name", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        f_lbl.place(x=30, y=100)
        self.f_entr = Entry(frame, textvariable=self.var_fname, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.f_entr.place(x=30, y=130, width=200)

        # Last Name
        l_lbl = Label(frame, text="Last Name", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        l_lbl.place(x=290, y=100)
        self.l_entr = Entry(frame, textvariable=self.var_lname, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.l_entr.place(x=290, y=130, width=200)

        # Email
        em_lbl = Label(frame, text="Email", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        em_lbl.place(x=30, y=180)
        self.em_entr = Entry(frame, textvariable=self.var_email, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.em_entr.place(x=30, y=210, width=200)

        # Contact
        c_lbl = Label(frame, text="Contact", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        c_lbl.place(x=290, y=180)
        self.c_entr = Entry(frame, textvariable=self.var_contact, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.c_entr.place(x=290, y=210, width=200)

        # Security Question
        t_lbl = Label(frame, text="Question Type", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        t_lbl.place(x=30, y=250)
        self.q_comb = ttk.Combobox(frame, font=('times new roman', 14), textvariable=self.var_securityQ, state='readonly')
        self.q_comb['values'] = ('Select', 'Birthday', "Friend's name", "Aniversary Date", "Fav Day")
        self.q_comb.place(x=30, y=280, width=200)
        self.q_comb.current(0)

        # Answer
        q_lbl = Label(frame, text="Answer", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        q_lbl.place(x=290, y=250)
        self.q_entr = Entry(frame, font=('times new roman', 14), textvariable=self.var_SecurityA, bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.q_entr.place(x=290, y=280, width=200)

        # Password
        p_lbl = Label(frame, text="Password", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        p_lbl.place(x=30, y=320)
        self.p_entr = Entry(frame, font=('times new roman', 14), textvariable=self.var_pass, bg=entry_bg, fg=entry_fg, insertbackground='white', show="*")
        self.p_entr.place(x=30, y=350, width=200)

        # Confirm Password
        cp_lbl = Label(frame, text="Confirm password", font=('times new roman', 16), bg=frame_bg, fg=text_fg)
        cp_lbl.place(x=290, y=320)
        self.cp_entr = Entry(frame, font=('times new roman', 14), textvariable=self.var_confpass, bg=entry_bg, fg=entry_fg, insertbackground='white', show="*")
        self.cp_entr.place(x=290, y=350, width=200)

        # Terms Checkbox
        terms = Checkbutton(
            frame,
            text="I agree to the terms and condition",
            variable=self.terms_var,
            onvalue=1,
            offvalue=0,
            font=('times new roman', 14),
            bg=frame_bg,
            fg=text_fg,
            activebackground=frame_bg,
            activeforeground=text_fg,
            selectcolor=entry_bg
        )
        terms.place(x=20, y=380)

        # Signup Button
        sign_Button = Button(
            frame,
            text='Signup',
            command=self.register_user,
            font=('times new roman', 14, 'bold'),
            border=3,
            relief=RIDGE,
            fg=btn_fg,
            bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        sign_Button.place(x=230, y=430, width=150, height=40)

        # Login Button
        lg_btn = Button(
            frame,
            text='Already have an account? Login',
            command=self.open_login,
            font=('times new roman', 10, 'bold'),
            border=3,
            relief=RIDGE,
            fg=btn_fg,
            bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        lg_btn.place(x=170, y=490, width=220, height=20)

    def open_login(self):
        self.root.destroy()
        win = Tk()
        window(win)
        win.mainloop()

    def get_connection(self):
        configs = [
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password},
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password, 'auth_plugin': 'caching_sha2_password'},
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password, 'auth_plugin': 'mysql_native_password'},
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password, 'use_pure': True}
        ]
        last_error = None
        for config in configs:
            try:
                return mysql.connector.connect(**config)
            except mysql.connector.Error as err:
                last_error = err
        raise last_error

    def initialize_database(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_name}")
            conn.commit()
            cursor.close()
            conn.close()

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {self.db_name}")
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50),
                    email VARCHAR(100) UNIQUE NOT NULL,
                    contact VARCHAR(20),
                    security_question VARCHAR(100) NOT NULL,
                    security_answer VARCHAR(100) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create transactions table with user_id foreign key
            cursor.execute('''
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
            ''')
            
            # Create budgets table with user_id foreign key
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    UNIQUE KEY (user_id, category),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to initialize database: {err}")
            if "Access denied" in str(err):
                messagebox.showinfo("Suggestion", "Please verify your MySQL username and password")
            elif "Can't connect" in str(err):
                messagebox.showinfo("Suggestion", "Please verify that MySQL server is running")
            elif "Authentication plugin" in str(err):
                messagebox.showinfo("Suggestion", 
                    "Please run the following SQL command in MySQL:\n\n" +
                    "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'your_password';\n" +
                    "FLUSH PRIVILEGES;"
                )

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        return True, "Password is strong"

    def email_exists(self, email):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {self.db_name}")
            cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
            count = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return count > 0
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to check email: {err}")
            return False

    def register_user(self):
        if (self.var_fname.get() == "" or self.var_email.get() == "" or 
            self.var_securityQ.get().lower() == "select" or self.var_SecurityA.get() == ''):
            messagebox.showerror("Error", "Please fill all the necessary fields")
            return
        if not self.validate_email(self.var_email.get()):
            messagebox.showerror("Error", "Please enter a valid email address")
            return
        if self.email_exists(self.var_email.get()):
            messagebox.showerror("Error", "Email address already registered")
            return
        if self.var_pass.get() != self.var_confpass.get():
            messagebox.showerror("Error", "Confirm password should match the password field")
            return
        is_valid, message = self.validate_password(self.var_pass.get())
        if not is_valid:
            messagebox.showerror("Error", message)
            return
        if self.terms_var.get() == 0:
            messagebox.showerror('Error', 'You must agree to the terms and conditions')
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {self.db_name}")
            cursor.execute("""
                INSERT INTO users 
                (first_name, last_name, email, contact, security_question, security_answer, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                self.var_fname.get(),
                self.var_lname.get(),
                self.var_email.get(),
                self.var_contact.get(),
                self.var_securityQ.get(),
                self.var_SecurityA.get(),
                self.var_pass.get()
            ))
            conn.commit()
            cursor.close()
            conn.close()
            messagebox.showinfo('Success', 'Your account has been registered successfully!')
            self.clear_fields()
            # Redirect to login page
            self.open_login()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to register user: {err}")

    def clear_fields(self):
        self.var_fname.set("")
        self.var_lname.set("")
        self.var_email.set("")
        self.var_contact.set("")
        self.var_securityQ.set("Select")
        self.var_SecurityA.set("")
        self.var_pass.set("")
        self.var_confpass.set("")
        self.terms_var.set(0)

class window:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("1920x1080")

        # MySQL Config
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_password = 'Ahmed@1220'
        self.db_name = 'finance_tracker'  # Changed to match finance_tracker database

        # Theme colors
        frame_bg = "#1e1e1e"       
        text_fg = "#FFD700"        
        entry_bg = "#2a2a2a"       
        entry_fg = "white"
        btn_bg = "#000000"
        btn_fg = "#FFD700"

        # Background image
        try:
            self.bg = ImageTk.PhotoImage(file="E:/program to warr gya/codes/python/python_projects/tkinter/background.jpg")
            lbl = Label(self.root, image=self.bg)
            lbl.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            # Fallback for image failure
            lbl = Label(self.root, bg="#333333")
            lbl.place(x=0, y=0, relwidth=1, relheight=1)

        frame = Frame(self.root, bg=frame_bg)
        frame.place(x=500, y=130, width=340, height=450)

        try:
            img1 = Image.open("E:/program to warr gya/codes/python/python_projects/tkinter/user.png")
            img1 = img1.resize((100, 100), Resampling.LANCZOS)
            self.photoimg1 = ImageTk.PhotoImage(img1)
            self.label_img1 = Label(image=self.photoimg1, bg=frame_bg, borderwidth=0)
            self.label_img1.place(x=630, y=140, width=100, height=100)
        except Exception as e:
            pass

        log_text = Label(frame, text="Login", font=('times new roman', 20, 'bold'), fg=text_fg, bg=frame_bg)
        log_text.place(x=140, y=110)

        username = Label(frame, text='Username', font=('times new roman', 14, 'bold'), fg=text_fg, bg=frame_bg)
        username.place(x=60, y=160)

        self.user = Entry(frame, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, insertbackground='white')
        self.user.place(x=20, y=190, width=300)

        password = Label(frame, text='Password', font=('times new roman', 14, 'bold'), fg=text_fg, bg=frame_bg)
        password.place(x=60, y=260)

        self.passw = Entry(frame, font=('times new roman', 14), bg=entry_bg, fg=entry_fg, show='*', insertbackground='white')
        self.passw.place(x=20, y=290, width=300)

        try:
            img2 = Image.open("E:/program to warr gya/codes/python/python_projects/tkinter/useric.png")
            img2 = img2.resize((48, 48), Resampling.LANCZOS)
            self.photoimg2 = ImageTk.PhotoImage(img2)
            self.label_img2 = Label(image=self.photoimg2, bg=frame_bg, borderwidth=0)
            self.label_img2.place(x=510, y=270, width=50, height=50)
        except Exception as e:
            pass

        try:
            img3 = Image.open("E:/program to warr gya/codes/python/python_projects/tkinter/pass.png")
            img3 = img3.resize((48, 48), Resampling.LANCZOS)
            self.photoimg3 = ImageTk.PhotoImage(img3)
            self.label_img3 = Label(image=self.photoimg3, bg=frame_bg, borderwidth=0)
            self.label_img3.place(x=510, y=370, width=50, height=50)
        except Exception as e:
            pass

        login_Button = Button(
            frame, text='Login', 
            command=self.login,
            font=('times new roman', 14, 'bold'),
            border=3, relief=RIDGE,
            fg=btn_fg, bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        login_Button.place(x=60, y=350, width=200, height=40)

        signup_Button = Button(
            frame, text='Signup',
            command=self.open_signup,
            font=('times new roman', 10, 'bold'),
            border=3, relief=RIDGE,
            fg=btn_fg, bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        signup_Button.place(x=100, y=390, width=120, height=20)

        fogp_Button = Button(
            frame, text='Forget Password',
            command=self.forgot_password,
            font=('times new roman', 10, 'bold'),
            border=3, relief=RIDGE,
            fg=btn_fg, bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        fogp_Button.place(x=100, y=410, width=120, height=20)

    def open_signup(self):
        self.root.destroy()
        root = Tk()
        app = signup(root)
        root.mainloop()

    def forgot_password(self):
        # Create a new window for password recovery
        forgot_window = Toplevel(self.root)
        forgot_window.title("Password Recovery")
        forgot_window.geometry("400x300")
        forgot_window.resizable(False, False)
        
        # Theme colors
        frame_bg = "#1e1e1e"
        text_fg = "#FFD700"
        entry_bg = "#2a2a2a"
        entry_fg = "white"
        
        frame = Frame(forgot_window, bg=frame_bg)
        frame.pack(fill=BOTH, expand=True)
        
        Label(frame, text="Password Recovery", font=('times new roman', 16, 'bold'), 
              bg=frame_bg, fg=text_fg).pack(pady=20)
        
        Label(frame, text="Email:", font=('times new roman', 12), 
              bg=frame_bg, fg=text_fg).pack()
        email_entry = Entry(frame, font=('times new roman', 12), 
                          bg=entry_bg, fg=entry_fg, insertbackground='white')
        email_entry.pack(pady=5)
        
        Label(frame, text="Security Question:", font=('times new roman', 12), 
              bg=frame_bg, fg=text_fg).pack()
        
        security_q = ttk.Combobox(frame, font=('times new roman', 12), state='readonly')
        security_q['values'] = ('Select', 'Birthday', "Friend's name", "Aniversary Date", "Fav Day")
        security_q.current(0)
        security_q.pack(pady=5)
        
        Label(frame, text="Answer:", font=('times new roman', 12), 
              bg=frame_bg, fg=text_fg).pack()
        answer_entry = Entry(frame, font=('times new roman', 12), 
                           bg=entry_bg, fg=entry_fg, insertbackground='white')
        answer_entry.pack(pady=5)
        
        def recover_password():
            email = email_entry.get()
            question = security_q.get()
            answer = answer_entry.get()
            
            if not email or question == "Select" or not answer:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                cursor.execute(f"USE {self.db_name}")
                cursor.execute("""
                    SELECT password FROM users 
                    WHERE email = %s AND security_question = %s AND security_answer = %s
                """, (email, question, answer))
                
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    messagebox.showinfo("Password Recovery", 
                                      f"Your password is: {result[0]}")
                else:
                    messagebox.showerror("Error", "Invalid credentials or security question/answer")
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Failed to recover password: {err}")
        
        Button(frame, text="Recover Password", command=recover_password,
              font=('times new roman', 12), bg="#000000", fg="#FFD700").pack(pady=20)

    def get_connection(self):
        configs = [
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password},
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password, 'auth_plugin': 'mysql_native_password'},
            {'host': self.db_host, 'user': self.db_user, 'password': self.db_password, 'use_pure': True}
        ]
        last_error = None
        for config in configs:
            try:
                return mysql.connector.connect(**config)
            except mysql.connector.Error as err:
                last_error = err
        raise last_error

    # login.py
    def login(self):
        username = self.user.get().strip()
        password = self.passw.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "Username or password field can't be empty")
            return

        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(f"USE {self.db_name}")
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (username, password))
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()

            if user_data:
                messagebox.showinfo("Success", f"Welcome {user_data[1]}! Login complete")
                self.root.destroy()
                self.launch_finance_tracker(user_data[0])  # Pass user_id (first column in users table)
            else:
                messagebox.showerror("Error", "Invalid username or password")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to login: {err}")

    def launch_finance_tracker(self, user_id):
        try:
            import tkinter as tk
            from gui import FinanceTrackerApp
            
            root = tk.Tk()
            app = FinanceTrackerApp(root, user_id)  # Pass user_id to FinanceTrackerApp
            root.protocol("WM_DELETE_WINDOW", app.on_closing)
            root.mainloop()
        except ImportError:
            messagebox.showerror("Error", "Could not launch Finance Tracker")

if __name__ == "__main__":
    root = Tk()
    app = window(root)
    root.mainloop()