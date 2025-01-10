
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
