from django.db import models
from Base.models import BaseModel

# defining models for the ideas
class Idea(BaseModel):

    STATUS_CHOICES = [
        ("Draft", "Draft"),
        ("Submitted", "Submitted"),
        ("Peer Review", "Peer Review"),
        ("Product Manager Review", "Product Manager Review"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Implementation", "Implementation"),
        ("Impact Evaluation", "Impact Evaluation"),
        ("Archived", "Archived"),
    ]

    PRIORITY_CHOICES = [
        ("High", "High"),
        ("Medium", "Medium"),
        ("Low", "Low"),
    ]

    creator = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=150, null=True, blank=True)

    description = models.TextField(null=True, blank=True)

    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Draft"
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        blank=True,
        null=True
    )

    due_date = models.DateField(
        blank=True,
        null=True
    )

    review_comment = models.TextField(
        blank=True,
        null=True
    )

    likes = models.IntegerField(default=0)

    dislikes = models.IntegerField(default=0)

    approved_at = models.DateTimeField(
        blank=True,
        null=True
    )



class IdeaComment(BaseModel):
    idea_id = models.ForeignKey('Idea', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)




class IdeaVote(BaseModel):
    idea_id = models.ForeignKey('Idea', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    VOTE_CHOICES = [

        ("Like", "Like"),

        ("Dislike", "Dislike")

    ]
    vote_type = models.CharField(
        max_length=20,
        choices=VOTE_CHOICES, null=True,blank=True
    )

    def __str__(self):
        return f"{self.idea_id} ({self.vote_type})"


