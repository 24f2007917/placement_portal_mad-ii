from celery import Celery
from celery.schedules import crontab

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
        include=["app.tasks"],
    )

    celery.conf.beat_schedule = {
        "daily-interview-reminders": {
            "task": "app.tasks.send_interview_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
        "monthly-placement-report": {
            "task": "app.tasks.generate_monthly_report",
            "schedule": crontab(hour=6, minute=0, day_of_month=1),
        },
    }

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery