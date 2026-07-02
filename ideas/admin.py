from django.contrib import admin
from .models import Idea, IdeaComment, IdeaVote

admin.site.register(Idea)
admin.site.register(IdeaComment)
admin.site.register(IdeaVote)
