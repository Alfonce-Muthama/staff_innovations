from django.http import JsonResponse
from users.models import User

#showing the highest schoring employee
def leaderboard(request):

    users = User.objects.order_by("-points")

    data = []

    for user in users:

        data.append({
            "username": user.username,
            "points": user.points
        })

    return JsonResponse(data, safe=False)


#showing badges achieved
from .models import UserBadge

def my_badges(request):

    badges = UserBadge.objects.filter(user=request.user)

    data = []

    for badge in badges:

        data.append({
            "badge": badge.badge.name,
            "earned_at": badge.earned_at
        })

    return JsonResponse(data, safe=False)


