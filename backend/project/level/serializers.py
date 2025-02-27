



from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import  AbacusTest,AttemptDetail,UserAttempt


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




class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AbacusTest
        fields = ['id', 'question_text']  # Ensure correct fields




class AttemptDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttemptDetail
        fields = ['attempt_type', 'score', 'timestamp']  # Specify the fields you want to include in the response

class UserAttemptSerializer(serializers.ModelSerializer):
    # Include the related AttemptDetails in the UserAttempt serializer
    attempts = AttemptDetailSerializer(many=True, read_only=True)

    class Meta:
        model = UserAttempt
        fields = ['user', 'practice_count', 'test_count', 'attempts']  # Include the 'attempts' field to show related attempt details

    def create(self, validated_data):
        user = validated_data.get('user')
        user_attempt, created = UserAttempt.objects.get_or_create(user=user, **validated_data)
        return user_attempt

    def update(self, instance, validated_data):
        instance.practice_count = validated_data.get('practice_count', instance.practice_count)
        instance.test_count = validated_data.get('test_count', instance.test_count)
        instance.save()
        return instance
