from .user import User
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