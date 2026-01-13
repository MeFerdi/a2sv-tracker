from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import secrets
import string
from submission_app.models import InvitationToken


class Command(BaseCommand):
    help = 'Create invitation token(s) for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            'emails',
            nargs='+',
            type=str,
            help='Email addresses to create invitations for'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days until expiry (default: 7)'
        )

    def generate_6digit_code(self):
        """Generate a 6-character alphanumeric code."""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))

    def handle(self, *args, **options):
        emails = options['emails']
        days = options['days']
        expiry_date = timezone.now() + timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(f'\n  Creating invitation tokens (expires in {days} days)...\n'))
        
        for email in emails:
            # Check if email already has an unused token
            existing = InvitationToken.objects.filter(email=email, used=False).first()
            if existing:
                self.stdout.write(self.style.WARNING(f'  Email {email} already has an unused token: {existing.token}'))
                self.stdout.write(f'  Registration URL: http://localhost:8000/register/?token={existing.token}')
                self.stdout.write('')
                continue
            
            # Generate a unique 6-digit code
            token = self.generate_6digit_code()
            while InvitationToken.objects.filter(token=token).exists():
                token = self.generate_6digit_code()
            
            # Create the invitation
            invitation = InvitationToken.objects.create(
                token=token,
                email=email,
                expiry_date=expiry_date
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created invitation for: {email}'))
            self.stdout.write(f'  Token: {token}')
            self.stdout.write(f'  Registration URL: http://localhost:8000/register/?token={token}')
            self.stdout.write('')
