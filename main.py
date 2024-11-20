from database.db_connection import DatabaseConnection
import database.db_operations as db_operations
from services.authentication import AuthenticationService
from models.student import Student
from models.advisor import Advisor
from models.staff import Staff
from models.instructor import Instructor
from tabulate import tabulate

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
                self.user.print_major_distribution(self.db_connection)
            elif choice == '4':
                break
            else:
                print("Invalid choice. Please try again.")


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
                student_id = " "
                while (student_id[0] != 'S'):
                    student_id = input("Enter Student ID: ")
                    summary = self.user.get_student_summary(self.db_connection, student_id)
                    if (summary is not None):
                        break
                    print("Invalid Student ID!")
                
                print()
                print(f"Summary for student: {summary['name']}")
                headers = ["Name", "Major", "Completed Credits", "GPA"]
                table = [[summary['name'], summary['major'], summary['completed_credits'], summary['gpa']]]
                print(tabulate(table, headers, tablefmt="grid"))
                
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please try again.")

    def manage_student_enrollment(self):
        while True:
            print("\n--- Student Enrollement Menu ---")
            print("1. Add Course")
            print("2. Drop Course")
            print("3. View Current Registration")
            print("4. Back to Main Menu")

            choice = input("Enter your choice: ")

            if (choice == '1'):
                student_id = " "
                course_id = -1
                while (student_id[0] != 'S'):
                    student_id = input("Enter Student ID: ")
                    if (student_id[0] == 'S'):
                        break
                    print("Invalid Student ID")

                while (course_id == -1):
                    course_id = int(input("Enter Course ID: "))
                    if (course_id > 0):
                        break
                    print("Invalid Course ID")

                self.user.add_course(self.db_connection, student_id, course_id)

            elif (choice == '2'):
                student_id = " "
                course_id = -1
                while (student_id[0] != 'S'):
                    student_id = input("Enter Student ID: ")
                    if (student_id[0] == 'S'):
                        break
                    print("Invalid Student ID")

                while (course_id == -1):
                    course_id = int(input("Enter Course ID: "))
                    if (course_id > 0):
                        break
                    print("Invalid Course ID")

                self.user.drop_course(self.db_connection, student_id, course_id)
            elif (choice == '3'):
                student_id = " "
                while (student_id[0] != 'S'):
                    student_id = input("Enter Student ID: ")
                    schedule = self.user.view_registration(self.db_connection, student_id)
                    if (schedule is not None):
                        break
                    print("Student registration not found")

                # Group courses by semester
                semesters = {"F": [], "S": []}
                for course in schedule:
                    semesters[course["semester"]].append([
                        course["course_code"], 
                        course["course_title"], 
                        course["credits"], 
                        f"{course['days']} {course['start_time'].strftime('%I:%M%p')}"
                    ])

                # Define headers for the table
                headers = ["Course", "Title", "Credits", "Time"]

                # Print schedules for each semester
                print()
                for sem, courses in semesters.items():
                    if courses:
                        print(f"--- { 'Fall' if sem == 'F' else 'Spring' } Schedule ---")
                        print(tabulate(courses, headers=headers, tablefmt="grid"))
                        print()
            elif (choice == '4'):
                break
            else:
                print("Invalid choice. Please try again")

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
                self.user.print_department_details(self.db_connection)
            elif choice == '3':
                self.instructor_management()
            elif choice == '4':
                self.course_management()
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please try again.")

    def major_management(self):
        while True:
            print("\n--- Major Management Menu ---")
            print("1. Add New Major")
            print("2. Modify Existing Major")
            print("3. Back to Main Menu")

            choice = input("Enter your choice: ")

            if (choice == '1'):
                major_name = input("Enter new major name: ")
                credits = "0"
                while (credits < "120"):
                    credits = input("Enter the required credits: ")
                
                credits = int(credits)
                self.user.add_major(self.db_connection, major_name, credits)
            elif (choice == '2'):
                major_name = input("Enter the major name to modify: ")
                new_major_name = input("Enter the new major name: ")
                new_credits = "0"
                while (new_credits < "120"):
                    new_credits = input("Enter the new required credits: ")
                
                new_credits = int(new_credits)
                self.user.modify_major(self.db_connection, major_name, new_major_name, new_credits)
                
            elif (choice == '3'):
                break
            else:
                print("Invalid choice. Please try again")


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