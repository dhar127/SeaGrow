from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpResponseForbidden, JsonResponse
from .models import Course, Question, TestResult, Topic, QuestionResponse
from .forms import CourseForm, QuestionForm
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm  # Add this import

from . import sample_questions  # Add this import at the top
from .utils import search_youtube_videos
from .models import CourseVideo


def home(request):
    """Home page view showing featured courses and basic statistics."""
    courses = Course.objects.all().order_by('-created_at')[:5]  # Get latest 5 courses
    total_users = Course.objects.aggregate(total_enrolled=Count('students'))
    context = {
        'courses': courses,
        'total_users': total_users['total_enrolled'],
        'featured_courses': Course.objects.filter(is_featured=True)[:3]
    }
    return render(request, 'courses/home.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful. Please login.')
            return redirect('courses:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'courses/register.html', {'form': form})

@login_required
def dashboard(request):
    """User dashboard showing personal statistics and progress."""
    user_stats = {
        'total_tests': TestResult.objects.filter(user=request.user).count(),
        'avg_score': TestResult.objects.filter(user=request.user).aggregate(Avg('score'))['score__avg'] or 0,
        'courses_created': Course.objects.filter(author=request.user).count(),
        'courses_enrolled': Course.objects.filter(students=request.user).count(),
        'recent_results': TestResult.objects.filter(user=request.user).order_by('-completed_at')[:5]
    }
    return render(request, 'courses/dashboard.html', {'stats': user_stats})

@login_required
def course_list(request):
    """Display list of all available courses with filtering options and YouTube videos."""
    courses = Course.objects.all().order_by('-created_at')
    videos = []
    selected_topic = None
    
    # Get topic from query parameters
    topic = request.GET.get('topic')
    if topic:
        try:
            selected_topic = dict(Course.TOPICS).get(topic)
            # Search YouTube videos for the selected topic
            search_query = f"{selected_topic} programming tutorial"
            print(f"Searching for: {search_query}")  # Debug print
            videos = search_youtube_videos(search_query)
        except Exception as e:
            print(f"Error in course_list view: {str(e)}")
            videos = []
    
    # Filter by difficulty if specified
    difficulty = request.GET.get('difficulty')
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
        
    context = {
        'courses': courses,
        'topics': Course.TOPICS,
        'difficulties': Course.DIFFICULTIES,
        'videos': videos,
        'selected_topic': selected_topic
    }
    return render(request, 'courses/course_list.html', context)

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    is_enrolled = request.user in course.students.all()
    
    # Search for related YouTube videos
    search_query = f"{course.title} {course.topic} tutorial"
    videos = search_youtube_videos(search_query)
    
    context = {
        'course': course,
        'is_enrolled': is_enrolled,
        'total_students': course.students.count(),
        'topics': course.topics.all(),
        'author': course.author,
        'videos': videos
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def load_more_videos(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    page = int(request.GET.get('page', 1))
    offset = (page - 1) * 5  # 5 videos per page
    
    search_query = f"{course.title} {course.topic} tutorial"
    videos = search_youtube_videos(search_query, max_results=5)
    
    return JsonResponse({'videos': videos})

@login_required
def create_course(request):
    """Create a new course."""
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = CourseForm()
    return render(request, 'courses/create_course.html', {'form': form})

@login_required
def edit_course(request, course_id):
    """Edit an existing course."""
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is the course author
    if course.author != request.user:
        return HttpResponseForbidden("You don't have permission to edit this course.")
        
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('courses:course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'courses/edit_course.html', {'form': form, 'course': course})

@login_required
def test_list(request):
    topics = Course.TOPICS
    levels = Question.LEVELS
    questions = None
    selected_topic = None
    selected_difficulty = None
    
    # Get filters from query parameters
    topic = request.GET.get('topic')
    difficulty = request.GET.get('difficulty')
    
    print(f"Topic: {topic}, Difficulty: {difficulty}")  # Debug print
    
    if topic:
        selected_topic = dict(Course.TOPICS).get(topic)
        if not difficulty:
            difficulty = 'beginner'
        selected_difficulty = difficulty
        
        # Debug print
        print(f"Selected Topic: {selected_topic}, Selected Difficulty: {selected_difficulty}")
        
        for question_set in sample_questions.QUESTIONS:
            if question_set['topic'].lower() == topic.lower() and question_set['level'].lower() == difficulty.lower():
                questions = question_set['questions']
                print(f"Found {len(questions)} questions")  # Debug print
                break
    
    context = {
        'topics': topics,
        'levels': levels,
        'questions': questions,
        'selected_topic': selected_topic,
        'selected_difficulty': selected_difficulty,
        'topic': topic,
        'difficulty': difficulty,
        'user_results': TestResult.objects.filter(user=request.user)
    }
    return render(request, 'courses/test_list.html', context)

def test_view(request, topic, level):
    questions = Question.objects.filter(topic=topic, level=level)
    user_answers = {}

    if request.method == 'POST':
        for question in questions:
            user_answers[question.id] = request.POST.get(f'q{question.id}')

    context = {
        'questions': questions,
        'topic': topic,
        'difficulty': level,
        'user_answers': user_answers,
    }
    return render(request, 'courses/test_list.html', context)


# views.py

@login_required
def take_test(request, topic, level):
    """
    Handle both displaying the test and processing results.
    """
    # Get all questions for this topic and level
    questions = Question.objects.filter(topic=topic, level=level)
    
    if request.method == 'POST':
        correct_answers = 0
        total_questions = len(questions)
        
        # Process each question's answer
        for question in questions:
            answer_key = f'question_{question.id}'
            selected_answer = request.POST.get(answer_key)
            
            if selected_answer:
                if int(selected_answer) == question.correct_answer:
                    correct_answers += 1
                
                # Create or update QuestionResponse
                QuestionResponse.objects.create(
                    user=request.user,
                    question=question,
                    selected_answer=int(selected_answer)
                )
        
        # Calculate score
        score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Create TestResult
        test_result = TestResult.objects.create(
            user=request.user,
            topic=topic,
            level=level,
            score=score_percentage,
            total_questions=total_questions,
            correct_answers=correct_answers
        )
        
        context = {
            'score_percentage': score_percentage,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'topic': topic,
            'level': level
        }
        
        return render(request, 'courses/test_result.html', context)
    
    # For GET request, display the test
    context = {
        'questions': questions,
        'topic': topic,
        'level': level,
    }
    return render(request, 'courses/take_test.html', context)

@login_required
def test_detail(request, result_id):
    """Display test results and detailed analysis."""
    result = get_object_or_404(TestResult, id=result_id, user=request.user)
    
    context = {
        'result': result,
        'score_percentage': (result.score / result.total_questions) * 100,
        'topic': result.topic,
        'level_display': dict(Question.LEVELS)[result.level],
        'previous_attempts': TestResult.objects.filter(
            user=request.user,
            topic=result.topic,
            level=result.level
        ).exclude(id=result_id)
    }
    return render(request, 'courses/test_detail.html', context)

@login_required
def user_progress(request):
    """Display overall user progress across all topics and levels."""
    test_results = TestResult.objects.filter(user=request.user).order_by('-completed_at')
    
    # Calculate overall statistics
    total_tests = test_results.count()
    avg_score = test_results.aggregate(Avg('score'))['score__avg'] or 0
    
    # Get progress by topic
    topic_progress = (
        test_results.values('topic')
        .annotate(
            attempts=Count('id'),
            avg_score=Avg('score'),
            best_score=Max('score'),
            last_attempt=Max('completed_at')
        )
        .order_by('-last_attempt')
    )
    
    # Get recent results
    recent_results = test_results[:5]
    
    context = {
        'total_tests': total_tests,
        'avg_score': avg_score,
        'topic_progress': topic_progress,
        'recent_results': recent_results,
    }
    
    return render(request, 'courses/user_progress.html', context)

@login_required
def topic_progress(request, topic_id):
    """Display user progress for a specific topic."""
    topic = get_object_or_404(Topic, id=topic_id)
    results = TestResult.objects.filter(
        user=request.user,
        topic=topic
    ).order_by('level', '-completed_at')
    
    # Calculate statistics for each difficulty level
    level_stats = {}
    for level, level_name in Question.LEVELS:
        level_results = results.filter(level=level)
        level_stats[level] = {
            'attempts': level_results.count(),
            'avg_score': level_results.aggregate(Avg('score'))['score__avg'] or 0,
            'best_score': level_results.order_by('-score').first(),
            'recent_results': level_results[:3]
        }
    
    context = {
        'topic': topic,
        'level_stats': level_stats,
        'overall_progress': sum(stat['avg_score'] for stat in level_stats.values()) / len(Question.LEVELS) if level_stats else 0
    }
    return render(request, 'courses/topic_progress.html', context)

@login_required
def manage_course_videos(request, course_id):
    """Manage videos for a specific course."""
    course = get_object_or_404(Course, id=course_id)
    
    if course.author != request.user:
        return HttpResponseForbidden("You don't have permission to manage this course's videos.")
    
    if request.method == 'POST':
        video_query = request.POST.get('video_query')
        if video_query:
            search_results = search_youtube_videos(f"{course.title} {video_query}")
            return render(request, 'courses/video_search_results.html', {
                'course': course,
                'search_results': search_results
            })
        
        # Handle video selection
        video_id = request.POST.get('video_id')
        video_data = {
            'title': request.POST.get('title'),
            'thumbnail_url': request.POST.get('thumbnail'),
            'duration': request.POST.get('duration'),
            'channel_name': request.POST.get('channel'),
            'order': CourseVideo.objects.filter(course=course).count()
        }
        
        if video_id:
            CourseVideo.objects.create(
                course=course,
                video_id=video_id,
                **video_data
            )
            messages.success(request, 'Video added successfully!')
            return redirect('courses:manage_course_videos', course_id=course.id)
    
    videos = course.videos.all()
    return render(request, 'courses/manage_videos.html', {
        'course': course,
        'videos': videos
    })

@login_required
def delete_course_video(request, video_id):
    """Delete a course video."""
    video = get_object_or_404(CourseVideo, id=video_id)
    
    if video.course.author != request.user:
        return HttpResponseForbidden("You don't have permission to delete this video.")
    
    video.delete()
    messages.success(request, 'Video removed successfully!')
    return redirect('courses:manage_course_videos', course_id=video.course.id)

@login_required
def submit_test(request, topic, difficulty):
    print(f"Submit test called with topic: {topic}, difficulty: {difficulty}")
    
    if request.method == 'POST':
        # Get questions from the sample questions
        questions = None
        for question_set in sample_questions.QUESTIONS:
            if question_set['topic'].lower() == topic.lower() and question_set['level'].lower() == difficulty.lower():
                questions = question_set['questions']
                break
        
        if not questions:
            messages.error(request, "No questions found for this topic and difficulty.")
            return redirect('courses:test_list')
        
        # Initialize variables before processing
        correct_answers = 0
        total_questions = len(questions)
        
        # Process each question
        for i, question in enumerate(questions, 1):
            answer_key = f'question_{i}'
            selected_answer = request.POST.get(answer_key)
            print(f"Processing question {i}, selected answer: {selected_answer}")
            
            if selected_answer and selected_answer.isdigit():
                if int(selected_answer) == question['correct_answer']:
                    correct_answers += 1
        
        # Calculate score percentage - moved inside the POST block
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        print(f"Score calculated: {score_percentage}%")  # Debug print
        
        try:
            # Create test result with the calculated score
            test_result = TestResult.objects.create(
                user=request.user,
                topic=topic,
                level=difficulty.lower(),
                score=score_percentage,
                total_questions=total_questions,
                correct_answers=correct_answers
            )
            print(f"Test result created with ID: {test_result.id}")
            
            # Redirect to test result page
            return redirect('courses:test_result', test_id=test_result.id)
            
        except Exception as e:
            print(f"Error creating test result: {str(e)}")
            messages.error(request, "There was an error saving your test results.")
            return redirect('courses:test_list')
    
    return redirect('courses:test_list')

# Add this view to handle the test result display
@login_required
def test_result(request, test_id):
    try:
        test_result = TestResult.objects.get(id=test_id, user=request.user)
        context = {
            'score_percentage': test_result.score,
            'correct_answers': test_result.correct_answers,
            'total_questions': test_result.total_questions,
            'topic': test_result.topic,
            'level': test_result.level,
            'test_result': test_result
        }
        return render(request, 'courses/test_result.html', context)
    except TestResult.DoesNotExist:
        messages.error(request, "Test result not found.")
        return redirect('courses:test_list')
    
@login_required
def save_answer(request):
    """AJAX endpoint to save answers during the test"""
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        answer = request.POST.get('answer')
        
        if not request.session.get('test_answers'):
            request.session['test_answers'] = {}
            
        request.session['test_answers'][question_id] = answer
        request.session.modified = True
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)