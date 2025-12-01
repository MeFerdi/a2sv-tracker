## A2SVTracker

Django-based tracker application with a primary app `submission_app`.

### Tech Stack
- Python 3.12
- Django 5.x
- Django REST framework
- PostgreSQL

### Setup
1. Create and activate virtual environment (if not already):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure PostgreSQL credentials in `A2SVTracker/settings.py` if they differ from defaults.
4. Run migrations and start the development server:
   ```bash
   python manage.py migrate
   python manage.py runserver
   ```
