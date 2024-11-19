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
def checkCourseAdd(db_connection, student_id, course_id):
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
