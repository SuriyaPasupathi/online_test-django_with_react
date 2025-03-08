from django.urls import path
from .views import RegisterView, LoginView, approve_user,GetQuestionsView,SubmitAnswersView,Validate_answer,Get_random_questions,get_test_notification,practice_session,test_session,LogoutView,check_test_status

urlpatterns = [
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('approve-user/', approve_user, name='approve_user'),
    path('api/questions/<int:level_id>/<int:section_id>/', GetQuestionsView.as_view(), name='get_questions'),
    path('api/submit_answers/<int:level_id>/<int:section_id>/', SubmitAnswersView.as_view(), name='submit_answers'),
   
    path('api/random_questions/<int:level_id>/<int:section_id>/', Get_random_questions.as_view(), name='get_random_questions'),
    path('api/validate_answers/<int:level_id>/<int:section_id>/', Validate_answer.as_view(), name='validate_answers'),
    path('api/test_notification/', get_test_notification, name='get_test_notification'),
   
   
    path('api/practice_session/', practice_session, name='practice_session'),
    path('api/test_session/', test_session, name='get_test_notification'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/test_status/', check_test_status, name='update_test_status'),
   
    
    
]


  
