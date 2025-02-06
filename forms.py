from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Course
import re
from django.contrib.auth.forms import PasswordChangeForm
from .models import CustomUser

User = get_user_model()
class ResetPasswordForm(forms.Form):
    national_id = forms.CharField(
        max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        national_id = cleaned_data.get("national_id")

        # Fix the incorrect profile reference
        if not CustomUser.objects.filter(email=email, national_id=national_id).exists():
            raise forms.ValidationError("Invalid National ID or Email")

        return cleaned_data

class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Current Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Student ID", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class RegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'First name is required'}
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Last name is required'}
    )
    national_id = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'National ID is required', 'min_length': 'National ID must be 10 digits', 'max_length': 'National ID must be 10 digits'}
    )
    username = forms.CharField(
        label="Student ID",
        max_length=9,
        min_length=8,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Student ID is required', 'min_length': 'Student ID must be at least 8 digits', 'max_length': 'Student ID must be maximum 9 digits'}
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Email is required', 'invalid': 'Email format is wrong'}
    )
    phone_number = forms.CharField(
        max_length=11,
        min_length=11,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Phone number is required', 'min_length': 'Phone number must be 11 digits', 'max_length': 'Phone number must be 11 digits'}
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Password is required'}
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Please confirm your password'}
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number','national_id', 'password1', 'password2']

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Last name should only contain letters.")
        return last_name

    def clean_username(self):  # Student ID validation
        student_id = self.cleaned_data.get("username")
        if not student_id.isdigit():
            raise forms.ValidationError("Student ID must contain only digits.")
        return student_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number

    def clean_national_id(self):
        national_id = self.cleaned_data.get("national_id")

        # Ensure it's only digits
        if not national_id.isdigit():
            raise forms.ValidationError("National ID must contain only digits.")

        # Ensure it's unique
        if User.objects.filter(national_id=national_id).exists():
            raise forms.ValidationError("A user with this National ID already exists.")

        return national_id

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise forms.ValidationError("Email format is wrong.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain both letters and numbers.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Passwords do not match.")
        return cleaned_data
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['code', 'name', 'credit_hours','day', 'class_time', 'exam_time', 'instructor_name', 'total_capacity', 'filled_capacity', 'department']

class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'First name is required'}
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Last name is required'}
    )
    national_id = forms.CharField(
        max_length=10,
        min_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'National ID is required', 'min_length': 'National ID must be 10 digits', 'max_length': 'National ID must be 10 digits'}
    )
    username = forms.CharField(
        label="Student ID",
        max_length=9,
        min_length=8,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Student ID is required', 'min_length': 'Student ID must be at least 8 digits', 'max_length': 'Student ID must be maximum 9 digits'}
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Email is required', 'invalid': 'Email format is wrong'}
    )
    phone_number = forms.CharField(
        max_length=11,
        min_length=11,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        error_messages={'required': 'Phone number is required', 'min_length': 'Phone number must be 11 digits', 'max_length': 'Phone number must be 11 digits'}
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'national_id']

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise forms.ValidationError("First name should only contain letters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name.isalpha():
            raise forms.ValidationError("Last name should only contain letters.")
        return last_name

    def clean_username(self):
        student_id = self.cleaned_data.get("username")
        if not student_id.isdigit():
            raise forms.ValidationError("Student ID must contain only digits.")
        return student_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone_number

    def clean_national_id(self):
        national_id = self.cleaned_data.get("national_id")
        if not national_id.isdigit():
            raise forms.ValidationError("National ID must contain only digits.")
        return national_id

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise forms.ValidationError("Email format is wrong.")
        return email

class ResetPasswordForm(forms.Form):
    national_id = forms.CharField(
        max_length=10, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        national_id = cleaned_data.get("national_id")

        if not CustomUser.objects.filter(email=email, national_id=national_id).exists():
            raise forms.ValidationError("Invalid National ID or Email")

        return cleaned_data