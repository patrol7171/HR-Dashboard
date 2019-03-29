web: gunicorn hr_dashboard.app:app
worker: celery worker --app=hr_dashboard.app --loglevel=INFO
