import os

from redis import Redis
import secrets

from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
basedir = os.path.abspath(os.path.dirname(__file__))


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
redis = Redis()
csrf = CSRFProtect()


def create_app():
    # Ensure tables are created by db.create_all()
    from .models import Product
    from .auth.models import User

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "test.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.realpath(".") + "/app/static/uploads"
    app.config["GITHUB_OAUTH_CLIENT_ID"] = os.environ.get("GITHUB_OAUTH_CLIENT_ID")
    app.config["GITHUB_OAUTH_CLIENT_SECRET"] = os.environ.get(
        "GITHUB_OAUTH_CLIENT_SECRET"
    )

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    csrf.init_app(app)

    # Initialize database
    db.create_all(app=app)

    # Apply the blueprint for views
    from .views import bp
    from .auth.views import auth, github_bp

    app.register_blueprint(bp)
    app.register_blueprint(auth)
    app.register_blueprint(github_bp, url_prefix="/login")

    # Set up error handlers
    app.register_error_handler(400, views.bad_request)
    app.register_error_handler(404, views.page_not_found)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, ssl_context="adhoc")
