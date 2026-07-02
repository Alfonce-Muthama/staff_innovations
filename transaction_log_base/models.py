from django.db import models

from Base.models import BaseModel


# Create your models here.
class TransactionLogBase(BaseModel):
    title = models.CharField(null=True, blank=True,max_length=200)
    user_ip_address = models.GenericIPAddressField(null=True, blank=True)
    event_type = models.CharField(null=True, blank=True, max_length=200)
    event_message = models.TextField(null=True, blank=True)
    event_date = models.DateField(null=True, blank=True)
    triggered_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.CASCADE)
    entity_type = models.CharField(null=True, blank=True, max_length=200)
    entity_id = models.CharField(null=True, blank=True, max_length=30)
    entity_name = models.CharField(null=True, blank=True, max_length=30)


    # class Meta:
    #     abstract = True


