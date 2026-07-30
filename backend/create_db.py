from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Database created successfully.")

    admin_email = "admin@ppa.local"
    existing_admin = User.query.filter_by(email=admin_email).first()

    if not existing_admin:
        admin = User(
            name="Institute Admin",
            email=admin_email,
            password_hash=generate_password_hash("Admin@123"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_email} / Admin@123")
    else:
        print("Admin user already exists, skipping.")