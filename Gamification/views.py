from django.http import JsonResponse
from users.models import User
from .models import UserBadge
from users.decorators import jwt_required


def leaderboard(request):
    users = User.objects.order_by("-points")

    data = []

    for user in users:
        data.append({
            "username": user.username,
            "points": user.points
        })

    return JsonResponse(data, safe=False)


@jwt_required
def my_badges(request):

    badges = UserBadge.objects.filter(user=request.user)

    data = []

    for badge in badges:
        data.append({
            "badge": badge.badge.name,
            "earned_at": badge.earned_at
        })

    return JsonResponse(data, safe=False)


