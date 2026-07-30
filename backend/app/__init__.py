from flask import Flask
from app.config import Config
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app import models  # ensures User table is registered with SQLAlchemy

    @app.route("/")
    def home():
        return {"message": "Placement Portal API running"}

    return app