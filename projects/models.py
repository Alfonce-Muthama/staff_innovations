from django.db import models
from Base.models import BaseModel

# defining models for the project execution
class Project(BaseModel):
    idea_id = models.ForeignKey('ideas.Idea', on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project_name = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)



class ProjectPhase(BaseModel):
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    phase_name = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)



class  Task(BaseModel):
    project_phase_id = models.ForeignKey('ProjectPhase', on_delete=models.CASCADE)
    assigned_to = models.ForeignKey('users.User', on_delete=models.CASCADE)
    title = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    priority = models.CharField(max_length=30,null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title




