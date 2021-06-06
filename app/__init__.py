import os

from redis import Redis
import secrets

from flask import Flask
from flask_admin import Admin
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg", "gif"])
basedir = os.path.abspath(os.path.dirname(__file__))


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
redis = Redis()
csrf = CSRFProtect()
my_api = Api(decorators=[csrf.exempt])
from .auth.views import CustomAdminIndexView

admin = Admin(index_view=CustomAdminIndexView())

# Initialize REST APIs
from .api import ProductApi

my_api.add_resource(
    ProductApi,
    "/api/v1/product",
    "/api/v1/product/<int:id>",
)


def create_app():
    # Ensure tables are created by db.create_all()
    from .models import Product, Category
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
    my_api.init_app(app)
    admin.init_app(app)
    csrf.init_app(app)

    # Initialize database
    db.create_all(app=app)

    # Apply the blueprints for views
    from .views import bp
    from .auth.views import auth, github_bp

    app.register_blueprint(bp)
    app.register_blueprint(auth)
    app.register_blueprint(github_bp, url_prefix="/login")

    # Add admin views
    from .auth.views import (
        DefaultAdminView,
        CategoryAdminView,
        ProductAdminView,
        UserAdminView,
    )

    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(ProductAdminView(Product, db.session))
    admin.add_view(CategoryAdminView(Category, db.session))

    # Set up error handlers
    app.register_error_handler(400, views.bad_request)
    app.register_error_handler(404, views.page_not_found)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, ssl_context="adhoc")
