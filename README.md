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
            ('Pending Review', 'Pending Review'),
            ('Review Scheduled', 'Review Scheduled'),
            ('Feedback Provided', 'Feedback Provided'),
            ('Under Approval', 'Under Approval'),
            ('Review Approved', 'Review Approved'),
            ('Review Rejected', 'Review Rejected'),
        ]
        
        employee = models.ForeignKey('Employee', related_name='performance_reviews', on_delete=models.CASCADE)
        stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='Pending Review')
        review_date = models.DateTimeField(null=True, blank=True)
        feedback = models.TextField(null=True, blank=True)
        approval_status = models.BooleanField(default=False)  # True for approved, False for rejected
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"Performance Review for {self.employee.name} - {self.stage}"

        def save(self, *args, **kwargs):
            if self.stage == 'Review Approved' and self.approval_status is False:
                raise ValueError("Review cannot be marked as approved if not approved by manager.")
            super().save(*args, **kwargs)

    

* what we done here ?

This code defines several models in Django for managing a company system. It includes a custom user model with roles, company, department, employee, project, and performance review models. Below is an explanation of each component and its functionality:

1. Custom User Model (User)
Purpose: The User model extends Django's AbstractBaseUser to provide a custom authentication system, using email as the unique identifier for users instead of the default username field.

Fields:

user_id: Auto-incremented primary key for user identification.
email: The unique email address used for user identification.
username: An optional field for legacy support, not used as a unique identifier.
is_active: A boolean flag to mark if the user is active.
is_staff: A boolean flag indicating if the user is a staff member.
date_joined: Date when the user joined the system.
role: A choice field to define the user's role within the company (Admin, Manager, or Employee).
company: A foreign key that links the user to a specific company.
Methods:

__str__(self): Returns the user’s email when the object is represented as a string.
Manager:

The CustomUserManager class provides methods to create a user and a superuser. The create_user method ensures that the user is created with an email and password, and create_superuser ensures that a superuser has the is_staff and is_superuser flags set to True.
2. Company Model (Company)
Purpose: Represents a company with details about the company's employees, departments, and projects.

Fields:

name: The name of the company.
Properties:

number_of_departments: Returns the number of departments within the company by counting the related departments.
number_of_employees: Returns the number of users (employees) associated with the company.
number_of_projects: Returns the number of projects associated with the company.
Methods:

__str__(self): Returns the name of the company.
3. Department Model (Department)
Purpose: Represents a department within a company, which can have employees and projects.

Fields:

company: A foreign key to the Company model, indicating which company the department belongs to.
name: The name of the department.
Properties:

number_of_employees: Returns the number of employees in the department.
number_of_projects: Returns the number of projects within the department.
Methods:

__str__(self): Returns the name of the department.
4. Employee Model (Employee)
Purpose: Represents an employee within a company, linking the user to the company and department.

Fields:

user: A one-to-one relationship with the User model, linking the employee to the user.
company: A foreign key to the Company model, indicating which company the employee works for.
department: A foreign key to the Department model, indicating which department the employee belongs to.
email_address: The employee's email address.
mobile_number: The employee's mobile number (optional).
address: The employee's address (optional).
designation: The employee's job title/designation.
hired_on: The date the employee was hired.
Properties:

days_employed: Returns the number of days the employee has been employed (calculated based on the hired_on date).
number_of_projects: Returns the number of projects assigned to the employee.
Methods:

__str__(self): Returns the employee’s username and designation.
5. Project Model (Project)
Purpose: Represents a project within a company, which may involve multiple departments and employees.

Fields:

company: A foreign key to the Company model, indicating which company the project belongs to.
department: A foreign key to the Department model, indicating which department is associated with the project.
name: The name of the project.
description: A description of the project.
start_date: The start date of the project.
end_date: The optional end date of the project.
assigned_employees: A many-to-many relationship to the Employee model, indicating the employees working on the project.
Methods:

__str__(self): Returns the name of the project.
6. Performance Review Model (PerformanceReview)
Purpose: Represents a performance review for an employee, tracking the review's stage and approval status.

Fields:

employee: A foreign key to the Employee model, indicating which employee the review is for.
stage: A choice field that tracks the status of the review (e.g., 'Pending Review', 'Review Scheduled', etc.).
review_date: The date and time the review is scheduled or completed.
feedback: Optional feedback provided during the review.
approval_status: A boolean flag indicating if the review has been approved (True) or rejected (False).
created_at: The date and time the performance review was created.
updated_at: The date and time the performance review was last updated.
Methods:

__str__(self): Returns a string representation of the performance review, including the employee’s name and review stage.
save(self, *args, **kwargs): Custom save method that raises an error if the review is marked as approved but not approved by the manager.

These models define the structure and relationships between different entities in your Django application. They can be used to create database tables and perform operations on the data stored in those tables, such as creating, updating, and querying records.


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



what we do here ? :
 This code defines two sets of tests using Django’s TestCase class to ensure that the application’s models and serializers are functioning as expected. Here's a breakdown of what is happening in both parts of the code:

    1. ModelTests Class
        This class contains tests for various model properties and methods defined in the Django models (Company, Department, Employee, PerformanceReview).

    setUp Method:
    Purpose: This method is executed before each test case to set up any data required for the tests.
    Data Creation:
    A Company instance (Tech Corp) is created.
    A Department instance (Engineering) is created and associated with the Company.
    A User instance (testuser) is created using Django’s get_user_model(), and this user is then associated with an Employee instance (Developer).
    Test Cases in ModelTests:
    test_number_of_departments_in_company:

    Purpose: Tests the number_of_departments property on the Company model.
    Expected Result: As one department (Engineering) has been created under the company (Tech Corp), the property should return 1.
    test_number_of_employees_in_department:

    Purpose: Tests the number_of_employees property on the Department model.
    Expected Result: As one employee (testuser) has been associated with the department (Engineering), the property should return 1.
    test_days_employed:

    Purpose: Tests the days_employed property on the Employee model. This property calculates the number of days the employee has been employed since their hired_on date.
    Expected Result: As the employee was hired on January 1, 2020, this test checks that the days_employed property returns a positive number greater than 0 (i.e., the employee has been employed for some days).
    test_performance_review_approval_validation:

    Purpose: Tests the custom validation in the PerformanceReview model's save() method. The save() method raises an error if the review's stage is "Review Approved" but the approval_status is set to False.
    Expected Result: This test checks that trying to save a performance review with "Review Approved" and approval_status=False will raise a ValueError.
    2. PerformanceReviewSerializerTest Class
    This class contains tests for the PerformanceReviewSerializer, which is responsible for serializing and deserializing the PerformanceReview model.

    setUp Method:
    Similar to the previous class, the setUp() method is used to prepare the necessary data:
    A Company, Department, User, and Employee are created.
    Test Cases in PerformanceReviewSerializerTest:
    test_performance_review_valid_data:

    Purpose: Tests the PerformanceReviewSerializer with valid data.
    Expected Result: The serializer should be valid when provided with a stage of "Review Scheduled" and approval_status=True. The test checks that the serializer correctly serializes the data without errors.
    test_performance_review_invalid_approval_status:

    Purpose: Tests the PerformanceReviewSerializer with invalid data, specifically when the approval_status is False while the stage is "Review Approved".
    Expected Result: The serializer should be invalid in this case, and the error message should include a non_field_errors entry with the message: "Review cannot be marked as approved if not approved by manager."
    Why We Use These Tests:
    Data Integrity: The tests help ensure that the logic behind the model properties (such as counting departments or employees) and validation rules (e.g., preventing invalid performance review data) are working as expected.
    Reliability: Automated tests help identify issues early in the development cycle, improving the stability of the application.
    Regression Testing: These tests provide a safety net to ensure that new changes don't break existing functionality.
    Confidence in Models and Serializers: By testing both the models and serializers, we confirm that the data structure and the data transformation layers (serialization/deserialization) behave correctly.
    In summary, these test cases verify that the business logic in the models and the data validation in the serializers are correctly implemented, ensuring the application behaves as intended.




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