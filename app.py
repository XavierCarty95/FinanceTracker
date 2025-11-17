import tkinter as tk
from tkinter import messagebox

from FinanceDB import FinanceDB
from FinanceAuth import FinanceAuth

db = FinanceDB()
auth = FinanceAuth(db)


def handle_signup():
    email = email_entry_signup.get().strip()
    name = name_entry_signup.get().strip()
    password = password_entry_signup.get().strip()

    success, message = auth.signup(email, name, password)

    if success:
        messagebox.showinfo("Sign up success", message)
        # Clear fields after successful signup
        email_entry_signup.delete(0, tk.END)
        name_entry_signup.delete(0, tk.END)
        password_entry_signup.delete(0, tk.END)
    else:
        messagebox.showerror("Sign up failed", message)


def handle_login():
    """Handle login button click: read fields, call auth, show message."""
    email = email_entry_login.get().strip()
    password = password_entry_login.get().strip()

    success, message = auth.login(email, password)

    if success:
        messagebox.showinfo("Login success", message)
        # TODO: later open a dashboard window here
    else:
        messagebox.showerror("Login failed", message)


def on_close():
    """Close DB connection and destroy the main window."""
    try:
        db.close()
    except Exception:
        # If close fails for some reason, just ignore and quit
        pass
    root.destroy()

root = tk.Tk()
root.title("Finance Tracker - Login / Sign Up")
root.geometry("380x430")

# SIGN UP FRAME
signup_frame = tk.LabelFrame(root, text="Sign Up", padx=10, pady=10)
signup_frame.pack(pady=15, padx=15, fill="x")

tk.Label(signup_frame, text="Email").pack(anchor="w")
email_entry_signup = tk.Entry(signup_frame, width=30)
email_entry_signup.pack()

tk.Label(signup_frame, text="Name").pack(anchor="w")
name_entry_signup = tk.Entry(signup_frame, width=30)
name_entry_signup.pack()

tk.Label(signup_frame, text="Password").pack(anchor="w")
password_entry_signup = tk.Entry(signup_frame, width=30, show="*")
password_entry_signup.pack()

signup_button = tk.Button(signup_frame, text="Sign Up", command=handle_signup)
signup_button.pack(pady=10)

# LOGIN FRAME
login_frame = tk.LabelFrame(root, text="Login", padx=10, pady=10)
login_frame.pack(pady=15, padx=15, fill="x")

tk.Label(login_frame, text="Email").pack(anchor="w")
email_entry_login = tk.Entry(login_frame, width=30)
email_entry_login.pack()

tk.Label(login_frame, text="Password").pack(anchor="w")
password_entry_login = tk.Entry(login_frame, width=30, show="*")
password_entry_login.pack()

login_button = tk.Button(login_frame, text="Login", command=handle_login)
login_button.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()