from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

def creator_required(view_func):
    """
    Decorator to ensure user is logged in and is a creator/staff member.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please log in with creator credentials to access the management dashboard.")
            return redirect(f"{reverse('dashboard:login')}?next={request.path}")
        if not request.user.is_staff:
            messages.error(request, "Access restricted. Creator or administrator privileges required.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
