# jobs/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Job, JobApplication

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    is_company = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    company_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'is_company', 'company_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to default fields
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        is_company = cleaned_data.get('is_company')
        company_name = cleaned_data.get('company_name')

        if is_company and not company_name:
            self.add_error('company_name', 'Company name is required when registering as a company.')

        return cleaned_data

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'location', 'salary', 'custom_form']
        widgets = {
            'custom_form': forms.Textarea(attrs={'placeholder': 'Enter custom form fields as JSON'})
        }

class DefaultJobApplicationForm(forms.ModelForm):
    resume = forms.FileField()
    cover_letter = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = JobApplication
        fields = ['resume', 'cover_letter']