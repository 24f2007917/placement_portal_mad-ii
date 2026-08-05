from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db, cache
from app.models import Student, JobPosition, Application
from app.utils import role_required
from datetime import datetime

student_bp = Blueprint("student", __name__)


def _current_student():
    user_id = int(get_jwt_identity())
    return Student.query.filter_by(user_id=user_id).first()


@student_bp.route("/profile", methods=["GET"])
@role_required("student")
def get_profile():
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404
    return jsonify({
        "id": student.id,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year,
        "skills": student.skills,
        "resume_path": student.resume_path,
    })


@student_bp.route("/profile", methods=["PUT"])
@role_required("student")
def update_profile():
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404

    data = request.get_json()
    student.branch = data.get("branch", student.branch)
    student.cgpa = data.get("cgpa", student.cgpa)
    student.year = data.get("year", student.year)
    student.skills = data.get("skills", student.skills)
    db.session.commit()
    return jsonify({"message": "profile updated"})


@student_bp.route("/job-positions", methods=["GET"])
@role_required("student")
@cache.cached(timeout=60, query_string=True)
def browse_jobs():
    """Only approved jobs are visible to students, per the guidelines."""
    search = request.args.get("q", "")
    query = JobPosition.query.filter_by(status="approved")
    if search:
        query = query.filter(JobPosition.title.ilike(f"%{search}%"))

    jobs = query.all()
    student = _current_student()
    applied_job_ids = {a.job_id for a in student.applications} if student else set()

    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "company_name": j.company.company_name,
            "description": j.description,
            "skills_required": j.skills_required,
            "salary": j.salary,
            "min_cgpa": j.min_cgpa,
            "eligible_branches": j.eligible_branches,
            "application_deadline": j.application_deadline.isoformat(),
            "already_applied": j.id in applied_job_ids,
        })
    return jsonify(result)


@student_bp.route("/job-positions/<int:job_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_job(job_id):
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404

    job = JobPosition.query.get_or_404(job_id)

    if job.status != "approved":
        return jsonify({"error": "this job posting is not open for applications"}), 400

    if job.application_deadline < datetime.utcnow():
        return jsonify({"error": "application deadline has passed"}), 400

    existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if existing:
        return jsonify({"error": "you have already applied to this job"}), 409

    application = Application(student_id=student.id, job_id=job.id, status="applied")
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "application submitted", "application_id": application.id}), 201


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def my_applications():
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404

    result = []
    for a in student.applications:
        result.append({
            "id": a.id,
            "job_title": a.job.title,
            "company_name": a.job.company.company_name,
            "status": a.status,
            "application_date": a.application_date.isoformat(),
        })
    return jsonify(result)


@student_bp.route("/dashboard", methods=["GET"])
@role_required("student")
def dashboard():
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404

    return jsonify({
        "branch": student.branch,
        "cgpa": student.cgpa,
        "total_applications": len(student.applications),
        "shortlisted_count": len([a for a in student.applications if a.status in ("shortlisted", "interview", "offer", "placed")]),
    })


@student_bp.route("/export-applications", methods=["POST"])
@role_required("student")
def export_applications():
    student = _current_student()
    if not student:
        return jsonify({"error": "profile not found"}), 404

    from app.tasks import export_applications_csv
    task = export_applications_csv.delay(student.id)
    return jsonify({"message": "export started", "task_id": task.id}), 202