from django.utils import timezone
from .models import TransactionLogBase

from django.db import DatabaseError
import logging

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log(request, user, event_type, message,
            entity_type=None, entity_id=None, entity_name=None):
        try:
            TransactionLogBase.objects.create(
                title=event_type,
                user_ip_address=request.META.get("REMOTE_ADDR"),
                event_type=event_type,
                event_message=message,
                triggered_by=user,
                entity_type=entity_type,
                entity_id=str(entity_id) if entity_id else None,
                entity_name=entity_name,
            )
            return True
        except DatabaseError as exc:
            logger.exception("Failed to write audit log: %s", exc)
            return False