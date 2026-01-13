from django.core.management.base import BaseCommand
from submission_app.models import User


class Command(BaseCommand):
    help = 'Update superuser email and role'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Set a specific email for the superuser'
        )

    def handle(self, *args, **options):
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            self.stdout.write(f"Found superuser: {superuser.username}")
            self.stdout.write(f"Email before: {superuser.email}")
            self.stdout.write(f"Role before: {superuser.role}")
            
            email = options.get('email')
            if email:
                # Set both username and email to the provided email
                superuser.username = email
                superuser.email = email
                self.stdout.write(f"Setting username and email to: {email}")
            elif not superuser.email or superuser.email == superuser.username:
                # If no email provided and current email is invalid, use username
                superuser.email = superuser.username
            
            # Always set role to ADMIN
            superuser.role = User.Roles.ADMIN
            superuser.save()
            
            self.stdout.write(f"Username after: {superuser.username}")
            self.stdout.write(f"Email after: {superuser.email}")
            self.stdout.write(f"Role after: {superuser.role}")
            self.stdout.write(self.style.SUCCESS('Superuser updated successfully!'))
            self.stdout.write(self.style.WARNING(f'\nYou can now login with:'))
            self.stdout.write(f'  Email: {superuser.email}')
            self.stdout.write(f'  Password: (your superuser password)')
        else:
            self.stdout.write(self.style.ERROR('No superuser found'))
