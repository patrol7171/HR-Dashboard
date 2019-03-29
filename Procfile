web: gunicorn hr_dashboard.app:app
worker: celery worker --app=app.celery --loglevel=INFO