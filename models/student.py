from .user import User
from tabulate import tabulate

class Student(User):
    """
    Student class representing a university student
    """
    def __init__(self, student_id, email, first_name, last_name, 
                 gpa, total_credits, major_id):

        super().__init__(student_id, email, first_name, last_name)
        self.gpa = gpa
        self.total_credits = total_credits
        self.major_id = major_id
    
    def get_gpa(self, db_connection):
        from database.db_operations import getGrades
        from database.db_operations import updateGPA
        # Fetch latest gpa
        grades = getGrades(db_connection, self.id)

        gpa_map = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        total_points = 0
        total_courses = len(grades)

        for grade in grades:
            total_points += gpa_map.get(grade, 0)

        gpa = total_points / total_courses if total_courses > 0 else 0
        if (gpa != self.gpa):
            self.gpa = gpa
            updateGPA(db_connection, self.id, gpa)

        return self.gpa
    
    def print_course_schedule(self, db_connection):
        from database.db_operations import getCourseSchedule

        # Fetch schedule
        schedule = getCourseSchedule(db_connection, self.id)
        if schedule is None:
            print("Schedule not found")
            return
        
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
        for sem, courses in semesters.items():
            if courses:
                print(f"--- { 'Fall' if sem == 'F' else 'Spring' } Schedule ---")
                print(tabulate(courses, headers=headers, tablefmt="grid"))
                print()
