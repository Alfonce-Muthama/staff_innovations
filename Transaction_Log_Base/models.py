from django.db import models

from Base.models import BaseModel, GenericBaseModel


# Create your models here.
class EventType(GenericBaseModel):
    def __str__(self):
        return self.name

    # LOGIN = "LOGIN", "Login"
    # LOGOUT = "LOGOUT", "Logout"
    # USER_CREATED = "USER_CREATED", "User Created"
    # USER_UPDATED = "USER_UPDATED", "User Updated"
    # USER_DELETED = "USER_DELETED", "User Deleted"
    # IDEA_CREATED = "IDEA_CREATED", "Idea Created"
    # IDEA_UPDATED = "IDEA_UPDATED", "Idea Updated"
    # IDEA_APPROVED = "IDEA_APPROVED", "Idea Approved"
    # PROJECT_CREATED = "PROJECT_CREATED", "Project Created"
    # PROJECT_UPDATED = "PROJECT_UPDATED", "Project Updated"
    # PROJECT_DELETED = "PROJECT_DELETED", "Project Deleted"



class TransactionLogBase(BaseModel):
    title = models.CharField(null=True, blank=True,max_length=200)
    user_ip_address = models.GenericIPAddressField(null=True, blank=True)
    event_type = models.ForeignKey(EventType,on_delete=models.PROTECT,null=True, blank=True)
    event_message = models.TextField(null=True, blank=True)
    triggered_by = models.ForeignKey("users.User", null=True, blank=True, on_delete=models.CASCADE)
    entity_type = models.CharField(null=True, blank=True, max_length=200)
    entity_id = models.CharField(null=True, blank=True, max_length=150)
    entity_name = models.CharField(null=True, blank=True, max_length=150)


class Notifications(BaseModel):
    transaction_log = models.ForeignKey("TransactionLogBase", on_delete=models.CASCADE, null=True, blank=True)
    read_at = models.DateField(null=True, blank=True)
    recipient = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)





class MpesaTransactionCost(BaseModel):
    """
    Stores Safaricom B2C transaction cost tariff bands.
    Managed via Django admin — update here when Safaricom changes tariffs.
    """

    min_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=("Minimum Amount")
    )
    max_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=("Maximum Amount")
    )
    cost = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=("Transaction Cost")
    )
    is_active = models.BooleanField(default=True, verbose_name=("Is Active"))

    class Meta:
        db_table = "mpesa_transaction_costs"
        verbose_name = ("M-Pesa Transaction Cost")
        verbose_name_plural = ("M-Pesa Transaction Costs")
        ordering = ["min_amount"]

    def __str__(self):
        return f"KES {self.min_amount} - {self.max_amount}: KES {self.cost}"

