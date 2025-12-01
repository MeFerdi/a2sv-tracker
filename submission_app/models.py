from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    class Roles(models.TextChoices):
        APPLICANT = "APPLICANT", "Applicant"
        ADMIN = "ADMIN", "Admin"

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.APPLICANT,
    )
    is_finalized = models.BooleanField(default=False) # pyright: ignore[reportArgumentType]


class Question(models.Model):
    class QuestionType(models.TextChoices):
        MANDATORY = "MANDATORY", "Mandatory"
        RECOMMENDED = "RECOMMENDED", "Recommended"

    class Difficulty(models.TextChoices):
        EASY = "EASY", "Easy"
        MEDIUM = "MEDIUM", "Medium"
        HARD = "HARD", "Hard"

    title = models.CharField(max_length=255)
    leetcode_link = models.URLField()
    q_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
    )
    difficulty = models.CharField(
        max_length=10,
        choices=Difficulty.choices,
    )
    # Default True is valid at runtime; this inline directive silences a strict type-checker complaint.
    is_active = models.BooleanField(default=True)  # pyright: ignore[reportArgumentType]


class Submission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    submission_link = models.URLField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "question")


class InvitationToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    used = models.BooleanField(default=False) # pyright: ignore[reportArgumentType]
    expiry_date = models.DateTimeField()
