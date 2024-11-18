import psycopg2

# Retrieve userType, userID for a given email/password
def getUser(db_connection, email, passwordHash):
    # List of tables to check 
    tables = ['advisor', 'staff', 'instructor', 'student']
    try:
        with db_connection.cursor() as cursor:
            for table in tables:
                # Create the SQL query
                query = f"SELECT '{table}' as userType, {table}_id as userID FROM {table} WHERE email = %s AND password = %s"
                
                # Execute the query
                cursor.execute(query, (email, passwordHash))
                result = cursor.fetchone()

                # If a matching user is found, return the userType and userID
                if result:
                    print(f"Found {result}")
                    return result
        
        # If no matching user is found in any table, return None
        print("Not found")
        return None
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in db_operations.getUser: {e}")
        return None
    
