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


