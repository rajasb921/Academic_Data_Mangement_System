class GradeAnalyzer:
    def __init__(self, student_id, gpa, credits):
        # Core student data
        self.student_id = student_id
        
        # Current academic data (from student table)
        self.current_gpa = gpa
        self.total_credits = credits
        
        # Grade system for calculations
        self.grade_points = {
            'A': 4.0,
            'B': 3.0,
            'C': 2.0,
            'D': 1.0,
            'F': 0.0
        }
        
        # Completed courses (from enrollment and course tables)
        # Only need: course credits and grade
        self.completed_courses = []

    def load_completed_courses(self, db_connection):
        from database.db_operations import getCourseSchedule
        schedule = getCourseSchedule(db_connection, self.student_id)
        if schedule:
            self.completed_courses = [
                {
                    'credits': course['credits'],
                    'grade': course['grade']
                }
                for course in schedule
                if course['grade'] is not None  # Only include courses with grades
            ]

    def calculate_projected_gpa(self, num_courses):
        """
        Calculate all possible projected GPAs for given number of additional courses
        
        Args:
            num_courses: int (number of future courses to consider)
        
        Returns:
            List of dictionaries containing:
            - courses: List of course details (credits and grades)
            - projected_gpa: float (resulting GPA)
        """
        # Calculate current total grade points
        current_points = self.current_gpa * self.total_credits
        
        # Define possible grades
        possible_grades = ['A', 'B', 'C', 'D', 'F']
        default_credits = 3
        scenarios = []
        
        # Generate all possible grade combinations
        from itertools import product
        grade_combinations = product(possible_grades, repeat=num_courses)
        
        for grades in grade_combinations:
            # Create course list for this scenario
            future_courses = [
                {'credits': default_credits, 'grade': grade}
                for grade in grades
            ]
            
            # Calculate additional points and credits
            additional_points = sum(
                course['credits'] * self.grade_points[course['grade']]
                for course in future_courses
            )
            additional_credits = default_credits * num_courses
            
            # Calculate new GPA
            new_total_credits = self.total_credits + additional_credits
            new_total_points = current_points + additional_points
            projected_gpa = new_total_points / new_total_credits if new_total_credits > 0 else 0.0
            
            scenarios.append({
                'courses': future_courses,
                'projected_gpa': round(projected_gpa, 2)
            })
        
        # Sort scenarios by projected GPA in descending order
        scenarios.sort(key=lambda x: x['projected_gpa'], reverse=True)
        
        return scenarios

    def find_courses_for_target_gpa(self, target_gpa, max_courses=3):
        """
        Find combinations of courses needed to achieve target GPA
        
        Args:
            target_gpa: float (desired GPA)
            max_courses: int (maximum number of additional courses to consider)
        
        Returns:
            List of possible course combinations
        """
        if target_gpa < self.current_gpa:
            return [{"message": "Target GPA is lower than current GPA"}]
            
        solutions = []
        standard_credits = [3, 4]  # Most common credit values
        possible_grades = ['A', 'B', 'C']  # Realistic grades to consider
        
        # Current total points
        current_points = self.current_gpa * self.total_credits
        
        # Try different numbers of courses
        for num_courses in range(1, max_courses + 1):
            # Try different credit combinations
            from itertools import product
            for credits_combo in product(standard_credits, repeat=num_courses):
                for grades_combo in product(possible_grades, repeat=num_courses):
                    # Calculate new total credits and points
                    new_credits = sum(credits_combo)
                    new_points = sum(
                        credits * self.grade_points[grade]
                        for credits, grade in zip(credits_combo, grades_combo)
                    )
                    
                    # Calculate resulting GPA
                    total_new_credits = self.total_credits + new_credits
                    total_new_points = current_points + new_points
                    resulting_gpa = total_new_points / total_new_credits
                    
                    # Check if this combination achieves the target GPA
                    if abs(resulting_gpa - target_gpa) < 0.1:  # Allow small difference
                        solution = {
                            "courses": [
                                {"credits": cred, "grade": grade}
                                for cred, grade in zip(credits_combo, grades_combo)
                            ],
                            "resulting_gpa": round(resulting_gpa, 2)
                        }
                        solutions.append(solution)
                        
                        # Limit number of solutions
                        if len(solutions) >= 5:
                            return solutions
        
        return solutions if solutions else [{"message": "No feasible solution found"}]