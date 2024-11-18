import hashlib
import os
from dotenv import load_dotenv
from database import db_operations as dbo
from database import db_connection as dbc

# Needed for salt env
load_dotenv()

class AuthenticationService:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def authenticate_user(self, email, password):
        salt = os.getenv('PWD_SALT')
        pwd = password+salt
        passwordHash = hashlib.sha256(pwd.encode())
        passwordHash = passwordHash.hexdigest()

        # Use db_operations.getUser to retrieve the user
        user = dbo.getUser(self.db_connection, email, passwordHash) # Just get password for now, since now accounts are saved with a hash

        # Will have to change this later so that we use the actual user models
        if len(user) == 2:
            print(f"User authenticated: {user}")
            return user
        else:
            print("Authentication failed.")
            return None