from .user import User
class Instructor(User):
    """
    Instructor class representing a university instructor
    """
    def __init__(self, instructor_id, email, first_name, last_name, 
                 phone_number, hired_semester, hired_year, department_id):

        super().__init__(instructor_id, email, first_name, last_name)
        self.phone_number = phone_number
        self.hired_semester = hired_semester
        self.hired_year = hired_year
        self.department_id = department_id