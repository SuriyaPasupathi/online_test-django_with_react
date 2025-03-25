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

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({
            'message': 'Register API is working.',
            'method': 'GET',
            'usage': 'Send a POST request with username, email, and password to register.',
            'example': {
                'username': 'exampleuser',
                'email': 'example@example.com',
                'password': 'yourpassword123'
            }
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            if not request.body:
                return Response({
                    'message': 'Request body is empty',
                    'help': 'Send JSON data',
                    'example': {
                        'username': 'exampleuser',
                        'email': 'example@example.com',
                        'password': 'yourpassword123'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                body_str = request.body.decode('utf-8')
                data = json.loads(body_str)
            except json.JSONDecodeError as e:
                return Response({
                    'message': 'Invalid JSON format',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)

            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()

            missing_fields = []
            if not username: missing_fields.append('username')
            if not email: missing_fields.append('email')
            if not password: missing_fields.append('password')

            if missing_fields:
                return Response({
                    'message': 'Missing required fields',
                    'missing_fields': missing_fields
                }, status=status.HTTP_400_BAD_REQUEST)

            if '@' not in email:
                return Response({
                    'message': 'Invalid email format',
                    'email': email
                }, status=status.HTTP_400_BAD_REQUEST)

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

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False  # You can change this based on approval logic
            )

            refresh = RefreshToken.for_user(user)
            tokens = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }

            try:
                send_mail(
                    'New User Registration',
                    f'New user registered: {username} ({email})',
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=True
                )
            except Exception as e:
                print(f'Email sending failed: {e}')

            return Response({
                'message': 'Registration successful',
                'user': {
                    'username': username,
                    'email': email
                },
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'message': 'Unexpected error occurred',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

logger = logging.getLogger(__name__)
class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "message": "Login API is working.",
            "method": "GET",
            "usage": "Send a POST request with username and password to log in.",
            "example": {
                "username": "exampleuser",
                "password": "yourpassword123"
            }
        }, status=status.HTTP_200_OK)

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

class GetQuestionsView(View):
    def get(self, request, level_id, section_id, *args, **kwargs):
        # Fetch the questions based on level and section
        questions = list(AbacusTest.objects.filter(level=level_id, section=section_id))
        random.shuffle(questions)

        # Prepare data to return
        questions_data = [{"id": question.id, "question_text": question.question_text} for question in questions]

        return JsonResponse({"questions": questions_data}, status=200)

@method_decorator(csrf_exempt, name='dispatch')
class SubmitAnswersView(View):
    def get(self, request, level_id, section_id, *args, **kwargs):
        return JsonResponse({
            "message": "SubmitAnswersView endpoint is working.",
            "method": "GET",
            "usage": "Send a POST request to submit answers for evaluation.",
            "required_fields": {
                "answers": {
                    "format": {
                        "question_id_1": "your_answer_1",
                        "question_id_2": "your_answer_2"
                    }
                }
            },
            "example_post_body": {
                "answers": {
                    "12": "32",
                    "13": "15"
                }
            },
            "endpoint": f"/api/submit-answers/{level_id}/{section_id}/"
        }, status=200)

    def post(self, request, level_id, section_id, *args, **kwargs):
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})

            if not answers:
                return JsonResponse({"error": "No answers provided."}, status=400)

            correct_count = 0
            incorrect_answers = {}
            correct_answers = {}

            questions = AbacusTest.objects.filter(level=level_id, section=section_id)
            total_questions = questions.count()

            for question in questions:
                question_id = str(question.id)
                user_answer = answers.get(question_id, "").strip()
                if user_answer == str(question.correct_answer).strip():
                    correct_count += 1
                else:
                    incorrect_answers[question_id] = user_answer
                    correct_answers[question_id] = question.correct_answer

            score = f"{correct_count}/{total_questions}"

            if section_id == 2:
                return JsonResponse({
                    "score": score,
                    "total_score": correct_count,
                    "incorrect_answers": incorrect_answers,
                    "correct_answers": correct_answers,
                    "move_to_next_level": True,
                }, status=200)

            return JsonResponse({
                "score": score,
                "total_score": correct_count,
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
    def get(self, request, level_id, section_id, *args, **kwargs):
        return JsonResponse({
            "message": "Validate_answer endpoint is working.",
            "method": "GET",
            "usage": "Send a POST request to validate answers.",
            "required_fields": {
                "answers": {
                    "format": {
                        "question_id_1": "your_answer_1",
                        "question_id_2": "your_answer_2"
                    }
                }
            },
            "example_post_body": {
                "answers": {
                    "101": "25",
                    "102": "47"
                }
            },
            "endpoint": f"/api/validate-answers/{level_id}/{section_id}/"
        }, status=200)

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
            total_questions = questions.count()

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

            if section_id == 2:
                return JsonResponse({
                    "score": score,
                    "total_score": correct_count,
                    "incorrect_answers": incorrect_answers,
                    "correct_answers": correct_answers,
                    "move_to_next_level": True,
                }, status=200)

            return JsonResponse({
                "score": score,
                "total_score": correct_count,
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

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this view
def practice_session(request):
    user = request.user
    print(f"Authenticated User: {user}")

    if request.method == 'GET':
        try:
            # Get or create the UserAttempt object
            user_attempt, created = UserAttempt.objects.get_or_create(user=user)
            
            # Fetch all past practice attempt details
            attempt_details = AttemptDetail.objects.filter(user_attempt=user_attempt, attempt_type="Practice")

            details_list = []
            for attempt in attempt_details:
                details_list.append({
                    "score": attempt.score,
                    "total_questions": attempt.total_questions,
                    "timestamp": attempt.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return Response({
                "message": "Practice session summary fetched successfully.",
                "practice_count": user_attempt.practice_count,
                "attempts": details_list
            }, status=200)

        except Exception as e:
            print(f"GET Error: {e}")
            return Response({"error": "Failed to fetch practice session details."}, status=500)

    elif request.method == 'POST':
        try:
            score = request.data.get('score')
            total_questions = request.data.get('total_questions', 0)

            if score is None or total_questions == 0:
                return Response({"error": "Missing required data: score and total_questions."}, status=400)

            user_attempt, created = UserAttempt.objects.get_or_create(user=user)
            user_attempt.practice_count += 1
            user_attempt.save()

            attempt_detail = AttemptDetail.objects.create(
                user_attempt=user_attempt,
                attempt_type="Practice",
                score=score,
                total_questions=total_questions
            )

            return Response({
                "message": "Practice session recorded successfully.",
                "score": f"{score}/{total_questions}",
                "attempt_detail_id": attempt_detail.id
            }, status=201)

        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            return Response({"error": "Database error occurred while processing your request."}, status=500)
        except Exception as e:
            print(f"POST Error: {e}")
            return Response({"error": "An error occurred while processing your request."}, status=500)

    else:
        return Response({"error": "Unsupported request method."}, status=405)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # Ensure only authenticated users can access this view
def test_session(request):
    user = request.user
    print(f"Authenticated User: {user}")

    if request.method == 'GET':
        try:
            # Get or create the UserAttempt object
            user_attempt, created = UserAttempt.objects.get_or_create(user=user)
            
            # Fetch all past test attempt details
            attempt_details = AttemptDetail.objects.filter(user_attempt=user_attempt, attempt_type="Test")

            details_list = []
            for attempt in attempt_details:
                details_list.append({
                    "score": attempt.score,
                    "total_questions": attempt.total_questions,
                    "timestamp": attempt.created_at.strftime("%Y-%m-%d %H:%M:%S")
                })

            return Response({
                "message": "Test session summary fetched successfully.",
                "test_count": user_attempt.test_count,
                "attempts": details_list
            }, status=200)

        except Exception as e:
            print(f"GET Error: {e}")
            return Response({"error": "Failed to fetch test session details."}, status=500)

    elif request.method == 'POST':
        try:
            score = request.data.get('score')
            total_questions = request.data.get('total_questions', 0)

            if score is None or total_questions == 0:
                return Response({"error": "Missing required data: score and total_questions."}, status=400)

            user_attempt, created = UserAttempt.objects.get_or_create(user=user)
            user_attempt.test_count += 1
            user_attempt.save()

            attempt_detail = AttemptDetail.objects.create(
                user_attempt=user_attempt,
                attempt_type="Test",
                score=score,
                total_questions=total_questions
            )

            return Response({
                "message": "Test session recorded successfully.",
                "score": f"{score}/{total_questions}",
                "attempt_detail_id": attempt_detail.id
            }, status=201)

        except IntegrityError as e:
            print(f"Integrity Error: {e}")
            return Response({"error": "Database error occurred while processing your request."}, status=500)
        except Exception as e:
            print(f"POST Error: {e}")
            return Response({"error": "An error occurred while processing your request."}, status=500)

    else:
        return Response({"error": "Unsupported request method."}, status=405)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return self.logout_user(request)

    def get(self, request):
        return self.logout_user(request)

    def logout_user(self, request):
        try:
            logger.info(f"Logout attempt - User: {request.user}")
            refresh_token = request.data.get('refresh') if request.method == 'POST' else request.query_params.get('refresh')

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