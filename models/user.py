from services.log import FileLogger
class User:
    def __init__(self, user_id, email, first_name, last_name):
        """
        Initialize a User instance.
        
        :param user_id: Unique identifier for the user
        :param email: User's email address
        :param first_name: User's first name
        :param last_name: User's last name
        """
        self.id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.logger = FileLogger()

    def __repr__(self):
        """
        Provide a string representation of the User instance.
        
        :return: String representation of the user
        """
        return f"User(id={self.id}, email={self.email}, name={self.get_full_name()})"
    
    def get_full_name(self):
        return self.first_name + " " + self.last_name
    