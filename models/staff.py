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