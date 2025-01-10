# views.py
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