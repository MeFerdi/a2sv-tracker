#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'A2SVTracker.settings')
django.setup()

from submission_app.models import User

# Get the superuser
superuser = User.objects.filter(is_superuser=True).first()
if superuser:
    print(f"Found superuser: {superuser.username}")
    print(f"Current email: {superuser.email}")
    print(f"Current role: {superuser.role}")
    
    # Update to the correct email
    email = "ferdinandodhis254@gmail.com"
    superuser.username = email
    superuser.email = email
    superuser.role = User.Roles.ADMIN
    superuser.save()
    
    print(f"\nUpdated username to: {superuser.username}")
    print(f"Updated email to: {superuser.email}")
    print(f"Updated role to: {superuser.role}")
    print("\n✅ Superuser updated successfully!")
    print(f"\nYou can now login with:")
    print(f"  Email: {superuser.email}")
    print(f"  Password: (your superuser password)")
else:
    print("❌ No superuser found")
