from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import User,AbacusTest,session,TestNotification,UserAttempt, AttemptDetail
from django.db.models import Sum




class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_registered', 'is_approved')
    list_filter = ('is_registered', 'is_approved')
    search_fields = ('username', 'email')
    actions = ['approve_user']

    def approve_user(self, request, queryset):
        for user in queryset:
            if not user.is_approved:
                user.is_approved = True
                user.is_registered = True  # Mark the user as registered
                user.save()

                # Ensure the user has an email before attempting to send an email
                if user.email:
                    # Send email notification to the user
                    send_mail(
                        'Account Approved',
                        f'Hello {user.username},\n\nYour account has been approved. You can now log in.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                    )
                    self.message_user(request, f"User {user.username} has been approved and notified via email.")
                else:
                    self.message_user(request, f"User {user.username} has been approved but has no email set.")
            else:
                self.message_user(request, f"User {user.username} is already approved.")

    approve_user.short_description = "Approve selected users for login"

admin.site.register(User, UserAdmin)

@admin.register(AbacusTest)
class AbacusTestAdmin(admin.ModelAdmin):
    list_display = ('level', 'section', 'question_text', 'correct_answer')  # Added score field
    list_filter = ('level', 'section')
    search_fields = ('question_text',)












# Unregister if the model is already registered
class sessionAdmin(admin.ModelAdmin):
    list_display = ('level', 'section', 'question_text', 'time_limit', 'correct_answer')
    search_fields = ('question_text', 'level', 'section')

admin.site.register(session, sessionAdmin)

class TestNotificationAdmin(admin.ModelAdmin):
    list_display = ('message', 'start_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('message',)
    date_hierarchy = 'start_date'  # Allows you to filter by date

admin.site.register(TestNotification, TestNotificationAdmin)




class AttemptDetailInline(admin.TabularInline):
    model = AttemptDetail
    extra = 0  # Don't show empty forms
    # Assuming 'question' is a ForeignKey and 'user_answer', 'correct_answer' are fields in AttemptDetail
    readonly_fields = ('question', 'user_answer', 'correct_answer')

    def question(self, obj):
        # This is assuming 'question' is a ForeignKey to another model
        return obj.question.text if obj.question else None

    def user_answer(self, obj):
        return obj.user_answer

    def correct_answer(self, obj):
        return obj.correct_answer

class UserAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'practice_count', 'test_count', 'total_score')
    readonly_fields = ('user', 'practice_count', 'test_count', 'total_score')

    def total_score(self, obj):
        # Sum the scores from related AttemptDetails
        total = AttemptDetail.objects.filter(user_attempt=obj).aggregate(total_score=Sum('score'))['total_score']
        return total if total else 0
    total_score.short_description = 'Total Score'

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Make the score fields readonly only when the object already exists
            return self.readonly_fields + ('total_score',)
        return self.readonly_fields

    inlines = [AttemptDetailInline]  # Show attempts as an inline table
    search_fields = ('user__username',)

# Register the custom admin class
admin.site.register(UserAttempt, UserAttemptAdmin)