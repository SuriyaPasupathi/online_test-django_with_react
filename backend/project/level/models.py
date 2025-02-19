# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class User(AbstractUser):
#     is_approved = models.BooleanField(default=False)

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     # Additional profile fields can go here (e.g., profile picture)



# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError





class User(AbstractUser):
    is_registered = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def approve(self):
        """ Approves the user and sends an email notification. """
        self.is_active = True
        self.is_approved = True
        self.is_registered = True
        self.save()

        # Send approval email
        send_mail(
            'Account Approved',
            f'Hello {self.username},\n\nYour account has been approved. You can now log in.',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
        )


class AbacusTest(models.Model):
    LEVEL_CHOICES = [(1, "Level 1"), (2, "Level 2"), (3, "Level 3")]
    SECTION_CHOICES = [(1, "Section 1"), (2, "Section 2")]

    level = models.IntegerField(choices=LEVEL_CHOICES)
    section = models.IntegerField(choices=SECTION_CHOICES)
    question_text = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=10)

    def __str__(self):
        return f"Level {self.level}, Section {self.section} - {self.question_text}"
    
class PracticeSession(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_count = models.PositiveIntegerField(default=0)  # Counts practice attempts
    last_practiced = models.DateTimeField(auto_now=True)  # Stores last practice time

   

    def __str__(self):
        return f"{self.user.username} - {self.session_count} times"


class session(models.Model):
    LEVEL_CHOICES = [(1, "Level 1"), (2, "Level 2"), (3, "Level 3")]
    SECTION_CHOICES = [(1, "Section 1"), (2, "Section 2")]

    level = models.IntegerField(choices=LEVEL_CHOICES)
    section = models.IntegerField(choices=SECTION_CHOICES)
    question_text = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=10)
    time_limit = models.IntegerField(help_text="Time limit in seconds")  # Time limit for each question

    def __str__(self):
        return f"Level {self.level}, Section {self.section} - {self.question_text} (Time Limit: {self.time_limit}s)"



class TestNotification(models.Model):
    message = models.TextField()
    start_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Test Notification: {self.message}"
