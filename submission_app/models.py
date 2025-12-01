from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Roles(models.TextChoices):
        APPLICANT = "APPLICANT", "Applicant"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.APPLICANT,
    )
    is_finalized = models.BooleanField(default=False)
