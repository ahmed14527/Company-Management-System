from django.contrib import admin
from .models import User, Company, Department, Employee, Project,PerformanceReview

admin.site.register(User)
admin.site.register(Company)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Project)
admin.site.register(PerformanceReview)
