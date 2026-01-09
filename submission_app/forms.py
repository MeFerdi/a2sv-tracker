from django import forms
from django.core.exceptions import ValidationError
from .models import Question, Submission


class InviteRegisterForm(forms.Form):
    """Form for registering with an invitation token."""
    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Full Name'
        })
    )
    email = forms.EmailField(
        disabled=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input bg-gray-100',
        })
    )
    password = forms.CharField(
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password (min 6 characters)'
        })
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Passwords do not match.')
        
        return cleaned_data


class LoginForm(forms.Form):
    """Form for user login."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class SubmissionForm(forms.ModelForm):
    """Form for submitting a solution link."""
    class Meta:
        model = Submission
        fields = ['submission_link']
        widgets = {
            'submission_link': forms.URLInput(attrs={
                'class': 'w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'https://leetcode.com/submissions/...'
            })
        }


class QuestionForm(forms.ModelForm):
    """Form for creating/editing questions."""
    class Meta:
        model = Question
        fields = ['title', 'leetcode_link', 'q_type', 'difficulty', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'leetcode_link': forms.URLInput(attrs={'class': 'form-input'}),
            'q_type': forms.Select(attrs={'class': 'form-select'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
