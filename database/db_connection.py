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

try:
    conn = psycopg2.connect(database=db_name, 
                            user=db_user, 
                            host=db_host,
                            password=db_password,
                            port=db_port)
    print("Connection successful")
except psycopg2.Error as e:
    print(f"Error: Could not make connection to the database\n{e}")