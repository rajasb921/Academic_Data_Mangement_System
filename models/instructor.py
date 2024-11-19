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
    
    def print_student_performance(self, db_connection):
        from database.db_operations import getInstructorCourseSchedule
        from database.db_operations import getPerformance

        schedule = getInstructorCourseSchedule(db_connection, self.id)
        if schedule is None:
            print("Schedule not found")
            return
        
        performances = []
        for course in schedule:

            performance = getPerformance(db_connection, course["course_id"])
            performances.append({
                "course_code": course["course_code"],
                "course_title": course["course_title"], 
                "performance": performance
            })

            # Process and display the performance data
            headers = ["Course", "Students", "Avg Grade", "A", "B", "C", "D", "F"]
            table = []
            for perf in performances:
                performance = perf["performance"]
                avg_grade_percentage = performance["avg_grade"] * 20  # Assuming GPA is out of 4.0
                table.append([
                    perf["course_code"],
                    performance["num_students"],
                    avg_grade_percentage,
                    performance["num_A"],
                    performance["num_B"],
                    performance["num_C"],
                    performance["num_D"],
                    performance["num_F"]
                ])

            print(tabulate(table, headers=headers, tablefmt="grid"))
            print()

        
