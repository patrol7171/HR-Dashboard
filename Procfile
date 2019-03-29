web: gunicorn hr_dashboard.app:app
worker: celery worker -A app.celery --loglevel=info