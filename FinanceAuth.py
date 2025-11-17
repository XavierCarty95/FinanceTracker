import bcrypt
from  psycopg2.errors import UniqueViolation

class FinanceAuth:
    def __init__(self, db):
        self.db = db

    def signup(self, email, name, password):
        """
                Register a new user by inserting their email, name, and hashed password
                into the users table.

                :param email: User's email (must be unique)
                :type email: str
                :param name: User's display name
                :type name: str
                :param password: Plaintext password that will be hashed
                :type password: str
                :return: Tuple (success: bool, message: str)
                """

        #check if email and name doesn't exist yet
        if not email or not name or not password:
            return False, "All fields must be present"

        # Hash the password securely
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            # Insert user into the db
            self.db.execute(
            "INSERT INTO users (email, name, password_hash) VALUES (%s, %s, %s)",
            (email, name, hashed),
        )
        except UniqueViolation:
            #email exists
            self.db.rollback()
            return False, "Email exists"
        except Exception as e:
            #Any generic database error
            self.db.rollback()
            return False, f"Error: {e}"
        return True, "You are successfully signed up"

    def login(self, email, password):
        """
         Log in an existing user by verifying the provided password
         against the stored password hash in the database.

         :param email: User's email
         :type email: str
         :param password: Plaintext password to validate
         :type password: str
         :return: Tuple (success: bool, message: str)
         """

        # validate input
        if not email or not password:
            return False, "All fields must be present"

        # get the loggedin user
        self.db.execute(
            "SELECT password_hash FROM users WHERE email = %s",
            (email,)
        )

        row = self.db.fetchone()

        # can't find the email
        if not row:
            return False, "Email does not exist"
        stored_hash, name = row

        #compare password
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True, f"Welcome {name}!"
        else:
            return False, "Wrong password"