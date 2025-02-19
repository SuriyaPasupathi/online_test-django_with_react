



from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import  AbacusTest,PracticeSession


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create a new user with registration status
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        # Send email notification to admin about the new user registration
        send_mail(
            'New User Registration',
            f'A new user has registered: {user.username} ({user.email}). Please approve them.',
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],  # Admin email where notifications will be sent
        )
        
        return user
class AbacusTestSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display the username instead of the user ID
    
    class Meta:
        model = AbacusTest
        fields = ['id', 'level', 'section', 'question_text', 'correct_answer', 'user', 'practice_count']

class PracticeSessionSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)  # Show username

    class Meta:
        model = PracticeSession
        fields = ['user', 'session_count']


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbacusTest
        fields = ['id', 'question_text']  # Ensure correct fields