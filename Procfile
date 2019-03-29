web: gunicorn hr_dashboard.app:app
worker: celery worker -A hr_dashboard.celery --loglevel=info
