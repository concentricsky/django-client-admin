from functools import wraps
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import login
from django.utils.translation import ugettext as _

def staff_member_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a staff
    member, displaying the login page if necessary.

    This is an adaptation of django.contrib.admin.views.decorators.staff_member_required
    that tries to grab defaults from contrib.admin.site before using hard-coded values.
    """
    @wraps(view_func)
    def _checklogin(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            # The user is valid. Continue to the admin page.
            return view_func(request, *args, **kwargs)

        assert hasattr(request, 'session'), "The Django admin requires session middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.sessions.middleware.SessionMiddleware'."

        extra_context = {
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            REDIRECT_FIELD_NAME: request.get_full_path(),
        }
        extra_context = dict(extra_context.items() + getattr(admin.site, 'extra_context', {}).items())

        defaults = {
            'template_name': getattr(admin.site, 'login_template', 'admin/login.html'),
            'authentication_form': getattr(admin.site, 'login_form', AdminAuthenticationForm),
            'extra_context': extra_context,
        }
        return login(request, **defaults)
    return _checklogin

