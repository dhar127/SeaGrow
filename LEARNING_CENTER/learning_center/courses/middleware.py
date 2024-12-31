from django.urls import reverse
from django.shortcuts import redirect

class ProfileCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            allowed_paths = [
                reverse('courses:dashboard'),
                reverse('courses:logout'),
                reverse('courses:course_list'),
                reverse('courses:test_list'),
                # Add the test-related paths
                request.path if request.path.startswith('/test/') else None,  # Allow all test URLs
            ]
            # Remove None values from the list
            allowed_paths = [path for path in allowed_paths if path is not None]
            
            # Check if the current path starts with any allowed path
            is_allowed = any(
                request.path == path or 
                (path.endswith('/test/') and request.path.startswith(path)) 
                for path in allowed_paths
            )
            
            if not is_allowed:
                return redirect('courses:dashboard')
                
        return self.get_response(request)