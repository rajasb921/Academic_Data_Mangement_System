from .user import User
from tabulate import tabulate
from .grade_analyzer import GradeAnalyzer

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
        self.grade_analyzer = GradeAnalyzer(self.id, self.gpa, self.total_credits)

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
        # Update gpa if it has been changed
        if (gpa != self.gpa):
            self.gpa = gpa
            updateGPA(db_connection, self.id, gpa)

        return self.gpa
    
    def print_course_schedule(self, db_connection):
        from database.db_operations import getStudentCourseSchedule

        # Fetch schedule
        schedule = getStudentCourseSchedule(db_connection, self.id)
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

    def what_if_analysis(self, db_connection):
        """
        Perform what-if analysis for the student using default test values
        Tests both projection and target GPA scenarios
        """
        # Load completed courses first
        self.grade_analyzer.load_completed_courses(db_connection)
        
        results = {
            "current_status": {
                "student_name": f"{self.first_name} {self.last_name}",
                "current_gpa": round(self.gpa, 2),
                "total_credits": self.total_credits
            },
            "scenarios": []
        }

        # Scenario 1: Project GPA with 2 future courses (default test)
        num_future_courses = 2
        projection_scenarios = self.grade_analyzer.calculate_projected_gpa(num_future_courses)
        
        # Get top 5 best scenarios and worst scenario
        best_scenarios = projection_scenarios[:5]
        worst_scenario = projection_scenarios[-1]
        
        results["scenarios"].extend([
            {
                "type": "projection",
                "num_courses": num_future_courses,
                "best_scenarios": [
                    {
                        "courses": [
                            f"{course['credits']} credits with grade {course['grade']}"
                            for course in scenario['courses']
                        ],
                        "resulting_gpa": scenario['projected_gpa']
                    }
                    for scenario in best_scenarios
                ],
                "worst_scenario": {
                    "courses": [
                        f"{course['credits']} credits with grade {course['grade']}"
                        for course in worst_scenario['courses']
                    ],
                    "resulting_gpa": worst_scenario['projected_gpa']
                }
            }
        ])

        # Scenario 2: Find path to target GPA (default test)
        target_gpa = round(self.gpa + 0.3, 2)  # Test with current GPA + 0.3
        target_solutions = self.grade_analyzer.find_courses_for_target_gpa(target_gpa)
        
        results["scenarios"].extend([
            {
                "type": "target_gpa",
                "target": target_gpa,
                "solutions": target_solutions
            }
        ])

        return results

