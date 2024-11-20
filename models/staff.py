from .user import User
from tabulate import tabulate

class Staff(User):
    """
    Staff class representing university staff
    """
    def __init__(self, staff_id, email, first_name, last_name, 
                 phone_number, department_id):

        super().__init__(staff_id, email, first_name, last_name)
        self.phone_number = phone_number
        self.department_id = department_id

    def print_department_details(self, db_connection):
        from database.db_operations import getDepartmentDetails

        details = getDepartmentDetails(db_connection, self.department_id)
        if (details is None):
            print("Department details not found")
            return None
        
        headers = ["Department Name", "Faculty Count", "Student Count", "Majors Offered", "Office Number"]
        table = [[details['department_name'], details['faculty_count'], details['student_count'], 
              details['majors_offered'], details['office_number']]]
        print(tabulate(table, headers, tablefmt="grid"))
    
    def add_major(self, db_connection, major_name, credits):
        from database.db_verification import checkMajorAdd
        from database.db_operations import addMajor


        if not checkMajorAdd(db_connection, self.department_id, major_name, credits):
            print("Major cannot be added")
            return False
        
        if addMajor(db_connection, self.department_id, major_name, credits):
            print("Major added")
            return True
        
        return False
    
    def modify_major(self, db_connection, major_name, new_major_name, new_credits):
        from database.db_verification import checkMajorModify
        from database.db_operations import modifyMajor

        if not checkMajorModify(db_connection, self.department_id, major_name, new_major_name, new_credits):
            print("Major cannot be modified")
            return False
        
        if modifyMajor(db_connection, self.department_id, major_name, new_major_name, new_credits):
            print("Major modified")
            return True
        
        return False
    
    def view_instructor_schedule(self, db_connection, instructor_id):
        from database.db_verification import checkInstructorDept
        from database.db_operations import getInstructorCourseSchedule

        if not checkInstructorDept(db_connection, self.department_id, instructor_id):
            print("Instructor does not belong to your department")
            return
        
        schedule = getInstructorCourseSchedule(db_connection, instructor_id)
        if schedule:
            headers = ["Course", "Title", "Credits", "Time"]
            courses = [
                [
                    course["course_code"],
                    course["course_title"],
                    course["credits"],
                    f"{course['days']} {course['start_time'].strftime('%I:%M%p')}"
                ]
            for course in schedule]
            print(tabulate(courses, headers=headers, tablefmt="grid"))
        else:
            print("No schedule found for the given instructor ID.")

    def delete_instructor(self, db_connection, instructor_id):
        from database.db_verification import checkInstructorDelete
        from database.db_operations import deleteInstructor

        if not checkInstructorDelete(db_connection, self.department_id, instructor_id):
            print("Instructor cannot be deleted")
            return False

        if deleteInstructor(db_connection, self.department_id, instructor_id):
            print("Instructor deleted")
            return True
        
        print("Failed to delete instructor")
        return False
    
    def update_course_for_instructor(self, db_connection, instructor_id, course_id):
        from database.db_verification import checkCourseUpdate
        from database.db_operations import updateCourseForInstructor

        if not checkCourseUpdate(db_connection, self.department_id, instructor_id, course_id):
            print("Course cannot be added for the instructor")
            return False

        if updateCourseForInstructor(db_connection, self.department_id, instructor_id, course_id):
            print("Course added for the instructor")
            return True

        print("Failed to add course for the instructor")
        return False
    
    def delete_course_for_instructor(self, db_connection, instructor_id, course_id):
        from database.db_verification import checkCourseDelete
        from database.db_operations import deleteCourseForInstructor


        if not checkCourseDelete(db_connection, self.department_id, instructor_id, course_id):
            print("Course cannot be deleted for the instructor")
            return False

        if deleteCourseForInstructor(db_connection, self.department_id, instructor_id, course_id):
            print("Course deleted for the instructor")
            return True

        print("Failed to delete course for the instructor")
        return False
    
    def add_course(self, db_connection, course_prefix, course_number, course_title, credits, 
                                     semester, year, section_id, days, start_time, end_time):
        
        from database.db_verification import checkCourseAdd
        from database.db_operations import addCourse

        if not checkCourseAdd(db_connection, course_prefix, course_number, course_title, credits, 
                                     semester, year, section_id, days, start_time, end_time):
            print("Course cannot be added")
            return False

        if addCourse(db_connection, course_prefix, course_number, course_title, credits, 
                                     semester, year, section_id, days, start_time, end_time):
            print("Course added")
            return True

        print("Failed to add course")
        return False
    
    def modify_course(self, db_connection, course_prefix, course_number, new_course_name, new_credits):
        from database.db_verification import checkCourseModify
        from database.db_operations import modifyCourse

        if not checkCourseModify(db_connection, course_prefix, course_number, new_course_name, new_credits):
            print("Course cannot be modified")
            return False

        if modifyCourse(db_connection, course_prefix, course_number, new_course_name, new_credits):
            print("Course modified")
            return True

        print("Failed to modify course")
        return False