from django.db import transaction
from users.models import User
from .models import PointRule, PointHistory, Badge, UserBadge


@transaction.atomic
def award_points(user, action):

    try:
        rule = PointRule.objects.get(action=action)
    except PointRule.DoesNotExist:
        raise ValueError(f"No PointRule found for action '{action}'")

    # Update user's total points
    user.points += rule.points
    user.save()

    # Record the transaction
    PointHistory.objects.create(
        user=user,
        action=rule.action,
        points=rule.points
    )

    # Check for new badges
    check_badges(user)

    return rule.points

#ensuring a badge is awarded only once
def check_badges(user):

    badges = Badge.objects.all()

    for badge in badges:

        if user.points >= badge.threshold:

            UserBadge.objects.get_or_create(
                user=user,
                badge=badge
            )

#this shows the leaderboard
def get_leaderboard(limit=10):

    return User.objects.order_by("-points")[:limit]

#showing users point history
def get_point_history(user):

    return PointHistory.objects.filter(
        user=user
    ).order_by("-created_at")

#getting users badge
def get_user_badges(user):

    return UserBadge.objects.filter(user=user)



