from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


def get_default_state():
    state, created = State.objects.get_or_create(
        name="Active",
        defaults={"description": "Default active state"},
    )
    return state.id


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_('id'))
    created_at = models.DateTimeField(auto_now_add=True , verbose_name=_('Date created'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Date modified'))
    state = models.ForeignKey(
        "Base.State",
        on_delete=models.CASCADE,
        default=get_default_state,
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


class State(GenericBaseModel):
    state = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
        related_name="child_states",
    )
