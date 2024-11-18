from .user import User
class Staff(User):
    """
    Staff class representing university staff
    """
    def __init__(self, staff_id, email, first_name, last_name, 
                 phone_number, department_id):

        super().__init__(staff_id, email, first_name, last_name)
        self.phone_number = phone_number
        self.department_id = department_id