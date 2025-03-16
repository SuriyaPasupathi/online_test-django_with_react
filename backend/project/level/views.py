import logging
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,AbacusTest,session,TestNotification, UserAttempt, AttemptDetail,TestStatus,YourModel
from rest_framework import status 
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.http import HttpResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from .serializers import TestStatusSerializer,YourModelSerializer
from rest_framework.permissions import IsAdminUser
import random
from django.contrib.auth import authenticate
from django.utils import timezone
from .utils import get_tokens_for_user
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from rest_framework_simplejwt.tokens import TokenError
from django.utils.timezone import localtime



logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            # Detailed request debugging
            print('\n', '='*50)
            print('DEBUG INFO:')
            print(f'Method: {request.method}')
            print(f'Headers: {dict(request.headers)}')
            print(f'Body Type: {type(request.body)}')
            print(f'Body Length: {len(request.body)}')
            print(f'Content-Type: {request.content_type}')
            print('Raw Body:', request.body)
            print('='*50, '\n')

            # Try to parse the raw body directly
            if not request.body:
                return Response({
                    'message': 'Request body is empty',
                    'help': 'Please send a POST request with JSON data',
                    'example': {
                        'username': 'aarthiaswin',
                        'email': 'aswinarthi1@gmail.com',
                        'password': 'aarthiadvik123'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Convert bytes to string and parse JSON
                body_str = request.body.decode('utf-8')
                data = json.loads(body_str)
                print('Parsed Data:', data)
                
                # Validate data is dictionary
                if not isinstance(data, dict):
                    return Response({
                        'message': 'Invalid data format. Expected JSON object',
                        'received_type': str(type(data))
                    }, status=status.HTTP_400_BAD_REQUEST)

            except json.JSONDecodeError as e:
                return Response({
                    'message': 'Invalid JSON format',
                    'error': str(e),
                    'received_data': body_str if 'body_str' in locals() else None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Extract and validate required fields
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            print('Extracted fields:')
            print(f'Username: {username}')
            print(f'Email: {email}')
            print(f'Password length: {len(password)}')

            # Check required fields
            if not all([username, email, password]):
                missing = []
                if not username: missing.append('username')
                if not email: missing.append('email')
                if not password: missing.append('password')
                return Response({
                    'message': 'Missing required fields',
                    'missing_fields': missing,
                    'received_data': data
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate email format
            if '@' not in email:
                return Response({
                    'message': 'Invalid email format',
                    'received_email': email
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check existing users
            if User.objects.filter(username=username).exists():
                return Response({
                    'message': 'Username already exists',
                    'username': username
                }, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({
                    'message': 'Email already registered',
                    'email': email
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create user
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=False
                )
                print(f'User created successfully: {username}')

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                tokens = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }

                # Try to send email
                try:
                    send_mail(
                        'New User Registration',
                        f'New user registered: {username} ({email})',
                        settings.DEFAULT_FROM_EMAIL,
                        [settings.ADMIN_EMAIL],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Email notification failed: {e}")

                return Response({
                    'message': 'Registration successful',
                    'user': {
                        'username': username,
                        'email': email
                    },
                    'tokens': tokens
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                print(f"User creation error: {e}")
                return Response({
                    'message': 'Failed to create user',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            print(f"Registration error: {e}")
            return Response({
                'message': 'Registration failed',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }, 
                status=status.HTTP_200_OK
            )
        
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
        random.shuffle(questions)

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
class Get_random_questions(View):
    def get(self, request, level_id, section_id, *args, **kwargs):
        # Filter questions based on level and section
        questions = list(session.objects.filter(level=level_id, section=section_id))

        # Shuffle questions
        random.shuffle(questions)

        # Pick first 10 questions (or less if total < 10)
        selected_questions = questions[:10]

        # Get time_limit from first question or default to 600 seconds
        time_limit = selected_questions[0].time_limit if selected_questions else 600

        # Prepare response data
        questions_data = [
            {
                "id": question.id,
                "question_text": question.question_text,
                "correct_answer": question.correct_answer
            }
            for question in selected_questions
        ]

        return JsonResponse({"questions": questions_data, "time_limit": time_limit}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class Validate_answer(View):
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
    Get the test notification message and compare the scheduled time with the system time.
    """
    # Fetch the latest active notification
    notification = TestNotification.objects.filter(is_active=True).last()

    if not notification:
        return Response({"error": "No active test notification found."}, status=status.HTTP_404_NOT_FOUND)

    # Convert the scheduled test time to local time
    notification_time = localtime(notification.start_date)

    # Format date as "dd.mm.yyyy"
    formatted_date = notification_time.strftime("%d.%m.%Y")

    # Format time as "hh:mm AM/PM"
    formatted_time = notification_time.strftime("%I:%M %p")  # 12-hour format

    # Compare scheduled test time with current system time
    current_time = localtime().strftime("%Y-%m-%d %H:%M:%S")
    notification_time_str = notification_time.strftime("%Y-%m-%d %H:%M:%S")

    is_time_reached = notification_time_str <= current_time

    return Response({
        "message": notification.message,
        "formatted_date": formatted_date,
        "formatted_time": formatted_time,
        "is_time_reached": is_time_reached  # Boolean flag to start the test automatically
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this view
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

@api_view(['GET'])
def check_test_status(request):
    try:
        test_status, created = TestStatus.objects.get_or_create(id=1)
        serializer = TestStatusSerializer(test_status)
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=400)
    

class YourModelView(APIView):
    def get(self, request):
        queryset = YourModel.objects.all()
        serializer = YourModelSerializer(queryset, many=True)
        return Response(serializer.data)
    
def home(request):
    return HttpResponse("Welcome to Abacus Online Test Portal")