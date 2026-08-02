from flask import Flask
from app.config import Config
from app.extensions import db, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    from app import models

    from app.auth.routes import auth_bp
    from app.admin.routes import admin_bp
    from app.company.routes import company_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(company_bp, url_prefix="/api/company")

    @app.route("/")
    def home():
        return {"message": "Placement Portal API running"}

    return app