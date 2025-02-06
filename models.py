from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    national_id = models.CharField(max_length=10, unique=True)
    phone_number = models.CharField(max_length=11, unique=True, null=True, blank=True)

class Department(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Course(models.Model):
    DAYS_OF_WEEK = [
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ]
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    credit_hours = models.IntegerField()
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK, default='Monday')
    class_time = models.CharField(max_length=255)
    exam_time = models.CharField(max_length=255)
    instructor_name = models.CharField(max_length=255)
    total_capacity = models.IntegerField()
    filled_capacity = models.IntegerField()
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name}"

class SelectedCourse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Link to Course
    date_selected = models.DateTimeField(auto_now_add=True)  # Automatically store the date and time of selection

    class Meta:
        unique_together = ('user', 'course')  # Ensure a user cannot select the same course multiple times

    def __str__(self):
        return f"{self.user.username} - {self.course.name}"