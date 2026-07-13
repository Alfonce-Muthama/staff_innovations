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
    entity_id = models.CharField(null=True, blank=True, max_length=150)
    entity_name = models.CharField(null=True, blank=True, max_length=150)


class Notifications(BaseModel):
    TransactionLogBase = models.ForeignKey("TransactionLogBase", on_delete=models.CASCADE, null=True, blank=True)
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

