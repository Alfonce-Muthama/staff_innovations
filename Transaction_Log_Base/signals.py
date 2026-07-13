# # transactionlogbase/signals.py
#
# from django.contrib.auth.signals import user_logged_in, user_logged_out
# from django.dispatch import receiver
# from django.utils import timezone
# from .models import TransactionLogBase
#
# @receiver(user_logged_in)
# def log_login(sender, request, user, **kwargs):
#     TransactionLogBase.objects.create(
#         title="User Login",
#         event_type="LOGIN",
#         event_message=f"{user.username} logged in.",
#         event_date=timezone.now().date(),
#         triggered_by=user,
#         user_ip_address=request.META.get("REMOTE_ADDR"),
#         entity_type="User",
#         entity_id=str(user.id),
#         entity_name=user.username,
#     )
#
# @receiver(user_logged_out)
# def log_logout(sender, request, user, **kwargs):
#     if user is None:
#         return
#
#     TransactionLogBase.objects.create(
#         title="User Logout",
#         event_type="LOGOUT",
#         event_message=f"{user.username} logged out.",
#         event_date=timezone.now().date(),
#         triggered_by=user,
#         user_ip_address=request.META.get("REMOTE_ADDR"),
#         entity_type="User",
#         entity_id=str(user.id),
#         entity_name=user.username,
#     )