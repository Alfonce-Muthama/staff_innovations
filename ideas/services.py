from django.utils import timezone
from django.db import transaction
from .models import Idea, IdeaVote, IdeaComment
from projects.models import Project
from Gamification.services import award_points
from Transaction_Log_Base.models import Notifications

DRAFT = "Draft"
SUBMITTED = "Submitted"
PEER_REVIEW = "Peer Review"
PM_REVIEW = "Product Manager Review"
APPROVED = "Approved"
REJECTED = "Rejected"
IMPLEMENTATION = "Implementation"
IMPACT = "Impact Evaluation"
ARCHIVED = "Archived"


def create_idea(user, title, description):

    idea = Idea.objects.create(
        creator=user,
        title=title,
        description=description,
        status=DRAFT
    )
    return idea

def submit_idea(idea):
    idea.status = SUBMITTED
    idea.save()
    award_points(
        idea.creator,
        "SUBMIT_IDEA"
    )

    create_notification(
        idea.creator,
        "Idea Submitted",
        f"{idea.title} has been submitted successfully."
    )
    return idea

def add_comment(user, idea, comment):
    idea_comment = IdeaComment.objects.create(
        idea_id=idea,
        user_id=user,
        comment=comment
    )

    award_points(
        user,
        "COMMENT"
    )
    return idea_comment

def like_idea(user, idea):
    vote, created = IdeaVote.objects.get_or_create(
        user_id=user,
        idea_id=idea,
        defaults={
            "vote_type": "Like"
        }
    )
    if not created:

        vote.vote_type = "Like"
        vote.save()

    award_points(
        user,
        "LIKE"
    )

    likes = IdeaVote.objects.filter(
        idea_id=idea,
        vote_type="Like"
    ).count()

    idea.likes = likes

    if likes >= 5:
        idea.status = PM_REVIEW

    idea.save()
    return idea

def dislike_idea(user, idea):
    vote, created = IdeaVote.objects.get_or_create(
        user_id=user,
        idea_id=idea,
        defaults={
            "vote_type": "Dislike"
        }
    )

    if not created:

        vote.vote_type = "Dislike"
        vote.save()

    dislikes = IdeaVote.objects.filter(
        idea_id=idea,
        vote_type="Dislike"
    ).count()

    idea.dislikes = dislikes
    idea.save()
    return idea

@transaction.atomic
def approve_idea(
        idea,
        priority,
        due_date,
        review_comment,
        product_manager
):

    idea.priority = priority
    idea.due_date = due_date
    idea.review_comment = review_comment
    idea.status = APPROVED
    idea.approved_at = timezone.now()
    idea.save()

    award_points(
        idea.creator,
        "IDEA_APPROVED"
    )

    project = Project.objects.create(
        idea_id=idea,
        user_id=idea.creator,
        project_name=idea.title,
        description=idea.description,
        start_date=timezone.now().date(),
        progress="0%"
    )

    create_notification(
        idea.creator,
        "Idea Approved",
        "Your idea has been approved."
    )
    return project

def reject_idea(
        idea,
        review_comment
):

    idea.review_comment = review_comment
    idea.status = REJECTED
    idea.save()
    create_notification(
        idea.creator,
        "Idea Rejected",
        "Your idea was not approved."
    )

    return idea

def mark_implemented(idea):
    idea.status = IMPLEMENTATION
    idea.save()
    award_points(
        idea.creator,
        "IDEA_IMPLEMENTED"
    )

    return idea

def impact_evaluation(idea):
    idea.status = IMPACT
    idea.save()
    return idea

def archive_idea(idea):
    idea.status = ARCHIVED
    idea.save()
    return idea


def create_notification(
        user,
        title,
        message
):
    Notifications.objects.create(
        title=title,
        event_message=message,
        triggered_by=user,
        event_date=timezone.now().date(),
        entity_type="Idea",
        entity_id=str(user.id),
        entity_name=user.username
    )


