from database.db_connection import DatabaseConnection
import database.db_operations as db_operations
from services.authentication import AuthenticationService
from models.student import Student
from models.advisor import Advisor
from models.staff import Staff
from models.instructor import Instructor

class UniversityManagementSystem:
    def __init__(self):
        self.db_connection = None
        self.auth_service = None
        self.user = None

    def start(self):
        self.db_connection = DatabaseConnection()
        self.auth_service = AuthenticationService(self.db_connection)

    def login(self):
        """
        Authentication method for the University Management System
        """
        print("Welcome to University Management System")
        while self.user is None:
            email = input("Email: ")
            password = input("Password: ")
            user = self.auth_service.authenticate_user(email, password)
            self.user = user
            if self.user is None:
                print("User Authentication failed!")
                return
        
        # Menus
        if isinstance(self.user, Student):
            self.student_main_menu()
        elif isinstance(self.user, Instructor):
            self.instructor_main_menu()
        elif isinstance(self.user, Advisor):
            self.advisor_main_menu()
        elif isinstance(self.user, Staff):
            self.staff_main_menu()
        else:
            print("Invalid user type")

    def method_not_implemented(self):
        """
        Placeholder for methods not yet implemented
        """
        print("Method not implemented. Coming soon!")

    # Student Menu and Methods
    def student_main_menu(self):
        while True:
            print("\n--- Student Main Menu ---")
            print("1. View Course Schedule")
            print("2. Perform What-If Analysis")
            print("3. View GPA")
            print("4. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.user.print_course_schedule(self.db_connection)
            elif choice == '2':
                # Perform what-if analysis
                analysis_results = self.user.what_if_analysis(self.db_connection)
                
                # Print student's current status
                print("\n=== What-If Analysis ===")
                print(f"Student: {analysis_results['current_status']['student_name']}")
                print(f"Current GPA: {analysis_results['current_status']['current_gpa']}")
                print(f"Total Credits: {analysis_results['current_status']['total_credits']}")
                
                while True:
                    print("\nWhat-If Analysis Options:")
                    print("1. Project GPA with additional courses")
                    print("2. Find path to target GPA")
                    print("3. Return to main menu")
                    
                    analysis_choice = input("\nEnter your choice (1-3): ")
                    
                    if analysis_choice == '1':
                        try:
                            num_courses = int(input("\nEnter number of future courses to consider: "))
                            if num_courses <= 0:
                                print("Please enter a positive number of courses.")
                                continue
                            
                            projection_scenarios = self.user.grade_analyzer.calculate_projected_gpa(num_courses)
                            
                            print("\nTop 5 Best Scenarios:")
                            for i, scenario in enumerate(projection_scenarios[:5], 1):
                                print(f"\nScenario {i}:")
                                for course in scenario['courses']:
                                    print(f"- Take a 3-credit course with grade {course['grade']}")
                                print(f"Projected GPA: {scenario['projected_gpa']}")
                            
                            print("\nWorst Scenario:")
                            worst = projection_scenarios[-1]
                            for course in worst['courses']:
                                print(f"- Take a 3-credit course with grade {course['grade']}")
                            print(f"Projected GPA: {worst['projected_gpa']}")
                            
                        except ValueError:
                            print("Please enter a valid number.")
                            
                    elif analysis_choice == '2':
                        try:
                            target_gpa = float(input("\nEnter your target GPA: "))
                            if target_gpa < 0 or target_gpa > 4.0:
                                print("Please enter a GPA between 0.0 and 4.0")
                                continue
                                
                            solutions = self.user.grade_analyzer.find_courses_for_target_gpa(target_gpa)
                            
                            print(f"\nPaths to reach GPA of {target_gpa}:")
                            if "message" in solutions[0]:
                                print(solutions[0]["message"])
                            else:
                                for i, solution in enumerate(solutions, 1):
                                    print(f"\nPath {i}:")
                                    for course in solution['courses']:
                                        print(f"- Take a {course['credits']}-credit course with grade {course['grade']}")
                                    print(f"Resulting GPA: {solution['resulting_gpa']}")
                            
                        except ValueError:
                            print("Please enter a valid GPA number.")
                    else:
                        break
            elif choice == '3':
                gpa = self.user.get_gpa(self.db_connection)
                print(f"Your current GPA is: {gpa:.1f}")
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")


    # Instructor Menu and Methods
    def instructor_main_menu(self):
        while True:
            print("\n--- Instructor Main Menu ---")
            print("1. View Course Schedule")
            print("2. Student Performance")
            print("3. Major Distribution")
            print("4. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.user.print_course_schedule(self.db_connection)
            elif choice == '2':
                self.user.print_student_performance(self.db_connection)
            elif choice == '3':
                self.view_major_distribution()
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")

    def view_instructor_course_schedule(self):
        self.method_not_implemented()

    def view_student_performance(self):
        self.method_not_implemented()

    def view_major_distribution(self):
        self.method_not_implemented()

    # Advisor Menu and Methods
    def advisor_main_menu(self):
        while True:
            print("\n--- Advisor Main Menu ---")
            print("1. Manage Student Enrollment")
            print("2. View Student Summary")
            print("3. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.manage_student_enrollment()
            elif choice == '2':
                self.view_student_summary()
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_student_enrollment(self):
        self.method_not_implemented()

    def view_student_summary(self):
        self.method_not_implemented()

    # Staff Menu and Methods
    def staff_main_menu(self):
        while True:
            print("\n--- Staff Main Menu ---")
            print("1. Major Management")
            print("2. Department Details")
            print("3. Instructor Management")
            print("4. Course Management")
            print("5. Exit")
            
            choice = input("Enter your choice: ")
            
            if choice == '1':
                self.major_management()
            elif choice == '2':
                self.view_department_details()
            elif choice == '3':
                self.instructor_management()
            elif choice == '4':
                self.course_management()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def major_management(self):
        self.method_not_implemented()

    def view_department_details(self):
        self.method_not_implemented()

    def instructor_management(self):
        self.method_not_implemented()

    def course_management(self):
        self.method_not_implemented()

def main():
    university_system = UniversityManagementSystem()
    university_system.start()
    university_system.login()

if __name__ == "__main__":
    main()