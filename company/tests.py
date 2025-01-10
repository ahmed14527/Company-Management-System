from django.test import TestCase
from django.utils import timezone
from datetime import date
from django.utils.timezone import now
from .models import (
    User,
    Company,
    Department,
    Employee,
    Project,
    PerformanceReview
)


class ModelsTestCase(TestCase):
    def setUp(self):
        # Create a company
        self.company = Company.objects.create(name="TechCorp")

        # Create a department
        self.department = Department.objects.create(company=self.company, name="Development")

        # Create a user
        self.user = User.objects.create_user(
            email="employee@example.com", 
            password="password123", 
            role="Employee", 
            company=self.company
        )

        # Create an employee
        self.employee = Employee.objects.create(
            user=self.user,
            company=self.company,
            department=self.department,
            email_address="employee@example.com",
            designation="Software Engineer",
            hired_on=date(2023, 1, 1)
        )

        # Create a project
        self.project = Project.objects.create(
            company=self.company,
            department=self.department,
            name="Project A",
            description="A sample project",
            start_date=date(2023, 2, 1),
            end_date=date(2023, 6, 1)
        )
        self.project.assigned_employees.add(self.employee)

        # Create a performance review
        self.review = PerformanceReview.objects.create(
            employee=self.employee,
            stage="pending_review",
            feedback="Great work!",
            is_approved=False
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "employee@example.com")
        self.assertTrue(self.user.check_password("password123"))
        self.assertEqual(self.user.role, "Employee")

    def test_company_creation(self):
        self.assertEqual(self.company.name, "TechCorp")
        self.assertEqual(self.company.number_of_departments, 1)
        self.assertEqual(self.company.number_of_employees, 1)

    def test_department_creation(self):
        self.assertEqual(self.department.name, "Development")
        self.assertEqual(self.department.number_of_employees, 1)
        self.assertEqual(self.department.number_of_projects, 1)

    def test_employee_creation(self):
        self.assertEqual(self.employee.user.email, "employee@example.com")
        self.assertEqual(self.employee.designation, "Software Engineer")
        self.assertEqual(self.employee.days_employed, (timezone.now().date() - date(2023, 1, 1)).days)

    def test_project_creation(self):
        self.assertEqual(self.project.name, "Project A")
        self.assertEqual(self.project.assigned_employees.count(), 1)
        self.assertEqual(self.project.assigned_employees.first(), self.employee)

    def test_performance_review_creation(self):
        self.assertEqual(self.review.employee, self.employee)
        self.assertEqual(self.review.stage, "pending_review")
        self.assertEqual(self.review.feedback, "Great work!")
        self.assertFalse(self.review.is_approved)

    def test_performance_review_stage_transition(self):
        # Test a valid stage transition
        self.review.transition("review_scheduled")
        self.assertEqual(self.review.stage, "review_scheduled")

        # Test an invalid stage transition
        with self.assertRaises(ValueError):
            self.review.transition("review_approved")

    def test_company_relationships(self):
        self.assertEqual(self.company.users.count(), 1)
        self.assertEqual(self.company.departments.count(), 1)
        self.assertEqual(self.company.projects.count(), 1)

    def test_department_relationships(self):
        self.assertEqual(self.department.employees.count(), 1)
        self.assertEqual(self.department.projects.count(), 1)
        
        



