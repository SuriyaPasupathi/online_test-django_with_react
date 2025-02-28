import logging
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,AbacusTest,session,TestNotification, UserAttempt, AttemptDetail,UserLogoutLog
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.views import View
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import TestSerializer
import random
from django.contrib.auth import authenticate
from django.utils import timezone
from .utils import get_tokens_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import TokenError

logger = logging.getLogger(__name__) # Set up logger
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
        username = request.data.get("username")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            # Generate JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response({"access_token": access_token}, status=status.HTTP_200_OK)
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

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

@method_decorator(csrf_exempt, name='dispatch')
class validate_answer(View):
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
            questions = session.objects.filter(level=level_id, section=section_id)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this view
def practice_session(request):
    print(f"Authenticated User: {request.user}")  # Log authenticated user
    if request.user.is_authenticated:
        try:
            user = request.user
            score = request.data.get('score')
            total_questions = request.data.get('total_questions', 0)

            if score is None or total_questions == 0:
                return Response({"error": "Missing required data: score and total_questions."}, status=400)

            # Get or create the UserAttempt object for the current user
            user_attempt, created = UserAttempt.objects.get_or_create(user=user)

            # Increment practice count
            user_attempt.practice_count += 1
            user_attempt.save()

            # Create AttemptDetail record for this practice session
            attempt_detail = AttemptDetail.objects.create(
                user_attempt=user_attempt,
                attempt_type="Practice",
                score=score,
                total_questions=total_questions
            )

            # Return a response with success message
            return Response({
                "message": "Practice session recorded successfully.",
                "score": f"{score}/{total_questions}",
                "attempt_detail": str(attempt_detail)
            })
        
        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            return Response({"error": "Database error occurred while processing your request."}, status=500)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "An error occurred while processing your request."}, status=500)
    else:
        return Response({"error": "User must be logged in."}, status=401)

<<<<<<< HEAD




@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this view
=======
@csrf_exempt  # Use this only if CSRF issues occur in testing (not recommended for production)
>>>>>>> a58004149dc035ece8747e149173c61219442c84
def test_session(request):
    print(f"Authenticated User: {request.user}")  # Log authenticated user
    if request.user.is_authenticated:
        try:
            user = request.user
            score = request.data.get('score')
            total_questions = request.data.get('total_questions', 0)

            if score is None or total_questions == 0:
                return Response({"error": "Missing required data: score and total_questions."}, status=400)

            # Get or create the UserAttempt object for the current user
            user_attempt, created = UserAttempt.objects.get_or_create(user=user)

            # Increment test count
            user_attempt.test_count += 1
            user_attempt.save()

            # Create AttemptDetail record for this test session
            attempt_detail = AttemptDetail.objects.create(
                user_attempt=user_attempt,
                attempt_type="Test",
                score=score,
                total_questions=total_questions
            )

            # Return a response with success message
            return Response({
                "message": "Test session recorded successfully.",
                "score": f"{score}/{total_questions}",
                "attempt_detail": str(attempt_detail)
            })

        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            return Response({"error": "Database error occurred while processing your request."}, status=500)
        except Exception as e:
            print(f"Error: {e}")
            return Response({"error": "An error occurred while processing your request."}, status=500)
    else:
        return Response({"error": "User must be logged in."}, status=401)



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.info(f"Logout attempt - User: {request.user}")
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                logger.warning("No refresh token provided")
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logger.info("Token blacklisted successfully")
            except TokenError as e:
                logger.warning(f"Token error: {e}")
            except Exception as e:
                logger.error(f"Token blacklist error: {e}")

            request.session.flush()
            return Response(
                {"message": "Successfully logged out"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        