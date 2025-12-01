from django.apps import AppConfig


class SubmissionAppConfig(AppConfig):
    # Runtime is correct; this inline directive silences a strict type-checker
    default_auto_field = 'django.db.models.BigAutoField'  # pyright: ignore[reportAssignmentType]
    name = 'submission_app'
