from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from .models import User,AbacusTest,PracticeSession,session,TestNotification




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
    list_display = ('level', 'section', 'question_text', 'correct_answer')
    list_filter = ('level', 'section')
    search_fields = ('question_text',)


class PracticeSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_count', 'last_practiced')
    readonly_fields = ('user', 'session_count', 'last_practiced')
    search_fields = ('user__username',)

    def has_change_permission(self, request, obj=None):
        return False  # Prevent modifications

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion

admin.site.register(PracticeSession, PracticeSessionAdmin)


# Register the admin class





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
