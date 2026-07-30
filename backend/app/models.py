from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    hr_contact = db.Column(db.String(120))
    website = db.Column(db.String(200))
    approval_status = db.Column(db.String(20), default="pending")
    user = db.relationship("User", backref="company_profile")


class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    branch = db.Column(db.String(80))
    cgpa = db.Column(db.Float)
    year = db.Column(db.Integer)
    skills = db.Column(db.String(255))
    resume_path = db.Column(db.String(255))
    user = db.relationship("User", backref="student_profile")


class JobPosition(db.Model):
    __tablename__ = "job_positions"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    skills_required = db.Column(db.String(255))
    salary = db.Column(db.String(50))
    eligible_branches = db.Column(db.String(255))
    min_cgpa = db.Column(db.Float, default=0)
    application_deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    company = db.relationship("Company", backref="job_positions")


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("job_positions.id"), nullable=False)
    status = db.Column(db.String(20), default="applied")
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="applications")
    job = db.relationship("JobPosition", backref="applications")
    __table_args__ = (db.UniqueConstraint("student_id", "job_id", name="uq_student_job"),)


class Placement(db.Model):
    __tablename__ = "placements"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False)
    position = db.Column(db.String(150))
    salary = db.Column(db.String(50))
    joining_date = db.Column(db.DateTime)
    student = db.relationship("Student", backref="placements")
    company = db.relationship("Company", backref="placements")