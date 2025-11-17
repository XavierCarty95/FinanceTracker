# FinanceTracker


FinanceTracker is a simple desktop application built using Python and Tkinter.  
It allows users to sign up and log in using a cloud-hosted PostgreSQL database  
(Neon). This app is the starting foundation for a full finance dashboard.

------------------------------------------------------------

## Features

- User Sign Up (email, name, password)
- User Login
- Secure password hashing with bcrypt
- PostgreSQL database connection
- Tkinter graphical user interface
- Environment variable support using .env
- Virtual environment recommended

------------------------------------------------------------

## Tech Stack

- Python 3.12+
- Tkinter GUI
- PostgreSQL (Neon)
- psycopg2-binary (database driver)
- bcrypt (password hashing)
- python-dotenv (environment variables)

------------------------------------------------------------

## Database Schema

Make sure your PostgreSQL database includes:

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

------------------------------------------------------------

## How to Run the Tkinter Application

Follow these steps to run FinanceTracker.

1. Clone the Repository

   git clone https://github.com/<your-username>/FinanceTracker.git
   cd FinanceTracker

2. Create a Virtual Environment

   On macOS/Linux:
       python3 -m venv venv
       source venv/bin/activate

   On Windows (PowerShell):
       python -m venv venv
       venv\Scripts\activate

3. Install Dependencies

   pip install python-dotenv psycopg2-binary bcrypt

4. Add Your .env File

   Create a file named ".env" in the project root containing:

   DB_URL=postgresql://username:password@host/database
   (*This will need to be provided by one of the contributors*)

5. Run the Application

   python app.py

A Tkinter window will appear with a Sign Up form and Login form.

------------------------------------------------------------

## Password Security

Passwords are hashed using:

bcrypt.hashpw(password.encode(), bcrypt.gensalt())

No plaintext passwords are stored in the database.

------------------------------------------------------------

## Common Issues

1. "No module named _tkinter"
   Install Python from python.org (not Homebrew) and select it in PyCharm.

2. "externally-managed-environment"
   Use a virtual environment (venv).

3. Login error: "not enough values to unpack"
   Ensure your query selects both fields:
   SELECT password_hash, name FROM users WHERE email = %s

------------------------------------------------------------

## Future Enhancements


------------------------------------------------------------

## Contributors

- Xavier Carty, Shree Shingre, Nikhil


------------------------------------------------------------

## License

This project is for educational and academic use.