from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Company, Department, Employee, PerformanceReview
from datetime import date

class ModelTests(TestCase):

    def setUp(self):
        # Setup sample data
        self.company = Company.objects.create(name="Tech Corp")
        self.department = Department.objects.create(name="Engineering", company=self.company)
        self.user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.employee = Employee.objects.create(
            user=self.user, company=self.company, department=self.department,
            email_address="testuser@techcorp.com", mobile_number="1234567890", 
            designation="Developer", hired_on=date(2020, 1, 1)
        )
    
    def test_number_of_departments_in_company(self):
        # Test the `number_of_departments` property on Company
        self.assertEqual(self.company.number_of_departments, 1)

    def test_number_of_employees_in_department(self):
        # Test the `number_of_employees` property on Department
        self.assertEqual(self.department.number_of_employees, 1)

    def test_days_employed(self):
        # Test the `days_employed` property on Employee
        self.assertGreater(self.employee.days_employed, 0)

    def test_performance_review_approval_validation(self):
        # Test the custom validation in PerformanceReview's save method
        performance_review = PerformanceReview(employee=self.employee, stage="Review Approved", approval_status=False)
        with self.assertRaises(ValueError):
            performance_review.save()  # Should raise error when trying to save a review with "Review Approved" but not approved


from django.test import TestCase
from .models import Company, Department, Employee
from .serializers import PerformanceReviewSerializer
from datetime import date

class PerformanceReviewSerializerTest(TestCase):

    def setUp(self):
        # Setup sample data for this test
        self.company = Company.objects.create(name="Tech Corp")
        self.department = Department.objects.create(name="Engineering", company=self.company)
        self.user = get_user_model().objects.create_user(username="testuser", password="password123")
        self.employee = Employee.objects.create(
            user=self.user, company=self.company, department=self.department,
            email_address="testuser@techcorp.com", mobile_number="1234567890", 
            designation="Developer", hired_on=date(2020, 1, 1)
        )

    def test_performance_review_valid_data(self):
        # Test valid data for performance review serializer
        data = {
            'employee': self.employee.id,  # Correctly associate the employee
            'stage': 'Review Scheduled',
            'approval_status': True
        }
        serializer = PerformanceReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_performance_review_invalid_approval_status(self):
        # Test invalid data for performance review (approval_status is False but stage is "Review Approved")
        data = {
            'employee': self.employee.id,  # Correctly associate the employee
            'stage': 'Review Approved',
            'approval_status': False
        }
        serializer = PerformanceReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)
        self.assertEqual(serializer.errors['non_field_errors'][0], "Review cannot be marked as approved if not approved by manager.")




