from django.shortcuts import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

class LoginCheckMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        modulename = view_func.__module__
        user = request.user

        # Allow access to login and dologin pages without redirecting
        if request.path == reverse("login") or request.path == reverse('dologin'):
            return None

        # Check if the user is authenticated
        if user.is_authenticated:
            # Admin user (user_type == '1')
            if user.user_type == '1':
                if modulename == 'student_management_app.HodViews' or modulename == 'student_management_app.views' or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('admin_home'))

            # Staff user (user_type == '2')
            elif user.user_type == '2':
                if modulename == 'student_management_app.StaffViews' or modulename == 'student_management_app.views' or modulename == "django.views.static":
                    pass
                else:
                    return HttpResponseRedirect(reverse('staff_home'))

            # Student user or any other user_type
            else:
                return HttpResponseRedirect(reverse('login'))

        # If user is not authenticated and not trying to log in, redirect to login
        else:
            return HttpResponseRedirect(reverse('login'))
