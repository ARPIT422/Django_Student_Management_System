from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from student_management_app.models import CustomerUser

class UserModel(UserAdmin):
    pass
admin.site.register(CustomerUser,UserModel)