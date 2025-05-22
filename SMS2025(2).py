import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
from datetime import datetime
import uuid
import shutil
import os

# Database Setup
def init_db():
    conn = sqlite3.connect('school_management.db')
    c = conn.cursor()
    
    # Users table with role
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 username TEXT PRIMARY KEY,
                 password TEXT,
                 role TEXT)''')
    
    # Students table
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                 student_id TEXT PRIMARY KEY,
                 name TEXT,
                 class TEXT,
                 hostel_status TEXT,
                 bus_status TEXT,
                 created_at TEXT)''')
    
    # Hostelers table
    c.execute('''CREATE TABLE IF NOT EXISTS hostelers (
                 hosteler_id TEXT PRIMARY KEY,
                 student_id TEXT,
                 room_number TEXT,
                 joining_date TEXT,
                 FOREIGN KEY(student_id) REFERENCES students(student_id))''')
    
    # Bus Holders table
    c.execute('''CREATE TABLE IF NOT EXISTS bus_holders (
                 bus_holder_id TEXT PRIMARY KEY,
                 student_id TEXT,
                 route_number TEXT,
                 pickup_point TEXT,
                 FOREIGN KEY(student_id) REFERENCES students(student_id))''')
    
    # Employees table
    c.execute('''CREATE TABLE IF NOT EXISTS employees (
                 employee_id TEXT PRIMARY KEY,
                 name TEXT,
                 designation TEXT,
                 salary REAL,
                 created_at TEXT)''')
    
    # Fee Transactions table
    c.execute('''CREATE TABLE IF NOT EXISTS fee_transactions (
                 transaction_id TEXT PRIMARY KEY,
                 student_id TEXT,
                 fee_type TEXT,
                 amount REAL,
                 payment_date TEXT,
                 FOREIGN KEY(student_id) REFERENCES students(student_id))''')
    
    # Salary Slips table
    c.execute('''CREATE TABLE IF NOT EXISTS salary_slips (
                 slip_id TEXT PRIMARY KEY,
                 employee_id TEXT,
                 month TEXT,
                 amount REAL,
                 issued_date TEXT,
                 FOREIGN KEY(employee_id) REFERENCES employees(employee_id))''')
    
    # Report Cards table
    c.execute('''CREATE TABLE IF NOT EXISTS report_cards (
                 report_id TEXT PRIMARY KEY,
                 student_id TEXT,
                 subject TEXT,
                 marks INTEGER,
                 created_at TEXT,
                 FOREIGN KEY(student_id) REFERENCES students(student_id))''')
    
    # System Logs table
    c.execute('''CREATE TABLE IF NOT EXISTS system_logs (
                 log_id TEXT PRIMARY KEY,
                 action TEXT,
                 username TEXT,
                 timestamp TEXT)''')
    
    # Fees table
    c.execute('''CREATE TABLE IF NOT EXISTS fees (
                 class TEXT PRIMARY KEY,
                 amount REAL)''')
    
    # Default admin user
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
              ('admin', 'admin', 'admin'))
    
    # Sample fees data
    c.execute("INSERT OR IGNORE INTO fees (class, amount) VALUES (?, ?)", ('Class 10', 5000.0))
    c.execute("INSERT OR IGNORE INTO fees (class, amount) VALUES (?, ?)", ('Class 11', 6000.0))
    
    conn.commit()
    conn.close()

# Log Action
def log_action(action, username):
    conn = sqlite3.connect('school_management.db')
    c = conn.cursor()
    log_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO system_logs (log_id, action, username, timestamp) VALUES (?, ?, ?, ?)",
              (log_id, action, username, timestamp))
    conn.commit()
    conn.close()

# Main Application
class SchoolManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("School Management System")
        self.root.geometry("1000x700")  # Increased window size
        self.current_user = None
        self.current_role = None
        self.current_student_id = None
        init_db()
        self.show_login_screen()

    # Navigation helpers
    def go_back_to_login(self):
        self.current_user = None
        self.current_role = None
        self.show_login_screen()

    def go_back_to_main_menu(self):
        self.show_main_menu()

    def confirm_logout(self):
        if messagebox.askyesno("Confirm Logout", "Are you sure you want to logout?"):
            self.show_login_screen()

    def show_login_screen(self):
        self.clear_screen()
        
        tk.Label(self.root, text="School Management System", font=("Arial", 20)).pack(pady=20)
        
        tk.Label(self.root, text="User Type").pack()
        self.user_type = ttk.Combobox(self.root, values=["Admin", "Student"], state="readonly")
        self.user_type.current(0)
        self.user_type.pack(pady=5)
        
        tk.Label(self.root, text="Username").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack(pady=5)
        
        tk.Label(self.root, text="Password").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.validate_login, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.root.destroy, font=("Arial", 12)).pack(pady=5)

    def validate_login(self):
        user_type = self.user_type.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not all([username, password]):
            messagebox.showerror("Error", "Username and password are required")
            return
        
        if user_type == "Student":
            self.student_login(username, password)
        else:
            conn = sqlite3.connect('school_management.db')
            c = conn.cursor()
            c.execute("SELECT username, password, role FROM users WHERE username=? AND password=? AND role=?",
                      (username, password, 'admin'))
            user = c.fetchone()
            conn.close()
            
            if user:
                self.current_user = username
                self.current_role = 'admin'
                log_action("Admin logged in", username)
                self.show_main_menu()
            else:
                messagebox.showerror("Error", "Invalid admin username or password")

    def student_login(self, username, password):
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT username, password, role FROM users WHERE username=? AND password=? AND role=?",
                  (username, password, 'student'))
        user = c.fetchone()
        conn.close()
        
        if user:
            self.current_user = username
            self.current_role = 'student'
            # Extract student_id from username
            student_id_prefix = username.replace("student", "")
            conn = sqlite3.connect('school_management.db')
            c = conn.cursor()
            c.execute("SELECT student_id FROM students WHERE student_id LIKE ?",
                      (f"%{student_id_prefix}%",))
            student = c.fetchone()
            conn.close()
            
            if student:
                self.current_student_id = student[0]
                log_action("Student logged in", username)
                self.show_student_dashboard()
            else:
                messagebox.showerror("Error", "Student ID not found")
        else:
            messagebox.showerror("Error", "Invalid student username or password")

    def show_student_dashboard(self):
        self.clear_screen()
        
        tk.Label(self.root, text=f"Welcome, {self.current_user}", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Logout", command=self.confirm_logout, 
                  font=("Arial", 14, "bold"), bg="red", fg="white", padx=10, pady=10).pack(pady=10)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=10, fill="both", expand=True)
        
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")
        self.show_results(results_frame)
        
        fee_frame = ttk.Frame(notebook)
        notebook.add(fee_frame, text="Tuition Fee")
        self.show_tuition_fee(fee_frame)

    def show_results(self, frame):
        tree = ttk.Treeview(frame, columns=("Subject", "Marks"), show="headings")
        tree.heading("Subject", text="Subject")
        tree.heading("Marks", text="Marks")
        tree.pack(pady=10, fill="both", expand=True)
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT subject, marks FROM report_cards WHERE student_id=?", (self.current_student_id,))
        results = c.fetchall()
        conn.close()
        
        if results:
            for result in results:
                tree.insert("", "end", values=(result[0], result[1]))
        else:
            tk.Label(frame, text="No results available", font=("Arial", 12), fg="red").pack(pady=10)

    def show_tuition_fee(self, frame):
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT class FROM students WHERE student_id=?", (self.current_student_id,))
        student_class = c.fetchone()
        
        if student_class:
            c.execute("SELECT amount FROM fees WHERE class=?", (student_class[0],))
            fee = c.fetchone()
            
            if fee:
                tk.Label(frame, text=f"Tuition Fee for {student_class[0]}: ${fee[0]}", 
                         font=("Arial", 14)).pack(pady=20)
            else:
                tk.Label(frame, text="Fee not set", font=("Arial", 12), fg="red").pack(pady=20)
        else:
            tk.Label(frame, text="Student class not found", font=("Arial", 12), fg="red").pack(pady=20)
        
        conn.close()

    def show_main_menu(self):
        self.clear_screen()
        
        # Create a canvas with a scrollbar
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add widgets to the scrollable frame
        tk.Label(scrollable_frame, text="Admin Panel", font=("Arial", 20)).pack(pady=20)
        tk.Button(scrollable_frame, text="Logout", command=self.confirm_logout, 
                  font=("Arial", 14, "bold"), bg="red", fg="white", padx=10, pady=10).pack(pady=10)
        tk.Button(scrollable_frame, text="Add Student", command=self.show_add_student, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Add Hosteler", command=self.show_add_hosteler, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Add Bus Holder", command=self.show_add_bus_holder, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Add Employee", command=self.show_add_employee, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Record Fee Payment", command=self.show_fee_payment, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Generate Salary Slip", command=self.show_salary_slip, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Generate Report Card", command=self.show_report_card, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Search Students", command=self.show_search_students, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Generate No Dues", command=self.show_no_dues, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Change Password", command=self.show_change_password, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Backup Database", command=self.backup_database, font=("Arial", 12)).pack(pady=10)
        tk.Button(scrollable_frame, text="Restore Database", command=self.restore_database, font=("Arial", 12)).pack(pady=10)

    def show_add_student(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Add Student", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Name").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        
        tk.Label(self.root, text="Class").pack()
        self.class_entry = tk.Entry(self.root)
        self.class_entry.pack(pady=5)
        
        tk.Label(self.root, text="Hostel (Yes/No)").pack()
        self.hostel_entry = tk.Entry(self.root)
        self.hostel_entry.pack(pady=5)
        
        tk.Label(self.root, text="Bus (Yes/No)").pack()
        self.bus_entry = tk.Entry(self.root)
        self.bus_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save", command=self.save_student, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_student(self):
        name = self.name_entry.get()
        class_ = self.class_entry.get()
        hostel = self.hostel_entry.get()
        bus = self.bus_entry.get()
        
        if not all([name, class_, hostel, bus]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        student_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        username = f"student{student_id[:8]}"
        password = student_id[:8]
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (student_id, name, class, hostel_status, bus_status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (student_id, name, class_, hostel, bus, created_at))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  (username, password, 'student'))
        conn.commit()
        conn.close()
        
        log_action(f"Added student: {name}", self.current_user)
        messagebox.showinfo("Success", f"Student added successfully.\nUsername: {username}\nPassword: {password}")
        self.show_main_menu()

    def show_add_hosteler(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Add Hosteler", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Student ID").pack()
        self.hostel_student_id_entry = tk.Entry(self.root)
        self.hostel_student_id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Room Number").pack()
        self.room_number_entry = tk.Entry(self.root)
        self.room_number_entry.pack(pady=5)
        
        tk.Label(self.root, text="Joining Date (YYYY-MM-DD)").pack()
        self.joining_date_entry = tk.Entry(self.root)
        self.joining_date_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save", command=self.save_hosteler, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_hosteler(self):
        student_id = self.hostel_student_id_entry.get()
        room_number = self.room_number_entry.get()
        joining_date = self.joining_date_entry.get()
        
        if not all([student_id, room_number, joining_date]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=? AND hostel_status='Yes'", (student_id,))
        student = c.fetchone()
        
        if not student:
            messagebox.showerror("Error", "Student not found or not a hosteler")
            conn.close()
            return
        
        hosteler_id = str(uuid.uuid4())
        c.execute("INSERT INTO hostelers (hosteler_id, student_id, room_number, joining_date) VALUES (?, ?, ?, ?)",
                  (hosteler_id, student_id, room_number, joining_date))
        conn.commit()
        conn.close()
        
        log_action(f"Added hosteler: {student_id}", self.current_user)
        messagebox.showinfo("Success", "Hosteler added successfully")
        self.show_main_menu()

    def show_add_bus_holder(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Add Bus Holder", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Student ID").pack()
        self.bus_student_id_entry = tk.Entry(self.root)
        self.bus_student_id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Route Number").pack()
        self.route_number_entry = tk.Entry(self.root)
        self.route_number_entry.pack(pady=5)
        
        tk.Label(self.root, text="Pickup Point").pack()
        self.pickup_point_entry = tk.Entry(self.root)
        self.pickup_point_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save", command=self.save_bus_holder, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_bus_holder(self):
        student_id = self.bus_student_id_entry.get()
        route_number = self.route_number_entry.get()
        pickup_point = self.pickup_point_entry.get()
        
        if not all([student_id, route_number, pickup_point]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=? AND bus_status='Yes'", (student_id,))
        student = c.fetchone()
        
        if not student:
            messagebox.showerror("Error", "Student not found or not a bus holder")
            conn.close()
            return
        
        bus_holder_id = str(uuid.uuid4())
        c.execute("INSERT INTO bus_holders (bus_holder_id, student_id, route_number, pickup_point) VALUES (?, ?, ?, ?)",
                  (bus_holder_id, student_id, route_number, pickup_point))
        conn.commit()
        conn.close()
        
        log_action(f"Added bus holder: {student_id}", self.current_user)
        messagebox.showinfo("Success", "Bus holder added successfully")
        self.show_main_menu()

    def show_add_employee(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Add Employee", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Name").pack()
        self.emp_name_entry = tk.Entry(self.root)
        self.emp_name_entry.pack(pady=5)
        
        tk.Label(self.root, text="Designation").pack()
        self.designation_entry = tk.Entry(self.root)
        self.designation_entry.pack(pady=5)
        
        tk.Label(self.root, text="Salary").pack()
        self.salary_entry = tk.Entry(self.root)
        self.salary_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save", command=self.save_employee, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_employee(self):
        name = self.emp_name_entry.get()
        designation = self.designation_entry.get()
        salary = self.salary_entry.get()
        
        if not all([name, designation, salary]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            salary = float(salary)
        except ValueError:
            messagebox.showerror("Error", "Invalid salary amount")
            return
        
        employee_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("INSERT INTO employees (employee_id, name, designation, salary, created_at) VALUES (?, ?, ?, ?, ?)",
                  (employee_id, name, designation, salary, created_at))
        conn.commit()
        conn.close()
        
        log_action(f"Added employee: {name}", self.current_user)
        messagebox.showinfo("Success", "Employee added successfully")
        self.show_main_menu()

    def show_fee_payment(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Record Fee Payment", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Student ID").pack()
        self.student_id_entry = tk.Entry(self.root)
        self.student_id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Fee Type (Class/Hostel/Bus)").pack()
        self.fee_type_entry = tk.Entry(self.root)
        self.fee_type_entry.pack(pady=5)
        
        tk.Label(self.root, text="Amount").pack()
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save Payment", command=self.save_fee_payment, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_fee_payment(self):
        student_id = self.student_id_entry.get()
        fee_type = self.fee_type_entry.get()
        amount = self.amount_entry.get()
        
        if not all([student_id, fee_type, amount]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        student = c.fetchone()
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            conn.close()
            return
        
        transaction_id = str(uuid.uuid4())
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT INTO fee_transactions (transaction_id, student_id, fee_type, amount, payment_date) VALUES (?, ?, ?, ?, ?)",
                  (transaction_id, student_id, fee_type, amount, payment_date))
        conn.commit()
        conn.close()
        
        log_action(f"Recorded payment for student: {student_id}", self.current_user)
        messagebox.showinfo("Success", f"Payment recorded. Transaction ID: {transaction_id}")
        self.show_main_menu()

    def show_salary_slip(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Generate Salary Slip", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Employee ID").pack()
        self.employee_id_entry = tk.Entry(self.root)
        self.employee_id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Month (e.g., 2025-04)").pack()
        self.month_entry = tk.Entry(self.root)
        self.month_entry.pack(pady=5)
        
        tk.Label(self.root, text="Amount").pack()
        self.salary_amount_entry = tk.Entry(self.root)
        self.salary_amount_entry.pack(pady=5)
        
        tk.Button(self.root, text="Generate Slip", command=self.save_salary_slip, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_salary_slip(self):
        employee_id = self.employee_id_entry.get()
        month = self.month_entry.get()
        amount = self.salary_amount_entry.get()
        
        if not all([employee_id, month, amount]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Invalid amount")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM employees WHERE employee_id=?", (employee_id,))
        employee = c.fetchone()
        
        if not employee:
            messagebox.showerror("Error", "Employee not found")
            conn.close()
            return
        
        slip_id = str(uuid.uuid4())
        issued_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT INTO salary_slips (slip_id, employee_id, month, amount, issued_date) VALUES (?, ?, ?, ?, ?)",
                  (slip_id, employee_id, month, amount, issued_date))
        conn.commit()
        conn.close()
        
        log_action(f"Generated salary slip for employee: {employee_id}", self.current_user)
        messagebox.showinfo("Success", f"Salary slip generated. Slip ID: {slip_id}")
        self.show_main_menu()

    def show_report_card(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Generate Report Card", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Student ID").pack()
        self.report_student_id_entry = tk.Entry(self.root)
        self.report_student_id_entry.pack(pady=5)
        
        tk.Label(self.root, text="Subject").pack()
        self.subject_entry = tk.Entry(self.root)
        self.subject_entry.pack(pady=5)
        
        tk.Label(self.root, text="Marks").pack()
        self.marks_entry = tk.Entry(self.root)
        self.marks_entry.pack(pady=5)
        
        tk.Button(self.root, text="Save Marks", command=self.save_report_card, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def save_report_card(self):
        student_id = self.report_student_id_entry.get()
        subject = self.subject_entry.get()
        marks = self.marks_entry.get()
        
        if not all([student_id, subject, marks]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            marks = int(marks)
            if marks < 0 or marks > 100:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Marks must be a number between 0 and 100")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        student = c.fetchone()
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            conn.close()
            return
        
        report_id = str(uuid.uuid4())
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute("INSERT INTO report_cards (report_id, student_id, subject, marks, created_at) VALUES (?, ?, ?, ?, ?)",
                  (report_id, student_id, subject, marks, created_at))
        conn.commit()
        conn.close()
        
        log_action(f"Added report card for student: {student_id}", self.current_user)
        messagebox.showinfo("Success", "Report card entry added")
        self.show_main_menu()

    def show_search_students(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Search Students", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Search by Name or Class").pack()
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack(pady=5)
        
        tk.Button(self.root, text="Search", command=self.perform_search, font=("Arial", 12)).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)
        
        self.tree = ttk.Treeview(self.root, columns=("ID", "Name", "Class", "Hostel", "Bus"), show="headings")
        self.tree.heading("ID", text="Student ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Class", text="Class")
        self.tree.heading("Hostel", text="Hostel")
        self.tree.heading("Bus", text="Bus")
        self.tree.pack(pady=10, fill="both", expand=True)

    def perform_search(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        search_term = self.search_entry.get().strip()
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        query = "SELECT * FROM students WHERE name LIKE ? OR class LIKE ?"
        c.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        students = c.fetchall()
        conn.close()
        
        for student in students:
            self.tree.insert("", "end", values=(student[0], student[1], student[2], student[3], student[4]))
        
        log_action(f"Searched students with term: {search_term}", self.current_user)

    def show_no_dues(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Generate No Dues Document", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Student ID").pack()
        self.no_dues_student_id_entry = tk.Entry(self.root)
        self.no_dues_student_id_entry.pack(pady=5)
        
        tk.Button(self.root, text="Generate", command=self.generate_no_dues, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def generate_no_dues(self):
        student_id = self.no_dues_student_id_entry.get()
        
        if not student_id:
            messagebox.showerror("Error", "Student ID is required")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
        student = c.fetchone()
        
        if not student:
            messagebox.showerror("Error", "Student not found")
            conn.close()
            return
        
        c.execute("SELECT SUM(amount) FROM fee_transactions WHERE student_id=?", (student_id,))
        total_paid = c.fetchone()[0] or 0
        has_dues = total_paid < 10000
        
        conn.close()
        
        if has_dues:
            messagebox.showerror("Error", "Student has pending dues")
            return
        
        no_dues_content = (
            f"No Dues Certificate\n"
            f"Student ID: {student_id}\n"
            f"Name: {student[1]}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d')}\n"
            "This certifies that the student has no pending dues."
        )
        
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as f:
                f.write(no_dues_content)
            log_action(f"Generated no dues for student: {student_id}", self.current_user)
            messagebox.showinfo("Success", "No dues document generated")
        
        self.show_main_menu()

    def show_change_password(self):
        self.clear_screen()
        
        tk.Label(self.root, text="Change Password", font=("Arial", 16)).pack(pady=20)
        
        tk.Label(self.root, text="Current Password").pack()
        self.current_password_entry = tk.Entry(self.root, show="*")
        self.current_password_entry.pack(pady=5)
        
        tk.Label(self.root, text="New Password").pack()
        self.new_password_entry = tk.Entry(self.root, show="*")
        self.new_password_entry.pack(pady=5)
        
        tk.Label(self.root, text="Confirm New Password").pack()
        self.confirm_password_entry = tk.Entry(self.root, show="*")
        self.confirm_password_entry.pack(pady=5)
        
        tk.Button(self.root, text="Change Password", command=self.change_password, font=("Arial", 12)).pack(pady=20)
        tk.Button(self.root, text="Back", command=self.go_back_to_main_menu, font=("Arial", 12)).pack(pady=5)

    def change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        if not all([current_password, new_password, confirm_password]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        if new_password != confirm_password:
            messagebox.showerror("Error", "New passwords do not match")
            return
        
        conn = sqlite3.connect('school_management.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (self.current_user, current_password))
        user = c.fetchone()
        
        if not user:
            messagebox.showerror("Error", "Current password is incorrect")
            conn.close()
            return
        
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, self.current_user))
        conn.commit()
        conn.close()
        
        log_action("Changed password", self.current_user)
        messagebox.showinfo("Success", "Password changed successfully")
        self.show_main_menu()

    def backup_database(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("Database files", "*.db")])
        if file_path:
            try:
                shutil.copyfile('school_management.db', file_path)
                log_action("Database backed up", self.current_user)
                messagebox.showinfo("Success", "Database backed up successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")
        self.show_main_menu()

    def restore_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("Database files", "*.db")])
        if file_path:
            try:
                shutil.copyfile(file_path, 'school_management.db')
                log_action("Database restored", self.current_user)
                messagebox.showinfo("Success", "Database restored successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed: {str(e)}")
        self.show_main_menu()

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolManagementSystem(root)
    root.mainloop()