from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from PIL.Image import Resampling
from tkinter import messagebox
import mysql.connector
import re



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
        self.db_name = 'user_registration'
        
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
            font=('times new roman', 10, 'bold'),
            border=3,
            relief=RIDGE,
            fg=btn_fg,
            bg=btn_bg,
            activebackground=frame_bg,
            activeforeground=text_fg
        )
        lg_btn.place(x=170, y=490, width=220, height=20)

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

if __name__ == "__main__":
    root = Tk()
    app = signup(root)
    root.mainloop()
