from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import Company, JobPosition, Application, Student
from app.utils import role_required
from datetime import datetime

company_bp = Blueprint("company", __name__)


def _current_company():
    user_id = int(get_jwt_identity())
    return Company.query.filter_by(user_id=user_id).first()


@company_bp.route("/profile", methods=["GET"])
@role_required("company")
def get_profile():
    company = _current_company()
    if not company:
        return jsonify({"error": "profile not found"}), 404
    return jsonify({
        "id": company.id,
        "company_name": company.company_name,
        "industry": company.industry,
        "location": company.location,
        "hr_contact": company.hr_contact,
        "website": company.website,
        "approval_status": company.approval_status,
    })


@company_bp.route("/profile", methods=["PUT"])
@role_required("company")
def update_profile():
    company = _current_company()
    if not company:
        return jsonify({"error": "profile not found"}), 404

    data = request.get_json()
    company.company_name = data.get("company_name", company.company_name)
    company.industry = data.get("industry", company.industry)
    company.location = data.get("location", company.location)
    company.hr_contact = data.get("hr_contact", company.hr_contact)
    company.website = data.get("website", company.website)
    db.session.commit()
    return jsonify({"message": "profile updated"})


@company_bp.route("/dashboard", methods=["GET"])
@role_required("company")
def dashboard():
    company = _current_company()
    if not company:
        return jsonify({"error": "profile not found"}), 404

    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    total_applicants = sum(len(j.applications) for j in jobs)

    return jsonify({
        "company_name": company.company_name,
        "approval_status": company.approval_status,
        "total_job_postings": len(jobs),
        "total_applicants": total_applicants,
    })

@company_bp.route("/job-positions", methods=["POST"])
@role_required("company")
def create_job_position():
    company = _current_company()
    if not company:
        return jsonify({"error": "profile not found"}), 404

    if company.approval_status != "approved":
        return jsonify({"error": "company must be approved by admin before posting jobs"}), 403

    data = request.get_json()
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    deadline_str = data.get("application_deadline")
    try:
        deadline = datetime.fromisoformat(deadline_str)
    except (TypeError, ValueError):
        return jsonify({"error": "application_deadline must be ISO format, e.g. 2026-08-31T00:00:00"}), 400

    job = JobPosition(
        company_id=company.id,
        title=title,
        description=data.get("description", ""),
        skills_required=data.get("skills_required", ""),
        salary=data.get("salary", ""),
        eligible_branches=data.get("eligible_branches", ""),
        min_cgpa=data.get("min_cgpa", 0),
        application_deadline=deadline,
        status="pending",
    )
    db.session.add(job)
    db.session.commit()
    return jsonify({"message": "job position submitted for approval", "job_id": job.id}), 201


@company_bp.route("/job-positions", methods=["GET"])
@role_required("company")
def list_own_job_positions():
    company = _current_company()
    if not company:
        return jsonify({"error": "profile not found"}), 404

    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "status": j.status,
            "application_deadline": j.application_deadline.isoformat(),
            "applicant_count": len(j.applications),
        })
    return jsonify(result)


@company_bp.route("/job-positions/<int:job_id>/applicants", methods=["GET"])
@role_required("company")
def view_applicants(job_id):
    company = _current_company()
    job = JobPosition.query.get_or_404(job_id)

    if job.company_id != company.id:
        return jsonify({"error": "not your job posting"}), 403

    applications = Application.query.filter_by(job_id=job.id).all()
    result = []
    for a in applications:
        result.append({
            "application_id": a.id,
            "student_name": a.student.user.name,
            "student_email": a.student.user.email,
            "branch": a.student.branch,
            "cgpa": a.student.cgpa,
            "status": a.status,
            "application_date": a.application_date.isoformat(),
        })
    return jsonify(result)


@company_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@role_required("company")
def update_application_status(application_id):
    company = _current_company()
    application = Application.query.get_or_404(application_id)

    if application.job.company_id != company.id:
        return jsonify({"error": "not your application to manage"}), 403

    data = request.get_json()
    new_status = data.get("status")
    valid_statuses = ("applied", "shortlisted", "interview", "offer", "rejected", "placed")
    if new_status not in valid_statuses:
        return jsonify({"error": f"status must be one of {valid_statuses}"}), 400

    application.status = new_status
    db.session.commit()
    return jsonify({"message": "application status updated", "new_status": new_status})