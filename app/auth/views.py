import logging
import secrets

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla.view import ModelView
from flask_admin.form import SecureForm, rules
from flask_login import current_user, login_user, logout_user, login_required
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint, github
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash
from wtforms import PasswordField

from app import db, login_manager
from .forms import LoginForm, RegistrationFrom
from .models import OAuth, User

auth = Blueprint("auth", __name__)
github_bp = make_github_blueprint(
    redirect_to="auth.home",
    storage=SQLAlchemyStorage(OAuth, db.session, user=current_user),
)


@oauth_authorized.connect_via(github_bp)
def github_logged_in(blueprint, token):
    if not token:
        flash("Log in via GitHub failed.", "negative")
        return False

    resp = blueprint.session.get("/user")
    if not resp.ok:
        flash("Fetching user info from GitHub failed.", "negative")
        return False

    github_info = resp.json()
    github_user_id = str(github_info["id"])

    query = OAuth.query.filter_by(
        provider=blueprint.name, provider_user_id=github_user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name, provider_user_id=github_user_id, token=token
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Log in via GitHub successful.", "positive")
    else:
        user = User(username=github_info["name"], password=secrets.token_hex(64))

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()

        login_user(user)
        flash("Log in via GitHub successful.", "positive")

    return False


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth.before_request
def get_current_user():
    g.user = current_user


@auth.context_processor
def search_form():
    from app.forms import SearchForm

    def _search_form():
        return SearchForm()

    return {"search_form": _search_form}


@auth.route("/")
@auth.route("/home")
def home():
    return render_template("home.html")


@auth.route("/register", methods=["GET", "POST"])
def register():
    if session.get("username"):
        flash("You are already logged in.")
        return redirect(url_for("auth.home"))

    form = RegistrationFrom()

    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash("This username is already taken.", "negative")
            return render_template("register.html", form=form)

        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "positive")
        return redirect(url_for("auth.login"))

    if form.errors:
        flash(form.errors, "negative")

    return render_template("register.html", form=form)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.")
        return redirect(url_for("auth.home"))

    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        existing_user = User.query.filter_by(username=username).first()

        if not (existing_user and existing_user.check_password(password)):
            flash("Invalid username or password.", "negative")
            return render_template("login.html", form=form)

        login_user(existing_user)
        flash("Login successful.", "positive")
        return redirect(url_for("auth.home"))

    if form.errors:
        flash(form.errors, "negative")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f"Logged out {username}")
    return redirect(url_for("auth.home"))


class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class DefaultAdminView(ModelView):
    form_base_class = SecureForm
    can_view_details = True


class UserAdminView(DefaultAdminView):
    column_editable_list = ["username", "admin"]
    column_searchable_list = ["username"]
    column_sortable_list = ["username", "admin"]
    column_exclude_list = ["pwdhash"]
    column_filters = ["username", "admin"]
    form_excluded_columns = ["pwdhash"]
    form_edit_rules = [
        "username",
        "admin",
        rules.Header("Reset Password"),
        "new_password",
        "confirm",
    ]
    form_create_rules = ["username", "admin", "password"]

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField("Password")
        form_class.new_password = PasswordField("New Password")
        form_class.confirm = PasswordField("Confirm New Password")
        return form_class

    def create_model(self, form):
        model = self.model(form.username.data, form.password.data, form.admin.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    def update_model(self, form, model):
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                flash("Passwords must match")
                return
            model.pwdhash = generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()


class ProductAdminView(DefaultAdminView):
    column_list = ["name", "price", "image_path", "category"]


class CategoryAdminView(DefaultAdminView):
    def scaffold_form(self):
        form_class = super(CategoryAdminView, self).scaffold_form()
        del form_class.products
        return form_class
