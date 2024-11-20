import psycopg2
from psycopg2.extras import RealDictCursor

# Check whether a student is enrolled in a course
def isEnrolled(db_connection, student_id, course_id):
    try:
        with db_connection.cursor() as cursor:
            query = """
                SELECT COUNT(*)
                FROM enrollment
                WHERE student_id = %s AND course_id = %s
            """
            cursor.execute(query, (student_id, course_id))
            result = cursor.fetchone()
            return result[0] > 0
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Check whether the student has availability in their schedule
def checkAvailability(db_connection, student_id, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Fetch the new course's details
            cursor.execute("""
                SELECT days, start_time, end_time
                FROM course
                WHERE course_id = %s
            """, (course_id,))
            new_course = cursor.fetchone()
            
            if not new_course:
                # Course not found
                return False
            
            # Fetch all currently enrolled courses for the student
            cursor.execute("""
                SELECT c.days, c.start_time, c.end_time
                FROM enrollment e
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
            """, (student_id,))
            current_courses = cursor.fetchall()
            
            # Check for schedule conflicts
            new_days = set(new_course['days'])
            new_start = new_course['start_time']
            new_end = new_course['end_time']
            
            for course in current_courses:
                # Check for day overlap
                existing_days = set(course['days'])
                if not new_days.isdisjoint(existing_days):
                    # Days overlap, now check time conflict
                    existing_start = course['start_time']
                    existing_end = course['end_time']
                    
                    # Check if times overlap
                    if not (new_end <= existing_start or new_start >= existing_end):
                        return False
            
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Check whether credits will exceed 18 when adding a course
def willExceedCredits(db_connection, student_id, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get current enrolled credits for the student
            cursor.execute("""
                SELECT SUM(c.credits) AS current_enrolled_credits
                FROM enrollment e
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
            """, (student_id,))
            current_credits_result = cursor.fetchone()
            current_enrolled_credits = current_credits_result['current_enrolled_credits'] or 0

            # Get credits for the new course
            cursor.execute("""
                SELECT credits
                FROM course
                WHERE course_id = %s
            """, (course_id,))
            new_course = cursor.fetchone()
            
            if not new_course:
                # Course not found
                return False
            
            new_course_credits = new_course['credits']

            # Check if total credits would exceed 18
            if current_enrolled_credits + new_course_credits > 18:
                return True
            
            return False

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Check whether the credits will be 0 when deleting a course
def noCredits(db_connection, student_id, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            # Get current enrolled credits for the student
            cursor.execute("""
                SELECT SUM(c.credits) AS current_enrolled_credits
                FROM enrollment e
                JOIN course c ON e.course_id = c.course_id
                WHERE e.student_id = %s
            """, (student_id,))
            current_credits_result = cursor.fetchone()
            current_enrolled_credits = current_credits_result['current_enrolled_credits'] or 0

            # Get credits for the course to be deleted
            cursor.execute("""
                SELECT credits
                FROM course
                WHERE course_id = %s
            """, (course_id,))
            course_to_delete = cursor.fetchone()
            
            if not course_to_delete:
                # Course not found
                return False
            
            course_to_delete_credits = course_to_delete['credits']

            # Check if total credits would be 0 after deletion
            if current_enrolled_credits - course_to_delete_credits == 0:
                return True
            
            return False

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Verify whether the student can take a given course
def checkCourseAdd_ID(db_connection, student_id, course_id):
    enrolled = isEnrolled(db_connection, student_id, course_id)
    if enrolled:
        print("Student already enrolled in this course")
        return False
    print("Student is not currently enrolled in the course")

    available = checkAvailability(db_connection, student_id, course_id)
    if not available:
        print("Student course schedule cannot accomodate this course")
        return False
    print("Student has availability in their schedule")

    credits = willExceedCredits(db_connection, student_id, course_id)
    if credits:
        print("Student will exceed maximum 18 credit limit")
        return False
    print("Student will not exceed 18 credit limit")

    return True

# Verify whether a student can drop a given course
def checkCourseDrop(db_connection, student_id, course_id):
    enrolled = isEnrolled(db_connection, student_id, course_id)
    if not enrolled:
        print("Student is not enrolled in this course")
        return False
    print("Student is currently enrolled in the course")

    no_credits = noCredits(db_connection, student_id, course_id)
    if no_credits:
        print("Student will have 0 credits after dropping this course")
        return False
    print("Student will not have 0 credits after dropping this course")

    return True

# Check whether a major exists in the department
def majorExists(db_connection, department_id, major_name):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM major
                WHERE department_id = %s AND major_name = %s
            """
            cursor.execute(query, (department_id, major_name))
            result = cursor.fetchone()
            return result['count'] > 0
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Verify whether a major can be added
def checkMajorAdd(db_connection, department_id, major_name, credits):
    if majorExists(db_connection, department_id, major_name):
        print("This major already exists in the department")
        return False
    print("This major does not exist in the department")
    if credits < 120 or credits > 144:
        print("Each major is required to have between 120 and 144 credits")
        return False
    return True

# Verify whether a major can be changed
def checkMajorModify(db_connection, department_id, major_name, new_major_name, new_credits):
    if not majorExists(db_connection, department_id, major_name):
        print("The major to be modified does not exist in the department")
        return False
    print("The major to be modified exists in the department")

    if majorExists(db_connection, department_id, new_major_name):
        print("The new major name already exists in the department")
        return False
    print("The new major name does not exist in the department")

    if new_credits < 120 or new_credits > 144:
        print("Each major is required to have between 120 and 144 credits")
        return False

    return True

# Counts number of courses an instructor teaches
def countCourses(db_connection, instructor_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM course
                WHERE instructor_id = %s
            """
            cursor.execute(query, (instructor_id,))
            result = cursor.fetchone()
            return result['count']
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Verify whether an instructor belongs to a particular department
def checkInstructorDept(db_connection, department_id, instructor_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM instructor
                WHERE department_id = %s AND instructor_id = %s
            """
            cursor.execute(query, (department_id, instructor_id))
            result = cursor.fetchone()
            return result['count'] > 0
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Verify whether an instructor can be deleted
def checkInstructorDelete(db_connection, department_id, instructor_id):
    if not checkInstructorDept(db_connection, department_id, instructor_id):
        print("Instructor does not belong to the specified department")
        return False
    print("Instructor belongs to the specified department")

    courses_count = countCourses(db_connection, instructor_id)
    if courses_count > 0:
        print("Instructor is currently teaching courses")
        return False
    print("Instructor is not teaching any courses")

    return True

# Verify whether an instructor teaches a course
def instructorTeachesCourse(db_connection, instructor_id, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM course
                WHERE instructor_id = %s AND course_id = %s
            """
            cursor.execute(query, (instructor_id, course_id))
            result = cursor.fetchone()
            return result['count'] > 0
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Verify whether an instructor can teach a course
def checkCourseUpdate(db_connection, department_id, instructor_id, course_id):

    if instructorTeachesCourse(db_connection, instructor_id, course_id):
        print("Instructor already teaches this course")
        return False
    print("Instructor does not teach this course")

    return True


# Check whether a course exists in the department
def courseExists(db_connection, course_prefix, course_number):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM course
                WHERE course_prefix = %s AND course_number = %s
            """
            cursor.execute(query, (course_prefix, course_number))
            result = cursor.fetchone()
            return result['count'] > 0
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
# Verify whether a course can be added
def checkCourseAdd(db_connection, course_prefix, course_number, course_title, credits, 
                                     semester, year, section_id, days, start_time, end_time):
    if courseExists(db_connection, course_prefix, course_number):
        print("Course already exists in the department")
        return False
    print("Course does not exist in the department")

    if credits < 1 or credits > 4:
        print("Each course is required to have between 1 and 4 credits")
        return False

    return True

# Verify whether a course can be changed
def checkCourseModify(db_connection, course_prefix, course_number, new_course_name, new_credits):
    if not courseExists(db_connection, course_prefix, course_number):
        print("Course to be modified does not exist")
        return False
    print("Course to be modified exists")

    if new_credits < 1 or new_credits > 4:
        print("Each course is required to have between 1 and 4 credits")
        return False

    return True

# Check number of students in a course
def numStudentsInCourse(db_connection, course_id):
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT COUNT(*)
                FROM enrollment
                WHERE course_id = %s
            """
            cursor.execute(query, (course_id,))
            result = cursor.fetchone()
            return result['count']
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Verify whether a course can be deleted
def checkCourseDelete(db_connection, course_prefix, course_number):
    if not courseExists(db_connection, course_prefix, course_number):
        print("Course does not exist")
        return False
    print("Course exists")
    try:
        with db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT course_id
                FROM course
                WHERE course_prefix = %s AND course_number = %s
            """
            cursor.execute(query, (course_prefix, course_number))
            course = cursor.fetchone()
            
            if not course:
                print("Course not found")
                return False
            
            course_id = int(course['course_id'])
            num_students = numStudentsInCourse(db_connection, course_id)

            if num_students > 0:
                print(f"Course has {num_students} students enrolled")
                return False
            print("Course has no students enrolled")
            
            return True

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
