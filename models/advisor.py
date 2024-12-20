from .user import User
from tabulate import tabulate

class Advisor(User):
    """
    Advisor class representing a university advisor
    """
    def __init__(self, advisor_id, email, first_name, last_name, phone_number):
        """
        Initialize an Advisor instance
        
        :param advisor_id: Unique advisor identifier
        :param email: Advisor's email address
        :param first_name: Advisor's first name
        :param last_name: Advisor's last name
        :param phone_number: Advisor's phone number
        """
        super().__init__(advisor_id, email, first_name, last_name)
        self.phone_number = phone_number
    
    def get_student_summary(self, db_connection, student_id):
        from database.db_operations import getStudentSummary

        summary, data_affected = getStudentSummary(db_connection, student_id)
        if summary is None:
            print("Summary not found")
            return None
        
        self.logger.log(self.id, 'read', data_affected)
        return summary
    

    def add_course(self, db_connection, student_id, course_id):
        from database.db_verification import checkCourseAdd_ID
        from database.db_operations import studentCourseAdd
        if not checkCourseAdd_ID(db_connection, student_id, course_id):
            print("Course Add Failed")
            return None
        
        flag, data_affected, old_data, new_data = studentCourseAdd(db_connection, student_id, course_id)
        

        if flag:
            print("Course added successfully")
            # Log
            self.logger.log(self.id, 'modify', data_affected, old_data, new_data)
            return None
    
    def drop_course(self, db_connection, student_id, course_id):
        from database.db_verification import checkCourseDrop
        from database.db_operations import studentCourseDrop
        if not checkCourseDrop(db_connection, student_id, course_id):
            print("Course Drop Failed")
            return None
        
        flag, data_affected, old_data, new_data = studentCourseDrop(db_connection, student_id, course_id)
        if flag:
            print("Course dropped successfully")
            # Log
            self.logger.log(self.id, 'delete', data_affected, old_data, new_data)
            return None
    
    def view_registration(self, db_connection, student_id):
        from database.db_operations import getStudentCourseSchedule

        # Fetch schedule
        schedule, data_affected = getStudentCourseSchedule(db_connection, student_id)
        if schedule is None:
            print("Schedule not found")
            return
        
        # Log
        self.logger.log(self.id, 'read', data_affected)
        return schedule