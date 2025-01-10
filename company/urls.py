
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
router.register('users', UserViewSet, basename='user')
router.register('companies', CompanyViewSet, basename='company')
router.register('departments', DepartmentViewSet, basename='department')
router.register('employees', EmployeeViewSet, basename='employee')
router.register('projects', ProjectViewSet, basename='project')
router.register('performance-reviews', PerformanceReviewViewSet, basename='performance-review')

urlpatterns = [
    path('user/register/', UserRegistrationAPIView.as_view()),
	path('user/login/', UserLoginAPIView.as_view()),
	path('user/', UserViewAPI.as_view()),
	path('user/logout/', UserLogoutViewAPI.as_view()),
    path('', include(router.urls)),  # Include all the generated URLs
]
