import logging
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,AbacusTest,PracticeSession,session,TestNotification
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.views import View
from django.views.decorators.cache import never_cache
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import TestSerializer
import random
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .utils import get_tokens_for_user




# Set up logger
logger = logging.getLogger(__name__)

class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow any user (unauthenticated)

    def post(self, request):
        """Handles user registration, sends admin approval request, and generates JWT token."""
        try:
            # Extract data from the request
            data = request.data
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            # Validate input - Ensure necessary fields are provided
            if not username or not email or not password:
                logger.warning("Missing required fields in registration data.")
                return Response({'message': 'Username, email, and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            if '@' not in email:
                logger.warning(f"Invalid email format: {email}")
                return Response({'message': 'Invalid email format.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if username or email is already taken
            if User.objects.filter(username=username).exists():
                logger.warning(f"Username already taken: {username}")
                return Response({'message': 'Username already taken.'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                logger.warning(f"Email already registered: {email}")
                return Response({'message': 'Email already registered.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create inactive user
            hashed_password = make_password(password)
            user = User(username=username, email=email, password=hashed_password, is_active=False)  
            user.save()

            # Generate JWT token for new user
            tokens = get_tokens_for_user(user)

            # Notify admin for approval
            try:
                send_mail(
                    'New User Registration',
                    f'A new user has registered: {username} ({email}). Please approve them.',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],  # Ensure this is a valid admin email
                )
                logger.info(f"Admin notified about new user: {username} ({email})")
            except Exception as email_error:
                logger.error(f"Error sending email notification: {str(email_error)}")
                return Response({'message': 'Registration successful, but failed to notify admin. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'message': 'Registration successful. Please wait for admin approval.',
                'access_token': tokens['access'],  # Send JWT access token as part of response
                'refresh_token': tokens['refresh']  # Send JWT refresh token as part of response
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return Response({'message': 'Something went wrong. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Authenticate the user (this is just an example)
        username = request.data.get('username')
        password = request.data.get('password')

        # Validate user credentials (you may want to use Django's built-in authentication system here)
        user = authenticate(username=username, password=password)
        if user is not None:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({"access_token": access_token})
        return Response({"detail": "Invalid credentials"}, status=400)
@api_view(['POST'])
def approve_user(request):
    """ Admin approves user and activates their account. """
    try:
        user_id = request.data.get('user_id')
        user = User.objects.filter(id=user_id).first()

        if not user:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({'message': 'User is already approved.'}, status=status.HTTP_400_BAD_REQUEST)

        # Activate user
        user.is_active = True
        user.save()

        # Notify user
        send_mail(
            'Account Approved',
            f'Hello {user.username},\n\nYour account has been approved. You can now log in.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )

        return Response({'message': 'User approved and notified via email.'}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error approving user: {str(e)}")
        return Response({'message': 'Something went wrong. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetQuestionsView(View):
    def get(self, request, level_id, section_id, *args, **kwargs):
        # Fetch the questions based on level and section
        questions = AbacusTest.objects.filter(level=level_id, section=section_id)

        # Prepare data to return
        questions_data = [{"id": question.id, "question_text": question.question_text} for question in questions]

        return JsonResponse({"questions": questions_data}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class SubmitAnswersView(View):
    def post(self, request, level_id, section_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})

            if not answers:
                return JsonResponse({"error": "No answers provided."}, status=400)

            correct_count = 0
            incorrect_answers = {}
            correct_answers = {}

            # Fetch all questions for this level and section
            questions = AbacusTest.objects.filter(level=level_id, section=section_id)
            total_questions = questions.count()  # Get the exact number of questions posted by admin

            # Validate submitted answers
            for question in questions:
                question_id = str(question.id)
                user_answer = answers.get(question_id, "").strip()
                if user_answer == str(question.correct_answer).strip():
                    correct_count += 1
                else:
                    incorrect_answers[question_id] = user_answer
                    correct_answers[question_id] = question.correct_answer

            score = f"{correct_count}/{total_questions}"

            # If it's the second section, return total results
            if section_id == 2:
                return JsonResponse({
                    "score": score,
                    "total_score": correct_count,  # Final total score
                    "incorrect_answers": incorrect_answers,  # Retain incorrect answers from both sections
                    "correct_answers": correct_answers,
                    "move_to_next_level": True,
                }, status=200)

            # If Section 1 is completed, pass incorrect answers to Section 2
            return JsonResponse({
                "score": score,
                "total_score": correct_count,  # Accumulate score for Section 2
                "incorrect_answers": incorrect_answers,
                "correct_answers": correct_answers,
                "move_to_next_section": True,
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class PracticeSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the user's practice session details."""
        try:
            session = PracticeSession.objects.get(user=request.user)
            return Response({
                "session_count": session.session_count,
                "last_practiced": session.last_practiced,
                "score": session.score  # Include the score here
            }, status=status.HTTP_200_OK)
        except PracticeSession.DoesNotExist:
            return Response({"message": "No practice session found!"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Increment session count when the user practices and update score."""
        session, created = PracticeSession.objects.get_or_create(user=request.user)
        
        # Increment the session count
        session.session_count += 1
        
        # Update the score (assuming you get the score from the frontend)
        score_from_frontend = request.data.get("score", 0)  # Get score from frontend
        session.score = score_from_frontend  # Update the score in the session object

        # Save the session object with updated values
        session.save()

        return Response({
            "message": "Practice session updated!",
            "session_count": session.session_count,
            "last_practiced": session.last_practiced,
            "score": session.score  # Return updated score as well
        }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([AllowAny])  # Allow public access
def get_random_questions(request, level_id, section_id):
    """
    Get random questions for the specified level and section.
    """
    questions = list(session.objects.filter(level=level_id, section=section_id))
    
    if not questions:
        return Response({"error": "No questions available for this level and section."}, status=404)

    random.shuffle(questions)  # Shuffle to get random questions
    serialized_questions = TestSerializer(questions, many=True)

    return Response(serialized_questions.data)

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow public access
def validate_answers(request, level_id, section_id):
    """
    Validate the answers submitted by the user for a specific level and section.
    Return the score based on correct answers, and update the user's practice session score.
    """
    answers = request.data.get('answers', {})

    if not isinstance(answers, dict):
        return Response({"error": "Invalid data format. Answers must be a dictionary."}, status=400)

    questions = AbacusTest.objects.filter(level=level_id, section=section_id)
    score = 0
    incorrect_answers = []
    correct_answers = {}

    # Iterate through each question and check the user's answer
    for question in questions:
        user_answer = answers.get(str(question.id), "").strip().lower()
        if user_answer == question.correct_answer.strip().lower():
            score += 1
        else:
            incorrect_answers.append(question.id)
            correct_answers[question.id] = question.correct_answer

    # Logic to determine whether to move to the next section or level
    move_to_next_section = score >= 7  # Move to next section if 7/10 are correct
    move_to_next_level = False

    # Move to the next level if Level 3 & Section 2 is completed with a high enough score
    if level_id == 3 and section_id == 2 and score >= 14:
        move_to_next_level = True

    # Update the score in the user's PracticeSession
    user = request.user  # Assuming the user is authenticated
    session, created = PracticeSession.objects.get_or_create(user=user)

    # Add score to the session (you can adjust this logic as needed)
    session.score += score
    session.save()

    return Response({
        "score": score,
        "incorrect_answers": incorrect_answers,
        "correct_answers": correct_answers,
        "move_to_next_section": move_to_next_section,
        "move_to_next_level": move_to_next_level
    })


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow public access
def get_test_notification(request):
    """
    Get the test notification message and start time with a countdown.
    """
    # Fetch the latest active notification
    notification = TestNotification.objects.filter(is_active=True).last()

    if not notification:
        return Response({"error": "No active test notification found."}, status=status.HTTP_404_NOT_FOUND)

    # Get current time (timezone-aware)
    now = timezone.now()

    # Get the start date from the TestNotification model
    test_start_time = notification.start_date

    # Compare current time with test start time
    if now < test_start_time:
        # Calculate remaining time until the test starts
        time_remaining = (test_start_time - now).total_seconds()
        minutes_remaining = int(time_remaining // 60)
        seconds_remaining = int(time_remaining % 60)

        return Response({
            "message": notification.message,
            "start_time": test_start_time.isoformat(),  # Convert to ISO format for frontend
            "start_message": f"Test will start in {minutes_remaining} minutes and {seconds_remaining} seconds.",
            "time_remaining_seconds": time_remaining  # Useful for frontend countdown
        }, status=status.HTTP_200_OK)
    
    # If the test has started, allow access
    return Response({
        "message": notification.message,
        "start_time": test_start_time.isoformat(),
        "start_message": "Test is now available!"
    }, status=status.HTTP_200_OK)


