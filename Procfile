web: gunicorn hr_dashboard.app:app
worker: celery -A hr_dashboard.app:celery worker --loglevel=info