from django.http import JsonResponse
from users.models import User
from .models import UserBadge
from users.decorators import jwt_required
from django.core.paginator import Paginator


def leaderboard(request):
    if request.method != "GET":
        return JsonResponse(
            {"error": "GET method required"},
            status=405
        )

    users = User.objects.order_by("-points")

    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 10)

    paginator = Paginator(users, page_size)
    page = paginator.get_page(page_number)

    data = []

    for user in page:
        data.append({
            "username": user.username,
            "points": user.points
        })

    return JsonResponse({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page.number,
        "page_size": int(page_size),
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
        "results": data
    })

@jwt_required
def my_badges(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "GET method required"},
            status=405
        )

    badges = UserBadge.objects.filter(user=request.user).order_by("-earned_at")

    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 10)

    paginator = Paginator(badges, page_size)
    page = paginator.get_page(page_number)

    data = []

    for badge in page:
        data.append({
            "badge": badge.badge.name,
            "earned_at": badge.earned_at
        })

    return JsonResponse({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page.number,
        "page_size": int(page_size),
        "has_next": page.has_next(),
        "has_previous": page.has_previous(),
        "results": data
    })


