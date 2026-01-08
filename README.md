# A2SV Tracker

A Django-based application for tracking applicant progress on coding questions. This project has been simplified to use Django templates instead of a separate React frontend.

## Architecture

- **Backend**: Django 5.2.8 with PostgreSQL
- **Frontend**: Django Templates with Tailwind CSS (via CDN)
- **Authentication**: Django's built-in session-based authentication

## Project Structure

```
a2sv-tracker/
├── A2SVTracker/           # Django project settings
│   ├── settings.py       # Configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py          # WSGI entry point
├── submission_app/        # Main application
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── forms.py          # Django forms
│   ├── admin.py          # Admin configuration
│   └── migrations/       # Database migrations
├── templates/             # HTML templates
│   ├── base.html         # Base template
│   ├── auth/             # Authentication templates
│   ├── applicant/        # Applicant dashboard
│   └── admin/            # Admin dashboard
├── static/               # Static files (CSS, JS)
└── manage.py            # Django management script
```

## Features

### For Applicants
- Register using invitation tokens
- View mandatory and recommended questions
- Submit LeetCode solution links
- Track progress (15 mandatory minimum)
- Finalize application when requirements met

### For Admins
- View dashboard with statistics
- Manage questions (CRUD operations)
- Track applicant rankings
- Export applicant data as CSV
- Generate invitation tokens via Django admin

## Setup Instructions

### 1. Prerequisites
- Python 3.10+
- PostgreSQL database
- pip (Python package manager)

### 2. Database Setup

Create a PostgreSQL database:

```bash
psql -U postgres
CREATE DATABASE a2svtracker_dev;
\q
```

Update database credentials in `A2SVTracker/settings.py` if needed:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'a2svtracker_dev',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Environment Setup

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account with role='ADMIN'.

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to access the application.

## Usage Guide

### Admin Workflow

1. **Login**: Access `http://localhost:8000/login/` with admin credentials
2. **Create Questions**: Navigate to Questions management
3. **Generate Invitations**: Use Django admin at `http://localhost:8000/admin/`
   - Go to Invitation Tokens
   - Add a new token with email and expiry date
   - Share the token link: `http://localhost:8000/register/?token=YOUR_TOKEN`
4. **Track Applicants**: View the applicant tracker to see rankings and progress
5. **Export Data**: Download CSV of all applicants

### Applicant Workflow

1. **Register**: Click the invitation link and set your name/password
2. **Login**: Access your dashboard
3. **View Questions**: See mandatory (15 required) and recommended questions
4. **Submit Solutions**: Click "Submit" on any question and paste your LeetCode link
5. **Finalize**: Once 15 mandatory questions are completed, click "Finalize Application"

## URL Structure

### Authentication
- `/` - Home (redirects to login)
- `/login/` - Login page
- `/register/?token=<token>` - Registration with invitation token
- `/logout/` - Logout

### Applicant Routes
- `/applicant/` - Applicant dashboard
- `/applicant/submit/<id>/` - Submit solution for a question
- `/applicant/finalize/` - Finalize application

### Admin Routes
- `/admin-dashboard/` - Admin dashboard
- `/admin-dashboard/questions/` - Question management
- `/admin-dashboard/questions/create/` - Create new question
- `/admin-dashboard/questions/<id>/edit/` - Edit question
- `/admin-dashboard/questions/<id>/delete/` - Delete (soft) question
- `/admin-dashboard/applicants/` - Applicant tracker
- `/admin-dashboard/applicants/export/` - Export CSV

## Models

### User
- **Fields**: email, first_name, role (APPLICANT/ADMIN), is_finalized
- **Auth**: Uses Django's AbstractUser with custom role field

### Question
- **Fields**: title, leetcode_link, q_type (MANDATORY/RECOMMENDED), difficulty (EASY/MEDIUM/HARD), is_active
- **Purpose**: Stores coding questions for applicants

### Submission
- **Fields**: user, question, submission_link, submitted_at
- **Constraint**: Unique together (user, question)

### InvitationToken
- **Fields**: token, email, used, expiry_date
- **Purpose**: Token-based registration system

## Key Changes from Previous Version

 **Removed**: 
- React frontend (entire `frontend/` directory)
- Django REST Framework
- JWT authentication
- CORS configuration
- Complex API structure

 **Added**:
- Django templates with Tailwind CSS
- Session-based authentication
- Server-side rendering
- Simplified URL routing
- Django forms for validation

 **Benefits**:
- Single technology stack (Django only)
- Easier deployment
- Better SEO
- Reduced complexity
- No frontend build process
- Faster development

## Development Tips

### Creating an Admin User

If you need to manually set a user as admin:

```bash
python manage.py shell
```

```python
from submission_app.models import User
user = User.objects.get(email='admin@example.com')
user.role = User.Roles.ADMIN
user.is_staff = True
user.is_superuser = True
user.save()
```

### Adding Test Questions

Use Django admin or shell:

```python
from submission_app.models import Question

Question.objects.create(
    title="Two Sum",
    leetcode_link="https://leetcode.com/problems/two-sum/",
    q_type="MANDATORY",
    difficulty="EASY",
    is_active=True
)
```

### Generating Invitation Tokens

```python
from submission_app.models import InvitationToken
from django.utils import timezone
from datetime import timedelta
import secrets

token = InvitationToken.objects.create(
    token=secrets.token_urlsafe(32),
    email="applicant@example.com",
    expiry_date=timezone.now() + timedelta(days=7)
)

print(f"Registration link: http://localhost:8000/register/?token={token.token}")
```

## Production Deployment

### Additional Settings for Production

In `settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
STATIC_ROOT = BASE_DIR / 'staticfiles'
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### Collect Static Files

```bash
python manage.py collectstatic
```

### Use a Production Server

Install and configure gunicorn:

```bash
pip install gunicorn
gunicorn A2SVTracker.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Verify database credentials in settings.py
- Check database exists: `psql -U postgres -l`

### Template Not Found
- Verify TEMPLATES DIRS in settings.py includes `BASE_DIR / 'templates'`
- Check template files exist in correct directories

### Static Files Not Loading
- Ensure Tailwind CDN link is in base.html
- For production, run `collectstatic` command

### Permission Denied
- Check user role is set correctly (APPLICANT or ADMIN)
- Verify login_required decorators are in place

## Contributing

When adding new features:
1. Create views in `submission_app/views.py`
2. Add URL patterns in `A2SVTracker/urls.py`
3. Create templates in appropriate `templates/` subdirectory
4. Update this README with new functionality

## License

This project is for A2SV internal use.
