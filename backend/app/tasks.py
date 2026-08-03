import csv
import io
import os
from datetime import datetime, timedelta

from app import create_app
from app.celery_app import make_celery

flask_app = create_app()
celery = make_celery(flask_app)

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


@celery.task(name="app.tasks.send_interview_reminders")
def send_interview_reminders():
    """Scheduled job: remind students with applications in 'interview' status."""
    from app.models import Application

    interviews = Application.query.filter_by(status="interview").all()
    count = 0
    for app_row in interviews:
        message = (
            f"Reminder: {app_row.student.user.name}, you have an interview scheduled "
            f"for '{app_row.job.title}' at {app_row.job.company.company_name}."
        )
        print(f"[REMINDER] {message}")  # placeholder for real email/SMS/GChat webhook
        count += 1
    return f"Sent {count} interview reminders."


@celery.task(name="app.tasks.generate_monthly_report")
def generate_monthly_report():
    """Scheduled job: monthly placement activity report."""
    from app.models import JobPosition, Application

    first_of_this_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

    jobs = JobPosition.query.filter(
        JobPosition.created_at >= first_of_last_month,
        JobPosition.created_at < first_of_this_month,
    ).all()
    applications = Application.query.filter(
        Application.application_date >= first_of_last_month,
        Application.application_date < first_of_this_month,
    ).all()
    placed = [a for a in applications if a.status == "placed"]

    html = f"""
    <h2>Monthly Placement Activity Report</h2>
    <p>Period: {first_of_last_month.date()} to {first_of_this_month.date()}</p>
    <ul>
        <li>Job postings: {len(jobs)}</li>
        <li>Applications: {len(applications)}</li>
        <li>Placements: {len(placed)}</li>
    </ul>
    """

    report_path = os.path.join(EXPORT_DIR, f"monthly_report_{first_of_last_month.strftime('%Y_%m')}.html")
    with open(report_path, "w") as f:
        f.write(html)

    print(f"[REPORT] Generated at {report_path}")
    return report_path


@celery.task(name="app.tasks.export_applications_csv")
def export_applications_csv(student_id):
    """User-triggered async job: export a student's application history to CSV."""
    from app.models import Student

    student = Student.query.get(student_id)
    if not student:
        return {"error": "student not found"}

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Student", "Company", "Job Title", "Status", "Application Date"])
    for a in student.applications:
        writer.writerow([
            student.user.name,
            a.job.company.company_name,
            a.job.title,
            a.status,
            a.application_date.isoformat(),
        ])

    filename = f"applications_student_{student_id}_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(EXPORT_DIR, filename)
    with open(filepath, "w", newline="") as f:
        f.write(buffer.getvalue())

    print(f"[EXPORT] CSV ready: {filename}")
    return {"file": filename, "path": filepath}