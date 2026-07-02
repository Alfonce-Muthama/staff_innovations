from django.db import models
import uuid


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


def get_default_state():
    state, created = State.objects.get_or_create(
        name="Active",
        defaults={
            "description": "Default active state"
        }
    )
    return state.id


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        default=get_default_state
    )

    class Meta:
        abstract = True


class GenericBaseModel(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

