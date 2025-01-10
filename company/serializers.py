from rest_framework import serializers
from .models import User, Company, Department, Employee, Project, PerformanceReview
from django.contrib.auth import get_user_model

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'username', 'is_active', 'is_staff', 'role', 'company']

# Serializer for the Company model
class CompanySerializer(serializers.ModelSerializer):
    number_of_departments = serializers.IntegerField(read_only=True)
    number_of_employees = serializers.IntegerField(read_only=True)
    number_of_projects = serializers.IntegerField(read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'name', 'number_of_departments', 'number_of_employees', 'number_of_projects']

# Serializer for the Department model
class DepartmentSerializer(serializers.ModelSerializer):
    number_of_employees = serializers.IntegerField(read_only=True)
    number_of_projects = serializers.IntegerField(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'company', 'number_of_employees', 'number_of_projects']

# Serializer for the Employee model
class EmployeeSerializer(serializers.ModelSerializer):
    days_employed = serializers.IntegerField(read_only=True)
    number_of_projects = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'company', 'department', 'email_address', 'mobile_number', 
                  'address', 'designation', 'hired_on', 'days_employed', 'number_of_projects']

# Serializer for the Project model
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'company', 'department', 'assigned_employees']

# Serializer for the PerformanceReview model
class PerformanceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceReview
        fields = ['id', 'employee', 'stage', 'review_date', 'feedback', 'approval_status', 'created_at', 'updated_at']






class UserRegistrationSerializer(serializers.ModelSerializer):
	password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	class Meta:
		model = get_user_model()
		fields = ['email', 'username', 'password']

	def create(self, validated_data):
		user_password = validated_data.get('password', None)
		db_instance = self.Meta.model(email=validated_data.get('email'), username=validated_data.get('username'))
		db_instance.set_password(user_password)
		db_instance.save()
		return db_instance



class UserLoginSerializer(serializers.Serializer):
	email = serializers.CharField(max_length=100)
	username = serializers.CharField(max_length=100, read_only=True)
	password = serializers.CharField(max_length=100, min_length=8, style={'input_type': 'password'})
	token = serializers.CharField(max_length=255, read_only=True)