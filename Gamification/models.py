from django.db import models
from Base.models import BaseModel
from users.models import User

# Create your models here.
class Badge(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    threshold = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return self.name



class UserBadge(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="badges"
    )

    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE
    )

    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "badge")

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


#these are the rules for awarding
class PointRule(BaseModel):

    action = models.CharField(
        max_length=100,
        unique=True
    )

    points = models.IntegerField()

    description = models.TextField(blank=True)

    def __str__(self):
        return self.action

class PointHistory(BaseModel):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="point_history"
    )

    points = models.IntegerField()

    action = models.CharField(max_length=100)


    def __str__(self):
        return f"{self.user.username} - {self.points}"








