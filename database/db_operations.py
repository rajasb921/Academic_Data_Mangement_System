import psycopg2
from psycopg2.extras import RealDictCursor
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

# Update the GPA for a student
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

# Get course schedule for student
def getStudentCourseSchedule(db_connection, student_id):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to fetch the schedule grouped by semester for the given student ID
            query = """
            SELECT 
                e.student_id, 
                c.course_prefix || ' ' || c.course_number AS course_code, 
                c.title AS course_title, 
                c.credits, 
                c.days, 
                c.start_time, 
                c.semester,
                e.grade
            FROM 
                enrollment e
            JOIN 
                course c
            ON 
                e.course_id = c.course_id
            WHERE 
                e.student_id = %s
            ORDER BY 
                c.semester, c.start_time;
            """
            # Execute the query with the provided student_id
            cursor.execute(query, (student_id,))
            
            # Fetch all results
            results = cursor.fetchall()

            # Return the results as a list of dictionaries
            schedule = [
                {
                    "student_id": row[0],
                    "course_code": row[1],
                    "course_title": row[2],
                    "credits": row[3],
                    "days": row[4],
                    "start_time": row[5],
                    "semester": row[6],
                    "grade":row[7]
                }
                for row in results
            ]

            return schedule

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Get course schedule for instructor
def getInstructorCourseSchedule(db_connection, instructor_id):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to fetch the schedule grouped by semester for the given instructor ID
            query = """
            SELECT 
                c.instructor_id, 
                c.course_prefix || ' ' || c.course_number AS course_code, 
                c.title AS course_title, 
                c.credits, 
                c.days, 
                c.start_time, 
                c.end_time, 
                c.semester, 
                c.year, 
                c.section_id,
                c.course_id
            FROM 
                course c
            WHERE 
                c.instructor_id = %s
            ORDER BY 
                c.year, c.semester, c.start_time;
            """
            # Execute the query with the provided instructor_id
            cursor.execute(query, (instructor_id,))
            
            # Fetch all results
            results = cursor.fetchall()

            # Return the results as a list of dictionaries
            schedule = [
                {
                    "instructor_id": row[0],
                    "course_code": row[1],
                    "course_title": row[2],
                    "credits": row[3],
                    "days": row[4],
                    "start_time": row[5],
                    "end_time": row[6],
                    "semester": row[7],
                    "year": row[8],
                    "section_id": row[9],
                    "course_id":row[10]
                }
                for row in results
            ]

            return schedule

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Get performance of students in a specific course
def getPerformance(db_connection, course_id):
    try:
        with db_connection.cursor() as cursor:
            # Define the SQL query
            query = """
                SELECT 
                    c.course_prefix || c.course_number AS course,
                    COUNT(e.student_id) AS num_students,
                    AVG(CASE 
                            WHEN e.grade = 'A' THEN 4
                            WHEN e.grade = 'B' THEN 3
                            WHEN e.grade = 'C' THEN 2
                            WHEN e.grade = 'D' THEN 1
                            WHEN e.grade = 'F' THEN 0
                            ELSE NULL 
                        END) AS avg_grade,
                    SUM(CASE WHEN e.grade = 'A' THEN 1 ELSE 0 END) AS num_A,
                    SUM(CASE WHEN e.grade = 'B' THEN 1 ELSE 0 END) AS num_B,
                    SUM(CASE WHEN e.grade = 'C' THEN 1 ELSE 0 END) AS num_C,
                    SUM(CASE WHEN e.grade = 'D' THEN 1 ELSE 0 END) AS num_D,
                    SUM(CASE WHEN e.grade = 'F' THEN 1 ELSE 0 END) AS num_F
                FROM 
                    public.course c
                JOIN 
                    public.enrollment e ON c.course_id = e.course_id
                WHERE
                    c.course_id = %s
                GROUP BY 
                    c.course_prefix, c.course_number
                ORDER BY 
                    c.course_prefix, c.course_number;
            """
            # Execute the query with the given course_id
            cursor.execute(query, (course_id,))
            result = cursor.fetchone()
            
            if result:
                # Process the results
                performance = {
                    "course": result[0],
                    "num_students": result[1],
                    "avg_grade": result[2],
                    "num_A": result[3],
                    "num_B": result[4],
                    "num_C": result[5],
                    "num_D": result[6],
                    "num_F": result[7]
                }
                return performance
            else:
                print("No performance data found for the given course ID.")
                return None

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Get major distribution
def getMajorDistribution(db_connection, course_id):
    try:
        with db_connection.cursor() as cursor:
            # Define the SQL query to get major distribution
            query = """
                SELECT 
                    m.major_name,
                    COUNT(e.student_id) AS num_students,
                    ROUND(COUNT(e.student_id) * 100.0 / SUM(COUNT(e.student_id)) OVER (), 2) AS percentage
                FROM 
                    public.enrollment e
                JOIN 
                    public.student s ON e.student_id = s.student_id
                JOIN 
                    public.course c ON e.course_id = c.course_id
                JOIN 
                    public.major m ON s.major_id = m.major_id
                WHERE
                    c.course_id = %s
                GROUP BY 
                    m.major_name
                ORDER BY 
                    num_students DESC;
            """
            # Execute the query with the given course_id
            cursor.execute(query, (course_id,))
            results = cursor.fetchall()
            
            if results:
                # Process the results
                major_distribution = [
                    {
                        "major": result[0],
                        "num_students": result[1],
                        "percentage": result[2]
                    } for result in results
                ]
                return major_distribution
            else:
                print("No major distribution data found for the given course ID.")
                return None

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Student summary
def getStudentSummary(db_connection, student_id):
    try:
        with db_connection.cursor() as cursor:
            query = """
            SELECT 
                first_name || ' ' || last_name AS full_name,
                m.major_name AS major,
                s.total_credits AS completed_credits,
                s.gpa
            FROM 
                public.student s
            JOIN 
                public.major m ON s.major_id = m.major_id
            WHERE 
                s.student_id = %s
            """
            cursor.execute(query, (student_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'name': result[0],
                    'major': result[1],
                    'completed_credits': result[2],
                    'gpa': result[3]
                }
            else:
                return None

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Add a student to a course
def studentCourseAdd(db_connection, student_id, course_id):
    try:

        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get the credits for the course
            cursor.execute("""
                SELECT credits
                FROM course
                WHERE course_id = %s
            """, (course_id,))
            course = cursor.fetchone()
            
            if not course:
                print("Course not found")
                return False
            
            course_credits = course['credits']

            # Insert into enrollment table
            cursor.execute("""
                INSERT INTO enrollment (student_id, course_id) 
                VALUES (%s, %s)
            """, (student_id, course_id))

            # Update student's total credits
            cursor.execute("""
                UPDATE student
                SET total_credits = total_credits + %s
                WHERE student_id = %s
            """, (course_credits, student_id))

            # Explicitly commit the transaction
            db_connection.commit()
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


# Drop a student from a course
def studentCourseDrop(db_connection, student_id, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get the credits for the course
            cursor.execute("""
                SELECT credits
                FROM course
                WHERE course_id = %s
            """, (course_id,))
            course = cursor.fetchone()
            
            if not course:
                print("Course not found")
                return False
            
            course_credits = course['credits']

            # Delete from enrollment table
            cursor.execute("""
                DELETE FROM enrollment 
                WHERE student_id = %s AND course_id = %s
            """, (student_id, course_id))

            # Update student's total credits
            cursor.execute("""
                UPDATE student
                SET total_credits = total_credits - %s
                WHERE student_id = %s
            """, (course_credits, student_id))

            # Explicitly commit the transaction
            db_connection.commit()
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Get the details about a department
def getDepartmentDetails(db_connection, department_id):
    try:
        with db_connection.cursor() as cursor:
            query = """
            SELECT 
                d.department_name,
                COUNT(DISTINCT i.instructor_id) AS faculty_count,
                COUNT(DISTINCT s.student_id) AS student_count,
                COUNT(DISTINCT m.major_id) AS majors_offered,
                d.office_number AS department_office
            FROM 
                public.department d
            LEFT JOIN 
                public.instructor i ON d.department_id = i.department_id
            LEFT JOIN 
                public.major m ON d.department_id = m.department_id
            LEFT JOIN 
                public.student s ON m.major_id = s.major_id
            WHERE 
                d.department_id = %s
            GROUP BY 
                d.department_id, d.department_name, d.office_number
            """
            cursor.execute(query, (department_id,))
            
            result = cursor.fetchone()
            
            if result:
                return {
                    'department_name': result[0],
                    'faculty_count': result[1],
                    'student_count': result[2],
                    'majors_offered': result[3],
                    'office_number': result[4]
                }
            else:
                return None

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Add a major to the department
def addMajor(db_connection, department_id, major_name, credits):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to insert a new major into the major table
            query = """
                INSERT INTO major (major_name, total_credit_hours, department_id)
                VALUES (%s, %s, %s)
                RETURNING major_id;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (major_name, credits, department_id))
            
            # Fetch the generated major_id
            major_id = cursor.fetchone()[0]
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully added major '{major_name}' with ID: {major_id}")
            return major_id

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return None
    
# Modify a major in the department
def modifyMajor(db_connection, department_id, major_name, new_major_name, new_credits):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to update the major details
            query = """
                UPDATE major
                SET major_name = %s, total_credit_hours = %s
                WHERE department_id = %s AND major_name = %s;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (new_major_name, new_credits, department_id, major_name))
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully modified major '{major_name}' to '{new_major_name}' with new credits: {new_credits}")
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    
# Delete and instructor from a department
def deleteInstructor(db_connection, department_id, instructor_id):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to delete the instructor from the instructor table
            query = """
                DELETE FROM instructor
                WHERE department_id = %s AND instructor_id = %s;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (department_id, instructor_id))
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully deleted instructor with ID: {instructor_id} from department ID: {department_id}")
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    
# Add a new instructor for a given course
def updateCourseForInstructor(db_connection, department_id, instructor_id, course_id):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to update the course with the new instructor
            query = """
                UPDATE course
                SET instructor_id = %s
                WHERE course_id = %s;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (instructor_id, course_id))
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully assigned instructor ID: {instructor_id} to course ID: {course_id}")
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    
# Add course
def addCourse(db_connection, course_prefix, course_number, course_title, credits, 
                                     semester, year, section_id, days, start_time, end_time):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to insert a new course into the course table
            query = """
                INSERT INTO course (course_prefix, course_number, title, credits, semester, year, section_id, days, start_time, end_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING course_id;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (course_prefix, course_number, course_title, credits, semester, year, section_id, days, start_time, end_time))
            
            # Fetch the generated course_id
            course_id = cursor.fetchone()[0]
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully added course '{course_title}' with ID: {course_id}")
            return course_id

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return None
    
# Modify a course
def modifyCourse(db_connection, course_prefix, course_number, new_course_name, new_credits):
    try:
        with db_connection.cursor() as cursor:
            # SQL query to update the course details
            query = """
            UPDATE course
            SET title = %s, credits = %s
            WHERE course_prefix = %s AND course_number = %s;
            """
            # Execute the query with the provided parameters
            cursor.execute(query, (new_course_name, new_credits, course_prefix, course_number))
            
            # Commit the transaction
            db_connection.commit()
            
            print(f"Successfully modified course '{course_prefix} {course_number}' to '{new_course_name}' with new credits: {new_credits}")
            return True
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        db_connection.rollback()  # Rollback on error
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        db_connection.rollback()  # Rollback on error
        return False