import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_host = os.getenv('DB_HOST')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

def DatabaseConnection():
    try:
        # Establish a connection to the database
        connection = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        print("Database connection successful")
        return connection
    except Exception as error:
        print(f"Error connecting to database: {error}")
        return None