from django.contrib import admin

from .models import TransactionLogBase, Notifications

# Register your models here.
admin.site.register(TransactionLogBase)
admin.site.register(Notifications)

