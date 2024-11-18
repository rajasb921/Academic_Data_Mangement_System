from .user import User
from tabulate import tabulate

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

    def print_course_schedule(self, db_connection):
        from database.db_operations import getInstructorCourseSchedule

        # Fetch instructor schedule
        schedule = getInstructorCourseSchedule(db_connection, self.id)
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
                f"{course['days']} {course['start_time'].strftime('%I:%M%p')} - {course['end_time'].strftime('%I:%M%p')}"
            ])

        # Define headers for the table
        headers = ["Course", "Title", "Credits", "Time"]

        # Print schedules for each semester
        for sem, courses in semesters.items():
            if courses:
                print(f"--- { 'Fall' if sem == 'F' else 'Spring' } Schedule ---")
                print(tabulate(courses, headers=headers, tablefmt="grid"))
                print()
