# transactionlogbase/middleware.py
import time
from django.utils import timezone
from .models import TransactionLogBase

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()

        response = self.get_response(request)

        duration = time.perf_counter() - start

        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False):
            TransactionLogBase.objects.create(
                title="Request",
                event_type=request.method,
                event_message=f"{request.path} completed in {duration:.3f}s",
                event_date=timezone.now().date(),
                triggered_by=user,
                user_ip_address=request.META.get("REMOTE_ADDR"),
                entity_type="Request",
                entity_name=request.path,
            )

        return response

