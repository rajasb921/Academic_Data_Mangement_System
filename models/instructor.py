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
        schedule, data_affected = getInstructorCourseSchedule(db_connection, self.id)
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

        # Log
        self.logger.log(self.id, 'read', data_affected)
        
    def print_student_performance(self, db_connection, course_id):
        from database.db_verification import instructorTeachesCourse
        from database.db_operations import getPerformance

        if not instructorTeachesCourse(db_connection, self.id, course_id):
            print("Instructor does not teach this course")
            return None
        
        # Fetch course summary
        course_summary, data_affected = getPerformance(db_connection, course_id)
        if course_summary is None:
            print("Course summary not found")
            return
        
        # Convert average grade to percentage
        avg_percentage = float(course_summary['avg_grade']) * 25  # Assuming 4.0 scale = 100%

        # Prepare summary data for tabulation
        summary_data = [
            ["Course", course_summary['course']],
            ["Total Students", course_summary['num_students']],
            ["Average Grade", f"{avg_percentage:.2f}%"],
            ["Grade Distribution", 
            f"A: {course_summary['num_A']}, "
            f"B: {course_summary['num_B']}, "
            f"C: {course_summary['num_C']}, "
            f"D: {course_summary['num_D']}, "
            f"F: {course_summary['num_F']}"]
        ]

        # Print summary
        print(f"--- Course Summary ---")
        print(tabulate(summary_data, tablefmt="grid"))
        print()

        # Log
        self.logger.log(self.id, 'read', data_affected)
        
        
    def print_major_distribution(self, db_connection):
        from database.db_operations import getInstructorCourseSchedule
        from database.db_operations import getMajorDistribution

        schedule = getInstructorCourseSchedule(db_connection, self.id)
        if schedule is None:
            print("Schedule not found")
            return
        
        major_distributions = []
        for course in schedule:
            major_dist = getMajorDistribution(db_connection, course["course_id"])
            major_distributions.append({
                "course_code": course["course_code"],
                "course_title": course["course_title"], 
                "major_distribution": major_dist
            })

        # Process and display the major distribution data
        headers = ["Course", "Major", "Students", "Percentage"]
        for dist in major_distributions:
            if dist["major_distribution"]:
                table = []
                for major in dist["major_distribution"]:
                    table.append([
                        dist["course_code"],
                        major["major"],
                        major["num_students"],
                        major["percentage"]
                    ])
                print(tabulate(table, headers=headers, tablefmt="grid"))
                print()
                print()