from django.db import models
from Base.models import BaseModel

# defining models for the ideas
class Idea(BaseModel):
    creator = models.ForeignKey("users.User", on_delete=models.CASCADE)
    title = models.CharField(max_length=150,null=True, blank=True)
    description = models.FileField(null=True, blank=True)



class IdeaComment(BaseModel):
    idea_id = models.ForeignKey('Idea', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)




class IdeaVote(BaseModel):
    idea_id = models.ForeignKey('Idea', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    vote_type = models.CharField(max_length=30,null=True, blank=True)

    def __str__(self):
        return f"{self.idea_id} ({self.vote_type})"


