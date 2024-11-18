import psycopg2
from models.student import Student
from models.advisor import Advisor
from models.instructor import Instructor
from models.staff import Staff

# Retrieve userType, userID for a given email/password
def getUser(db_connection, email, passwordHash):
    # List of tables to check 
    tables = ['advisor', 'staff', 'instructor', 'student']
    userType, userId = None, None
    
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
                    userType, userId = result
                    break
        
            # Not found 
            if (userType is None or userId is None):
                print("User not found")
                return None

            # Create object
            if (userType == "student"):
                query = "SELECT student_id as userId, email, first_name, last_name, gpa, total_credits, major_id FROM student WHERE student_id = %s"
                cursor.execute(query, (userId,))
                userId, email, first_name, last_name, gpa, total_credits, major_id = cursor.fetchone()
                student = Student(userId, email, first_name, last_name, gpa, total_credits, major_id)
                return student
                
            elif (userType == "instructor"):
                query = "SELECT instructor_id as userId, email, first_name, last_name, phone_number, hired_semester, hired_year, department_id FROM instructor WHERE instructor_id = %s"
                cursor.execute(query, (userId,))
                userId, email, first_name, last_name, phone_number, hired_semester, hired_year, department_id = cursor.fetchone()
                instructor = Instructor(userId, email, first_name, last_name, phone_number, hired_semester, hired_year, department_id)
                return instructor
                
            elif (userType == "advisor"):
                query = "SELECT advisor_id as userId, email, first_name, last_name, phone_number FROM advisor WHERE advisor_id = %s"
                cursor.execute(query, (userId,))
                userId, email, first_name, last_name, phone_number = cursor.fetchone()
                advisor = Advisor(userId, email, first_name, last_name, phone_number)
                return advisor
                
            elif (userType == "staff"):
                query = "SELECT staff_id as userId, email, first_name, last_name, phone_number, department_id FROM staff WHERE staff_id = %s"
                cursor.execute(query, (userId,))
                userId, email, first_name, last_name, phone_number, department_id = cursor.fetchone()
                staff = Staff(userId, email, first_name, last_name, phone_number, department_id)
                return staff
                
            else:
                print(f"Invalid user type: {userType}")
                return None
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in db_operations.getUser: {e}")
        return None


# Get grades for a student
def getGrades(db_connection, student_id):
    try:
        with db_connection.cursor() as cursor:
             # SQL query to fetch grades for the specific student
            query = """
            SELECT grade
            FROM student
            JOIN enrollment ON student.student_id = enrollment.student_id
            JOIN course ON enrollment.course_id = course.course_id
            WHERE student.student_id = %s;
            """
            # Execute the query with the student_id as a parameter
            cursor.execute(query, (student_id,))
            
            # Only get letter grades
            grades = [grade[0] for grade in cursor.fetchall()]
            
            # Return the grades if any are found
            if grades:
                return grades
            else:
                print(f"No grades found for student_id {student_id}")
                return None
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in db_operations.getUser: {e}")
        return None
    
def updateGPA(db_connection, student_id, new_gpa):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to update the GPA in the student table
                update_query = """
                UPDATE student
                SET gpa = %s
                WHERE student_id = %s;
                """
                # Execute the update query
                cursor.execute(update_query, (new_gpa, student_id))
                
                # Commit the transaction
                db_connection.commit()
    
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in db_operations.getUser: {e}")
        return None

