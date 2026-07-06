from django.contrib import admin
from Gamification.models import Badge, UserBadge, PointRule, PointHistory

# Register your models here.
admin.site.register(Badge)
admin.site.register(UserBadge)
admin.site.register(PointRule)
admin.site.register(PointHistory)
