"""
ModelForms for TeamFlow — Session 05

ModelForms are forms automatically generated from a Django model.
Django handles field types, validation, and saving to the database.
"""
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Project, Task
from .validators import validate_future_deadline
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class ProjectForm(forms.ModelForm):
    """
    Form for creating and editing Projects.

    ModelForm automatically creates form fields from the model's fields.
    We exclude 'owner', 'members', 'created_at', 'updated_at' because
    they are set programmatically, not by the user filling in a form.
    """
    class Meta:
        model = Project
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project name',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the project goals and scope...',
            }),
        }


class TaskForm(forms.ModelForm):
    """
    Form for creating and editing Tasks.

    We apply our custom deadline validator to the deadline field.
    The 'project' field is set in the view, not by the user.
    """
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'deadline', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe what needs to be done...',
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        """
        Override __init__ to apply the custom deadline validator.
        We add it here rather than in the model so the validator only
        runs in forms (not when creating tasks programmatically).
        """
        super().__init__(*args, **kwargs)
        # Add our custom validator to the deadline field
        self.fields['deadline'].validators.append(validate_future_deadline)
        # Make the assigned_to field optional with a blank choice
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = '— Unassigned —'



class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1',
                'password2']
        widgets = {
                'username': forms.TextInput(
        attrs={'class': 'form-control'}),
                }
        def init(self, args, **kwargs):
            super().init(args, **kwargs)
            # Bootstrap class for password fields
            for f in ['password1', 'password2']:
                self.fields[f].widget.attrs[
                'class'] = 'form-control'


        
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }


