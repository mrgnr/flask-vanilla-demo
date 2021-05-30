import os

from redis import Redis
import secrets

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
basedir = os.path.abspath(os.path.dirname(__file__))


db = SQLAlchemy()
migrate = Migrate()
redis = Redis()
csrf = CSRFProtect()


def create_app():
    # Ensure product table is created by db.create_all()
    from .models import Product

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "test.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.realpath(".") + "/app/static/uploads"

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Initialize database
    db.create_all(app=app)

    # Apply the blueprint for views
    from . import views

    app.register_blueprint(views.bp)

    # Set up error handlers
    app.register_error_handler(400, views.bad_request)
    app.register_error_handler(404, views.page_not_found)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
