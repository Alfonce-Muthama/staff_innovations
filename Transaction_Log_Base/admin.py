from django.contrib import admin

from .models import TransactionLogBase, Notifications, MpesaTransactionCost, EventType

# Register your models here.
# admin.site.register(TransactionLogBase)

admin.site.register(Notifications)

admin.site.register(MpesaTransactionCost)
admin.site.register(EventType)

# admin.site.register(User)
@admin.register(TransactionLogBase)
class TransactionLogAdmin(admin.ModelAdmin):
    readonly_fields = ["id", 'created_at', 'updated_at']


