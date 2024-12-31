# courses/context_processors.py
from .models import Course, TestResult

def user_stats(request):
    if request.user.is_authenticated:
        return {
            'total_courses': Course.objects.filter(author=request.user).count(),
            'total_tests': TestResult.objects.filter(user=request.user).count(),
        }
    return {}