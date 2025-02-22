from django.urls import path
from .views import RegisterView, LoginView, approve_user,GetQuestionsView,SubmitAnswersView,PracticeSessionView,get_random_questions,validate_answers,get_test_notification

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('approve-user/', approve_user, name='approve_user'),
    path('api/questions/<int:level_id>/<int:section_id>/', GetQuestionsView.as_view(), name='get_questions'),
    path('api/submit_answers/<int:level_id>/<int:section_id>/', SubmitAnswersView.as_view(), name='submit_answers'),
    path("api/practice-session/", PracticeSessionView.as_view(), name="practice-session"),
    path('api/random_question/<int:level_id>/<int:section_id>/', get_random_questions, name='get_random_questions'),
    path('api/validate_answers/<int:level_id>/<int:section_id>/', validate_answers, name='validate_answers'),
    path('api/test_notification/', get_test_notification, name='get_test_notification'),
    
    
]


  
