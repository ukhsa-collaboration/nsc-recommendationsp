from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _


class User(AbstractUser):
    last_session_id = models.CharField(max_length=40, default="", blank=True)
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )

    class Meta(AbstractUser.Meta):
        swappable = "AUTH_USER_MODEL"
        db_table = "auth_user"
