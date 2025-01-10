# Company Management System
 

<p>An online Company Management System developed in django-3:) </p>

### Short Note

This guide will Step-by-Step help you to create your own Company Management System APIs in DRF.

Note: this guide is not for absolute beginners so im assuming that you have the basic knowledge of MVT in django to get started. To know more on it i recommend you <a href="https://docs.djangoproject.com/en/3.0/">django documentation</a>.

# Table of contents
- [About_this_App](#About_this_App)
- [Company_app](#hospitals_app)
  * [models](#models)
  * [migrations](#migrations)
  * [admin](#admin)
  * [server](#server)
  * [views](#views)
  * [tests](#tests)
  * [urls](#urls)
  * [Swagger_UI](#Swagger_UI)
  * [Logging](#Logging)
  
<hr>

## About_this_App
Django Company Management System is a comprehensive application designed to efficiently manage Company operations. It covers various aspects of Company management, including User Accounts and Company , Department, Employee, Project.


## Company_app

Lets begin our project by starting our project and installing a Company_app , type below commands in terminal.

(django_project)$`django-admin startproject DRF .` (do not avoid this period)

(django_project)$`python manage.py startapp Company`

Now, open your favourite IDE and locate this project directory. (Im using VS Code so it should be something like this) note that at this point django doesnt know about this app, therefore we need to mention this app name inside our settings.py file.

* settings.py 

open your ecom_project folder, in here you will find settings.py file (open it). Go to Installed app section and mention your app name there (as shown below).


	INSTALLED_APPS = [
	    'django.contrib.admin',
	    'django.contrib.auth',
	    'django.contrib.contenttypes',
	    'django.contrib.sessions',
	    'django.contrib.messages',
	    'django.contrib.staticfiles',


        # Packages installed 
        'rest_framework',
        'rest_framework_simplejwt',
        'corsheaders',
        'drf_spectacular',
        
	    # my apps,				# changes
	    'Company',
	    ]


### models

When done with the settings.py file, open the course folder (our app), in here you we find models.py file (open it)
Now put the following code in it,


	from django.db import models
    from django.contrib.auth.models import AbstractUser
    from django.db.models import Count
    from django.utils import timezone

    # Custom User model to extend user with roles and other info
    from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
    from django.db import models

    # Custom User Manager for creating user and superuser
    class CustomUserManager(BaseUserManager):
        def create_user(self, email, password=None, **extra_fields):
            """Create and return a regular user with an email and password."""
            if not email:
                raise ValueError('A user email is needed.')
            
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            user.set_password(password)  # Hash the password
            user.save(using=self._db)
            return user

        def create_superuser(self, email, password=None, **extra_fields):
            """Create and return a superuser with an email and password."""
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('is_superuser', True)

            if extra_fields.get('is_staff') is not True:
                raise ValueError('Superuser must have is_staff=True.')
            if extra_fields.get('is_superuser') is not True:
                raise ValueError('Superuser must have is_superuser=True.')

            return self.create_user(email, password, **extra_fields)

    # Define the custom user model
    class User(AbstractBaseUser, PermissionsMixin):
        # Primary key (auto-generated)
        user_id = models.AutoField(primary_key=True)

        # User fields
        email = models.EmailField(max_length=100, unique=True)  # Email is used as the unique identifier
        username = models.CharField(max_length=100, blank=True)  # Optional field for legacy support, but not used as a unique identifier
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)
        date_joined = models.DateField(auto_now_add=True)

        # Role and company relationship
        ROLE_CHOICES = [
            ('Admin', 'Admin'),
            ('Manager', 'Manager'),
            ('Employee', 'Employee'),
        ]
        role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
        company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

        # To specify the email as the unique field for authentication
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = ['username']  # If you want to keep a required field for username (for legacy purposes)

        # Custom manager for handling user creation
        objects = CustomUserManager()

        def __str__(self):
            return self.email


    # Company model
    class Company(models.Model):
        name = models.CharField(max_length=255)
        
        @property
        def number_of_departments(self):
            return self.departments.count()
        
        @property
        def number_of_employees(self):
            return self.users.count()
        
        @property
        def number_of_projects(self):
            return self.projects.count()
        
        def __str__(self):
            return self.name

    # Department model
    class Department(models.Model):
        company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
        name = models.CharField(max_length=255)
        
        @property
        def number_of_employees(self):
            return self.employees.count()
        
        @property
        def number_of_projects(self):
            return self.projects.count()

        def __str__(self):
            return self.name

    # Employee model
    class Employee(models.Model):
        user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee')
        company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
        department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
        email_address = models.EmailField()
        mobile_number = models.CharField(max_length=15, blank=True, null=True)
        address = models.TextField(blank=True, null=True)
        designation = models.CharField(max_length=255)
        hired_on = models.DateField(null=True, blank=True)
        
        @property
        def days_employed(self):
            if self.hired_on:
                return (timezone.now().date() - self.hired_on).days
            return 0
        
        @property
        def number_of_projects(self):
            return self.projects.count()

        def __str__(self):
            return f"{self.user.username} - {self.designation}"

    # Project model
    class Project(models.Model):
        company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects')
        department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects')
        name = models.CharField(max_length=255)
        description = models.TextField()
        start_date = models.DateField()
        end_date = models.DateField(null=True, blank=True)
        assigned_employees = models.ManyToManyField(Employee, related_name='projects')
        
        def __str__(self):
            return self.name


    class PerformanceReview(models.Model):
        STAGE_CHOICES = [
            ('pending_review', 'Pending Review'),
            ('review_scheduled', 'Review Scheduled'),
            ('feedback_provided', 'Feedback Provided'),
            ('under_approval', 'Under Approval'),
            ('review_approved', 'Review Approved'),
            ('review_rejected', 'Review Rejected'),
        ]

        employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
        stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='pending_review')
        review_date = models.DateTimeField(null=True, blank=True)
        feedback = models.TextField(blank=True, null=True)
        is_approved = models.BooleanField(default=False)  # True for approved, False for rejected
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"Performance Review for {self.employee.name} - {self.get_stage_display()}"

        def transition(self, new_stage):
            """Transition logic for stages."""
            allowed_transitions = {
                'pending_review': ['review_scheduled'],
                'review_scheduled': ['feedback_provided'],
                'feedback_provided': ['under_approval'],
                'under_approval': ['review_approved', 'review_rejected'],
                'review_rejected': ['feedback_provided'],
            }
            if new_stage not in allowed_transitions.get(self.stage, []):
                raise ValueError(f"Cannot transition from {self.stage} to {new_stage}")
            self.stage = new_stage
            self.save()



    

* what we done here ?

This code defines a Django app's database models and associated functionality. It includes customizations for a User model, and models for managing companies, departments, employees, projects, and performance reviews. Here's a breakdown:

1. Custom User Management

CustomUserManager
A custom manager for creating User instances.
Provides methods:
create_user: Creates a standard user, ensuring an email is provided, and hashes the password.
create_superuser: Creates a superuser with elevated privileges (is_staff and is_superuser set to True).
User Model
Extends Django's AbstractBaseUser and PermissionsMixin to create a customizable user model.
Key Fields:
email: Used as the unique identifier (USERNAME_FIELD).
username: Optional, for legacy support.
role: Defines the user's role (Admin, Manager, Employee).
company: Links the user to a Company.
is_staff and is_active: Control access to the admin panel and user activity.
Custom user creation is handled by CustomUserManager.


2. Company, Department, and Employee Models

Company Model
Represents a company.
Key Field:
name: Name of the company.
Properties:
number_of_departments: Counts associated departments.
number_of_employees: Counts associated users (employees).
number_of_projects: Counts associated projects.
Department Model
Represents a department within a company.
Fields:
company: Foreign key to the company.
name: Name of the department.
Properties:
number_of_employees: Counts employees in the department.
number_of_projects: Counts projects within the department.
Employee Model
Represents an employee.
Key Fields:
user: One-to-one link with a User instance.
company and department: Foreign keys linking the employee to their organization.
designation: Job title.
hired_on: Date of hiring.
Properties:
days_employed: Calculates the number of days since hiring.
number_of_projects: Counts the projects assigned to the employee.

3. Project Management

Project Model
Represents a project within a company and department.
Fields:
company and department: Foreign keys linking the project.
name, description: Details of the project.
start_date, end_date: Project timeline.
assigned_employees: Many-to-many relationship with employees, enabling multiple employees to be assigned to the same project.

4. Performance Reviews

PerformanceReview Model
Represents performance evaluations for employees.
Fields:
employee: Foreign key linking the review to an employee.
stage: Current stage of the review process, with predefined choices (e.g., "pending_review", "feedback_provided").
review_date: When the review is conducted.
feedback: Text feedback for the review.
is_approved: Boolean indicating if the review is approved.
created_at, updated_at: Track creation and modification times.
Methods:
transition: Controls stage transitions based on allowed flows. Throws an error for invalid transitions.

5. Key Features

Custom User Model: Uses email as the primary authentication field and allows role-based differentiation.
Data Relationships:
Companies have departments and projects.
Departments have employees and projects.
Employees participate in multiple projects and have performance reviews.
Dynamic Properties: @property methods calculate values (e.g., number of employees in a department, days employed).
Validation and Business Logic:
Custom stage transitions in PerformanceReview.
Ensures proper superuser configuration.


## migrations 

now its time to create some tables in our database, most of which is already handled by django, we just need to run following commands:

(django_project)$`python manage.py makemigrations`

(django_project)$`python manage.py migrate`

Migrations for  `models.py`  involve the following steps:

1. Initial migration: When you first create the Django app and define the models, you need to generate an initial migration. This initial migration sets up the database tables for the models defined in `models.py`.

2. Creating tables for models: The initial migration creates the necessary database tables for the `User Accounts `, `Company`, `Department`, and `Employee` models. Each model corresponds to a separate table in the database.

3. Adding fields: If you add any new fields to the models or make modifications to existing fields, you will need to create a new migration to reflect those changes in the database schema. Django's migration system will generate the necessary migration files to add or alter the respective fields in the database tables.

4. Applying migrations: Once you have the migration files, you can apply the migrations to update the database schema. Django's migration system will execute the migration files, creating or modifying the database tables according to the changes made in `models.py`.

5. Handling relationships: In the case of the `User` model, which has foreign key relationships with  the `Employee`  models, the migration system will create the appropriate foreign key constraints in the database tables. This ensures referential integrity between the tables.

6. Data migration (optional): If you need to migrate existing data when making changes to the models, you can write data migration scripts. These scripts allow you to manipulate the data in the database during the migration process.

By following these steps, Django's migration system helps you keep the database schema in sync with the changes made to the models defined in `models.py`. It provides a structured and controlled way to manage the evolution of your database schema over time.

### admin

now we need to register our models in admin file in order in to use them. Put the following code in admin.py file

	from django.contrib import admin
    from .models import User, Company, Department, Employee, Project,PerformanceReview

    admin.site.register(User)
    admin.site.register(Company)
    admin.site.register(Department)
    admin.site.register(Employee)
    admin.site.register(Project)
    admin.site.register(PerformanceReview)


Here, .models means from this current directory import the User  and Company ,Department ,Employee,Project,PerformanceReview  model, from Models.py file and
for each model to register we need the command --> admin.site.register(model_name)

### server

Now, lets check that our model is being registered properly or not. First lets ensure that our server is running properly. Put the following commmand in terminal:

(django_project)$`python manage.py runserver`

* now open this link in your browser http://127.0.0.1:8000/

You will see a rocket there and a message saying, 'The install worked successfully! Congratulations!'

if yes, we didn't make any mistakes. Good !

* Now go to admin page by using this link http://127.0.0.1:8000/admin/


### views


    from rest_framework import viewsets
    from rest_framework.permissions import IsAuthenticated
    from .models import User, Company, Department, Employee, Project, PerformanceReview
    from .serializers import UserSerializer, CompanySerializer, DepartmentSerializer, EmployeeSerializer, ProjectSerializer, PerformanceReviewSerializer
    from .permissions import IsAdmin, IsManager, IsEmployee  # Custom permissions
    from django.shortcuts import render
    from .serializers import UserRegistrationSerializer, UserLoginSerializer
    from rest_framework.views import APIView
    from rest_framework.authentication import TokenAuthentication
    from rest_framework.permissions import AllowAny, IsAuthenticated
    from rest_framework.response import Response
    from rest_framework import status
    from rest_framework.exceptions import AuthenticationFailed
    from django.contrib.auth import authenticate
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from .utils import generate_access_token
    import jwt


    class UserViewSet(viewsets.ModelViewSet):
        queryset = User.objects.all()
        serializer_class = UserSerializer
        permission_classes = [IsAuthenticated, IsAdmin]  # Only Admin can view/edit users

    class CompanyViewSet(viewsets.ModelViewSet):
        queryset = Company.objects.all()
        serializer_class = CompanySerializer
        permission_classes = [IsAuthenticated, IsAdmin]  # Only Admin can view/edit companies

    class DepartmentViewSet(viewsets.ModelViewSet):
        queryset = Department.objects.all()
        serializer_class = DepartmentSerializer
        permission_classes = [IsAuthenticated, IsManager]  # Admin and Manager can manage departments

    class EmployeeViewSet(viewsets.ModelViewSet):
        queryset = Employee.objects.all()
        serializer_class = EmployeeSerializer
        permission_classes = [IsAuthenticated, IsEmployee]  # All roles can access employee info, with restrictions

        def get_queryset(self):
            queryset = super().get_queryset()
            if self.request.user.role == 'Employee':
                queryset = queryset.filter(user=self.request.user)  # Employees can only see their own profile
            return queryset

    class ProjectViewSet(viewsets.ModelViewSet):
        queryset = Project.objects.all()
        serializer_class = ProjectSerializer
        permission_classes = [IsAuthenticated, IsManager]  # Admins and Managers can manage projects

        def get_queryset(self):
            queryset = super().get_queryset()
            if self.request.user.role == 'Employee':
                queryset = queryset.filter(assigned_employees__user=self.request.user)  # Employees can only see their own projects
            return queryset

    class PerformanceReviewViewSet(viewsets.ModelViewSet):
        queryset = PerformanceReview.objects.all()
        serializer_class = PerformanceReviewSerializer
        permission_classes = [IsAuthenticated, IsManager]  # Admins and Managers can view/edit reviews







    class UserRegistrationAPIView(APIView):
        serializer_class = UserRegistrationSerializer
        authentication_classes = (TokenAuthentication,)
        permission_classes = (AllowAny,)

        def get(self, request):
            content = { 'message': 'Hello!' }
            return Response(content)

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                new_user = serializer.save()
                if new_user:
                    access_token = generate_access_token(new_user)
                    data = { 'access_token': access_token }
                    response = Response(data, status=status.HTTP_201_CREATED)
                    response.set_cookie(key='access_token', value=access_token, httponly=True)
                    return response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    class UserLoginAPIView(APIView):
        serializer_class = UserLoginSerializer
        authentication_classes = (TokenAuthentication,)
        permission_classes = (AllowAny,)

        def post(self, request):
            email = request.data.get('email', None)
            user_password = request.data.get('password', None)

            if not user_password:
                raise AuthenticationFailed('A user password is needed.')

            if not email:
                raise AuthenticationFailed('An user email is needed.')

            user_instance = authenticate(username=email, password=user_password)

            if not user_instance:
                raise AuthenticationFailed('User not found.')

            if user_instance.is_active:
                user_access_token = generate_access_token(user_instance)
                response = Response()
                response.set_cookie(key='access_token', value=user_access_token, httponly=True)
                response.data = {
                    'access_token': user_access_token
                }
                return response

            return Response({
                'message': 'Something went wrong.'
            })



    class UserViewAPI(APIView):
        authentication_classes = (TokenAuthentication,)
        permission_classes = (AllowAny,)

        def get(self, request):
            user_token = request.COOKIES.get('access_token')

            if not user_token:
                raise AuthenticationFailed('Unauthenticated user.')

            payload = jwt.decode(user_token, settings.SECRET_KEY, algorithms=['HS256'])

            user_model = get_user_model()
            user = user_model.objects.filter(user_id=payload['user_id']).first()
            user_serializer = UserRegistrationSerializer(user)
            return Response(user_serializer.data)



    class UserLogoutViewAPI(APIView):
        authentication_classes = (TokenAuthentication,)
        permission_classes = (AllowAny,)

        def get(self, request):
            user_token = request.COOKIES.get('access_token', None)
            if user_token:
                response = Response()
                response.delete_cookie('access_token')
                response.data = {
                    'message': 'Logged out successfully.'
                }
                return response
            response = Response()
            response.data = {
                'message': 'User is already logged out.'
            }
            return response

In our  `views.py` file, the following actions are performed:

The views.py file defines various views and APIs for managing users, companies, departments, employees, projects, and performance reviews in a Django REST Framework (DRF) based application. It uses viewsets, serializers, and custom permissions to control the access to these resources. Below is a detailed explanation of each component.

1. UserViewSet
This viewset manages the CRUD operations for the User model.

Permissions:
Only authenticated users with the IsAdmin permission can view or modify users (i.e., only Admin can manage users).
Queryset:
The queryset fetches all User objects.
Serializer:
It uses the UserSerializer to handle user data representation and validation.
2. CompanyViewSet
This viewset manages the CRUD operations for the Company model.

Permissions:
Only authenticated users with the IsAdmin permission can view or modify companies.
Queryset:
The queryset fetches all Company objects.
Serializer:
It uses the CompanySerializer to handle company data representation and validation.
3. DepartmentViewSet
This viewset manages the CRUD operations for the Department model.

Permissions:
Only authenticated users with the IsManager permission can view or modify departments.
Queryset:
The queryset fetches all Department objects.
Serializer:
It uses the DepartmentSerializer to handle department data representation and validation.
4. EmployeeViewSet
This viewset manages the CRUD operations for the Employee model.

Permissions:

All authenticated users with the IsEmployee permission can view employee data, but with restrictions:
Admins/Managers: Can access all employee records.
Employees: Can only access their own profile by filtering based on the logged-in user.
Queryset:

The queryset fetches all Employee objects.
Serializer:

It uses the EmployeeSerializer to handle employee data representation and validation.
5. ProjectViewSet
This viewset manages the CRUD operations for the Project model.

Permissions:
Only authenticated users with the IsManager permission can view or modify projects.
Queryset:
The queryset fetches all Project objects.
Serializer:
It uses the ProjectSerializer to handle project data representation and validation.
Employee-specific filtering:
Employees can only view projects they are assigned to by filtering the queryset based on the assigned_employees relationship.
6. PerformanceReviewViewSet
This viewset manages the CRUD operations for the PerformanceReview model.

Permissions:

Only authenticated users with the IsManager permission can view or modify performance reviews.
Queryset:

The queryset fetches all PerformanceReview objects.
Serializer:

It uses the PerformanceReviewSerializer to handle performance review data representation and validation.
7. UserRegistrationAPIView
This API view handles user registration.

Permissions:
This endpoint is open to any user (via AllowAny permission).
Authentication:
No authentication required for registration (it uses TokenAuthentication for other endpoints, but AllowAny for this one).
Process:
The POST method allows users to register by submitting data through the UserRegistrationSerializer.
If registration is successful, a JWT access token is generated for the new user using the generate_access_token function, and the token is sent in the response and set as a cookie.
8. UserLoginAPIView
This API view handles user login.

Permissions:

Open to any user (via AllowAny permission).
Authentication:

No authentication required initially (though authentication is done via username and password).
Process:

The POST method authenticates the user using the provided email and password (authenticate function).
If authentication is successful, a JWT access token is generated and sent in the response. The token is also set as a cookie for persistent login.
Error handling:

If credentials are incorrect, an AuthenticationFailed exception is raised.
9. UserViewAPI
This API view returns the details of the logged-in user.

Permissions:
Open to any user with a valid access token (via AllowAny permission).
Authentication:
The user must be authenticated, so the request must contain a valid JWT in the cookie.
Process:
The GET method retrieves the access_token from the cookies, decodes it using jwt.decode, and fetches the corresponding user from the database.
The user data is then serialized and returned in the response using the UserRegistrationSerializer.
10. UserLogoutViewAPI
This API view handles user logout.

Permissions:
Open to any user (via AllowAny permission).
Authentication:
No authentication required initially (though authentication is done via token).
Process:
The GET method retrieves the access_token from the cookies and deletes the cookie, effectively logging the user out.
A response is returned confirming the logout, or if the user is already logged out, it informs the user.
Key Components Used:
ViewSets: A DRF feature that allows for quick implementation of CRUD operations for models.
Permissions: Custom permissions (IsAdmin, IsManager, IsEmployee) control access to various resources based on the user’s role.
Token Authentication: Ensures that only authenticated users can access certain views.
JWT (JSON Web Token): Used for securely transmitting user authentication information and session management (via access tokens).
Serializer Classes: Transform model instances to JSON format and validate incoming data.
Custom Permissions: Restrictions based on user roles (Admin, Manager, Employee) determine which views users can access.
Summary of Viewset Functionality
UserViewSet: Admins manage users.
CompanyViewSet: Admins manage companies.
DepartmentViewSet: Admins and Managers manage departments.
EmployeeViewSet: All roles can view employee data, but employees are restricted to their own profile.
ProjectViewSet: Managers manage projects; employees see only their assigned projects.
PerformanceReviewViewSet: Managers manage performance reviews.
The API endpoints provide authentication, registration, login, logout, and secure access to user, company, department, employee, project, and performance review data.



### tests

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
        
        






what we do here ? :
Imports
from django.test import TestCase
Provides a test case class to write and run tests in Django.

Other imports (timezone, date, now)
Used for working with dates and times in Django.

from .models import ...
Imports the models (User, Company, Department, Employee, Project, and PerformanceReview) to test their functionality.

Test Class: ModelsTestCase
The class inherits from TestCase, which allows the setup of test data and the execution of assertions.

1. setUp Method
Runs before each test method to set up the necessary test data.
Creates instances of models:
A Company named "TechCorp".
A Department called "Development" within the company.
A User associated with the company.
An Employee linked to the user, company, and department.
A Project assigned to the department and employee.
A PerformanceReview linked to the employee.
2. Test Methods
Each method validates specific aspects of the models' behavior. The assertEqual and assertTrue methods are used to verify expected outcomes.

test_user_creation
Ensures the User instance is created with the correct email, password, and role.

test_company_creation
Verifies that the Company has the expected number of departments and employees.

test_department_creation
Ensures the Department has the correct number of employees and projects.

test_employee_creation
Checks that the Employee is created with the correct details, including email, designation, and days employed (calculated using timezone.now()).

test_project_creation
Verifies the Project is created and assigned to the correct employee.

test_performance_review_creation
Ensures the PerformanceReview has the correct stage, feedback, and approval status.

test_performance_review_stage_transition
Tests the ability to transition between review stages:

Allows valid transitions (e.g., to review_scheduled).
Raises an exception for invalid transitions (e.g., directly to review_approved).
test_company_relationships
Checks that the company has the correct number of related users, departments, and projects.

test_department_relationships
Verifies the department has the correct number of related employees and projects.

Purpose
These tests ensure the correct behavior and relationships of the models, particularly:

Object creation and field values.
Relationships between models (e.g., company to departments, department to employees).
Custom behaviors like stage transitions in the PerformanceReview.
By running this test suite, developers can catch errors in model logic or relationships early in development.




### urls
we create urls.py file to confic our urls-endpoints 


	
    from django.urls import path, include
    from rest_framework.routers import DefaultRouter
    from .views import UserViewSet, CompanyViewSet, DepartmentViewSet, EmployeeViewSet, ProjectViewSet, PerformanceReviewViewSet
    from rest_framework_simplejwt import views as jwt_views
    from company.views import (
        UserRegistrationAPIView,
        UserLoginAPIView,
        UserViewAPI,
        UserLogoutViewAPI
    )
    router = DefaultRouter()

    router.register(r'users', UserViewSet, basename='user')
    router.register(r'companies', CompanyViewSet, basename='company')
    router.register(r'departments', DepartmentViewSet, basename='department')
    router.register(r'employees', EmployeeViewSet, basename='employee')
    router.register(r'projects', ProjectViewSet, basename='project')
    router.register(r'performance-reviews', PerformanceReviewViewSet, basename='performance-review')

    urlpatterns = [
        path('user/register/', UserRegistrationAPIView.as_view()),
        path('user/login/', UserLoginAPIView.as_view()),
        path('user/', UserViewAPI.as_view()),
        path('user/logout/', UserLogoutViewAPI.as_view()),
        path('', include(router.urls)),  # Include all the generated URLs
    ]



* what we done here ? 

    This Django project uses Django REST Framework (DRF) for API routing, providing endpoints for handling user authentication, registration, profiles, and CRUD operations for models like User, Company, Department, Employee, Project, and PerformanceReview.

    URL Structure Overview
    User Authentication and Management:

        /user/register/ (POST): Registers a new user.
        /user/login/ (POST): Logs in an existing user.
        /user/ (GET): Retrieves the current user's profile.
        /user/logout/ (GET): Logs out the current user by deleting the authentication token.
    CRUD Operations via Viewsets: The following resources use DRF's DefaultRouter to automatically generate CRUD operations for:

        /users/: User-related operations (e.g., create, read, update, delete).
        /companies/: Company-related operations.
        /departments/: Department-related operations.
        /employees/: Employee-related operations.
        /projects/: Project-related operations.
        /performance-reviews/: Performance review-related operations.
    Custom User Views:
        User Registration (/user/register/): Allows new users to register.
        User Login (/user/login/): Allows existing users to log in.
        User Profile (/user/): Retrieves the authenticated user's profile.
        User Logout (/user/logout/): Logs the user out and deletes the authentication token.
    Generated URLs with Viewsets:
        /users/: Lists, creates, and manages users.
        /companies/: Lists, creates, and manages companies.
        /departments/: Lists, creates, and manages departments.
        /employees/: Lists, creates, and manages employees.
        /projects/: Lists, creates, and manages projects.
        /performance-reviews/: Lists, creates, and manages performance reviews.
    Routing and Permissions:
    Permissions: The views and viewsets include specific permissions such as IsAuthenticated, IsAdmin, IsManager, and IsEmployee to ensure that only authorized users can access or modify resources.
    DefaultRouter: Automatically generates routes for all registered viewsets, supporting full CRUD operations for each resource.
    This API structure facilitates the management of users, companies, departments, employees, projects, and performance reviews in a secure and organized manner.


Before putting some code in this file go to DRF folder and open urls.py file. Update this file in the follwing manner

	from django.contrib import admin
    from django.urls import path,include
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
    )

    urlpatterns = [
        path('admin/', admin.site.urls),
        path('',include('company.urls')),
        path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
        path(
            'api/docs/',
            SpectacularSwaggerView.as_view(url_name='api-schema'),
            name='api-docs',
        )
    ]



### Swagger_UI


Swagger UI is a powerful tool that provides an interactive web interface for documenting and testing RESTful APIs. It automatically generates a visual and interactive API documentation from your API's schema. Here’s why it's beneficial to use Swagger UI in Django projects:

1. Interactive API Documentation
    Swagger UI provides an interactive documentation interface that allows developers to explore, test, and understand API endpoints directly from the browser. It lets users:

        View a list of available API endpoints (GET, POST, PUT, DELETE, etc.).
        See the required parameters and request body formats.
        Test API calls directly from the interface (e.g., sending a POST request or retrieving data with GET).
        This helps both backend developers and API consumers (like frontend developers or third-party developers) interact with the API more easily.

2. Standardized API Documentation
    Swagger UI provides a standardized format for API documentation. This ensures that the documentation follows a consistent structure and makes it easier for developers to quickly understand the API’s capabilities. It helps:

        Improve the clarity of API documentation.
        Allow developers to automatically generate and update documentation when API models or views are modified.
        Maintain clear communication about API functionality across different teams.
3. Simplifies Development & Debugging
    With Swagger UI, developers can test and debug their APIs without needing to write custom code or use tools like Postman or cURL. This is helpful for:

        Quick testing of API endpoints to ensure that they work as expected.
        Identifying issues or bugs early in the development process by interacting directly with the API through Swagger UI.
        Verifying request and response formats, ensuring they align with what the API is supposed to return.
4. Auto-generates API Docs
    Swagger UI is often paired with OpenAPI (formerly Swagger) specification, which allows it to automatically generate API documentation from code annotations or a predefined schema. This reduces the need for manually writing documentation, which is:

        Time-saving: Automatically generates documentation as the API is built or modified.
        Accurate: Reduces errors by generating up-to-date documentation based on the actual API code.
5. Improves Collaboration
    Swagger UI makes it easier for cross-functional teams (backend, frontend, QA, and even non-technical stakeholders) to understand the API. This leads to:

        Better collaboration: Team members can see what API calls are available and test them without needing to understand the code.
        Clearer API specifications: Frontend developers can interact with and test APIs without waiting for backend developers to provide sample requests.
6. Great for API Versioning
    As APIs evolve, Swagger UI can accommodate versioning by allowing the specification to be versioned as well. This helps:

        Provide documentation for multiple versions of the API.
        Let developers test endpoints for different versions directly from the UI.
7. Easy Integration with Django
    Using Swagger UI with Django is easy, especially when combined with Django REST Framework and libraries like drf-yasg or drf-swagger. These libraries can automatically generate Swagger-compatible OpenAPI documentation from your Django REST API code.

8. Helps with API Security
    Swagger UI can be used to test and review security features by specifying authentication (e.g., OAuth2, API keys, etc.) and observing how the API handles security protocols. This enables:

    Security testing by simulating requests with various levels of authentication.
    Review of permissions and access control to verify that endpoints are secure.
9. Supports Different Formats
    Swagger UI allows the API to be described in multiple formats, such as JSON or YAML, which can be useful for:

    Importing/exporting API definitions between different environments or tools.
    Collaborating with other teams or using third-party services that rely on the OpenAPI specification.
In Summary:
    Swagger UI makes the development, testing, and maintenance of APIs easier by:

    Providing interactive documentation for users.
    Allowing easy testing of API calls.
    Enabling standardized API documentation.
    Reducing manual documentation efforts.
    Supporting collaboration between development teams.
    By using Swagger UI, Django projects can have well-documented, easily testable, and accessible APIs, which streamlines the development process and improves the overall user experience for API consumers.





### Logging

    import os 
    LOGGING_DIR = os.path.join(BASE_DIR, 'logs')  # Define the logs directory

    # Make sure the directory exists
    if not os.path.exists(LOGGING_DIR):
        os.makedirs(LOGGING_DIR)

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': os.path.join(LOGGING_DIR, 'error.log'),
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'ERROR',
                'propagate': True,
            },
        },
    }


what we do this ?

This code is part of the logging configuration for a Django project. Here's a breakdown of what it does:

Directory Setup for Logs:

LOGGING_DIR = os.path.join(BASE_DIR, 'logs'): Defines the directory where logs will be stored. BASE_DIR is typically the root directory of the Django project, and the logs will be saved in a folder named logs within that directory.
if not os.path.exists(LOGGING_DIR): os.makedirs(LOGGING_DIR): Checks if the logs directory exists. If not, it creates the directory to ensure there's a valid path to store logs.
Logging Configuration:

LOGGING is a dictionary that defines the configuration for logging in Django.
Inside the LOGGING dictionary:

Handlers:
Console Handler:
This sends log messages to the console (stdout) with a severity level of DEBUG or higher.
It's useful for development or debugging as it displays logs in the terminal.
File Handler:
This logs messages to a file. In this case, it writes error-level (ERROR) and higher logs to a file named error.log inside the logs directory.
Loggers:
There is a logger specifically for Django's internal logging ('django').
This logger will handle logs with ERROR level or higher and will use both the console and file handlers to record the logs.
propagate: True means that the logs from the Django logger will propagate to higher-level loggers (e.g., root logger).
Summary:
The code ensures the existence of a logs directory.
It sets up logging so that debug messages are shown in the console, and error messages are written to a file (error.log).
This configuration helps monitor application behavior during development and production, especially for catching errors.
