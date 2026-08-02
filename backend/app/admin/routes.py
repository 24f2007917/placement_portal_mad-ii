from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User, Company, Student, JobPosition, Application
from app.utils import role_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def dashboard():
    return jsonify({
        "total_students": Student.query.count(),
        "total_companies": Company.query.count(),
        "total_job_positions": JobPosition.query.count(),
        "total_applications": Application.query.count(),
        "pending_company_approvals": Company.query.filter_by(approval_status="pending").count(),
        "pending_job_approvals": JobPosition.query.filter_by(status="pending").count(),
    })


@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    status = request.args.get("status")
    query = Company.query
    if status:
        query = query.filter_by(approval_status=status)

    companies = query.all()
    result = []
    for c in companies:
        result.append({
            "id": c.id,
            "user_id": c.user_id,
            "company_name": c.company_name,
            "industry": c.industry,
            "location": c.location,
            "email": c.user.email,
            "approval_status": c.approval_status,
        })
    return jsonify(result)


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@role_required("admin")
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "approved"
    db.session.commit()
    return jsonify({"message": "company approved", "company_id": company.id})


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.approval_status = "rejected"
    db.session.commit()
    return jsonify({"message": "company rejected", "company_id": company.id})


@admin_bp.route("/companies/search", methods=["GET"])
@role_required("admin")
def search_companies():
    q = request.args.get("q", "")
    companies = Company.query.filter(
        (Company.company_name.ilike(f"%{q}%")) | (Company.industry.ilike(f"%{q}%"))
    ).all()
    result = [{"id": c.id, "company_name": c.company_name, "industry": c.industry} for c in companies]
    return jsonify(result)


@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    students = Student.query.all()
    result = []
    for s in students:
        result.append({
            "id": s.id,
            "user_id": s.user_id,
            "name": s.user.name,
            "email": s.user.email,
            "branch": s.branch,
            "cgpa": s.cgpa,
            "year": s.year,
        })
    return jsonify(result)


@admin_bp.route("/students/search", methods=["GET"])
@role_required("admin")
def search_students():
    q = request.args.get("q", "")
    students = Student.query.join(User).filter(
        (User.name.ilike(f"%{q}%")) | (User.email.ilike(f"%{q}%"))
    ).all()
    result = [{"id": s.id, "name": s.user.name, "email": s.user.email} for s in students]
    return jsonify(result)


@admin_bp.route("/users/<int:user_id>/blacklist", methods=["POST"])
@role_required("admin")
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"error": "cannot blacklist admin"}), 400
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "user blacklisted", "user_id": user.id})


@admin_bp.route("/users/<int:user_id>/activate", methods=["POST"])
@role_required("admin")
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    return jsonify({"message": "user activated", "user_id": user.id})


@admin_bp.route("/job-positions", methods=["GET"])
@role_required("admin")
def list_job_positions():
    status = request.args.get("status")
    query = JobPosition.query
    if status:
        query = query.filter_by(status=status)

    jobs = query.all()
    result = []
    for j in jobs:
        result.append({
            "id": j.id,
            "title": j.title,
            "company_name": j.company.company_name,
            "salary": j.salary,
            "application_deadline": j.application_deadline.isoformat(),
            "status": j.status,
        })
    return jsonify(result)


@admin_bp.route("/job-positions/<int:job_id>/approve", methods=["POST"])
@role_required("admin")
def approve_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    job.status = "approved"
    db.session.commit()
    return jsonify({"message": "job position approved", "job_id": job.id})


@admin_bp.route("/job-positions/<int:job_id>/reject", methods=["POST"])
@role_required("admin")
def reject_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    job.status = "rejected"
    db.session.commit()
    return jsonify({"message": "job position rejected", "job_id": job.id})


@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def list_all_applications():
    from app.models import Application
    applications = Application.query.all()
    result = []
    for a in applications:
        result.append({
            "id": a.id,
            "student_name": a.student.user.name,
            "student_email": a.student.user.email,
            "job_title": a.job.title,
            "company_name": a.job.company.company_name,
            "status": a.status,
            "application_date": a.application_date.isoformat(),
        })
    return jsonify(result)


@admin_bp.route("/students/<int:student_id>", methods=["GET"])
@role_required("admin")
def view_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({
        "id": student.id,
        "name": student.user.name,
        "email": student.user.email,
        "branch": student.branch,
        "cgpa": student.cgpa,
        "year": student.year,
        "skills": student.skills,
        "is_active": student.user.is_active,
        "applications": [
            {
                "job_title": a.job.title,
                "company_name": a.job.company.company_name,
                "status": a.status,
            } for a in student.applications
        ],
    })