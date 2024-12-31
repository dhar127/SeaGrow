from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Course, Question, TestResult

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'topic', 'description', 'video_url', 'pdf_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter course title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 4,
                'placeholder': 'Enter course description'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'Enter video URL (YouTube, Vimeo, etc.)'
            }),
            'topic': forms.Select(attrs={'class': 'form-select'})
        }

    def clean_video_url(self):
        url = self.cleaned_data.get('video_url')
        if url:
            allowed_domains = ['youtube.com', 'vimeo.com', 'youtu.be']
            if not any(domain in url.lower() for domain in allowed_domains):
                raise forms.ValidationError('Please enter a valid YouTube or Vimeo URL')
        return url

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf:
            if not pdf.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed')
            if pdf.size > 10*1024*1024:  # 10MB limit
                raise forms.ValidationError('File size must be under 10MB')
        return pdf

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['topic', 'level', 'question_text', 'option_1', 'option_2', 
                 'option_3', 'option_4', 'correct_answer']
        widgets = {
            'question_text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'rows': 3
            }),
            'topic': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'correct_answer': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 4
            })
        }

    def clean_correct_answer(self):
        answer = self.cleaned_data.get('correct_answer')
        if answer not in range(1, 5):
            raise forms.ValidationError('Correct answer must be between 1 and 4')
        return answer

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Choose a username'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email

class TestSubmissionForm(forms.Form):
    def __init__(self, questions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(questions, 1):
            self.fields[f'question_{i}'] = forms.ChoiceField(
                choices=[(1, question.option_1),
                        (2, question.option_2),
                        (3, question.option_3),
                        (4, question.option_4)],
                widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
                required=True,
                label=question.question_text
            )

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'})
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError('This email is already registered')
        return email