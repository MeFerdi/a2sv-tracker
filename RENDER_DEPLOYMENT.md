# Render Deployment Setup

## Changes Made

### 1. **Updated requirements.txt**
Added the following packages for production deployment:
- `dj-database-url==2.1.0` - For environment-based database configuration
- `gunicorn==23.0.0` - Production WSGI server
- `whitenoise==6.6.0` - Static file serving in production

### 2. **Updated A2SVTracker/settings.py**
- Added `dj_database_url` import
- Changed `DEBUG` to read from environment variable (False in production)
- Updated `ALLOWED_HOSTS` to read from environment
- Added database configuration to use `DATABASE_URL` from environment in production
- Added WhiteNoise middleware for static files
- Added `CSRF_TRUSTED_ORIGINS` for Render domains

### 3. **Created render.yaml**
Configuration file for Render with:
- Web service using Gunicorn
- Python 3.13 runtime
- PostgreSQL database service
- Build command with migrations
- Environment variables setup

## Deployment Steps for Render

1. **Push to GitHub**
   ```bash
   git add -A
   git commit -m "Configure for Render deployment"
   git push origin main
   ```

2. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

3. **Deploy from GitHub**
   - Go to Dashboard → New +
   - Select "Blueprint"
   - Connect your GitHub repository
   - Choose branch (main)
   - Render will automatically read render.yaml

4. **Or Deploy Manually**
   - Dashboard → New Web Service
   - Connect GitHub repository
   - Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Set start command: `gunicorn A2SVTracker.wsgi:application --bind 0.0.0.0:$PORT`
   - Add environment variables (see below)

## Environment Variables on Render

Set these in Render Dashboard:
- `DEBUG` = `False`
- `SECRET_KEY` = (Generate a strong key or let Render generate it)
- `ALLOWED_HOSTS` = `your-app.onrender.com`
- `DATABASE_URL` = (Auto-created by PostgreSQL service if using render.yaml)

## Database

With render.yaml:
- PostgreSQL database is automatically created
- `DATABASE_URL` is automatically injected

Without render.yaml:
- Add PostgreSQL service in Render dashboard
- Copy the connection string to `DATABASE_URL` environment variable

## After Deployment

1. **Create Superuser**
   ```bash
   # In Render Dashboard, go to Shell
   python manage.py createsuperuser
   # Or run management command
   python manage.py update_superuser --email your-email@example.com
   ```

2. **Create Invitation Tokens**
   ```bash
   python manage.py create_invite user@example.com user2@example.com
   ```

3. **Access Your App**
   - Visit: `https://your-app.onrender.com`
   - Login at: `https://your-app.onrender.com/login/`
   - Register with token at: `https://your-app.onrender.com/register/?token=YOUR_TOKEN`

## Troubleshooting

- Check logs in Render Dashboard
- Ensure all environment variables are set
- Verify DATABASE_URL is correct
- Make sure SECRET_KEY is set (not empty)
