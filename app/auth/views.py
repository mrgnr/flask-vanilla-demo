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
from flask_login import current_user, login_user, logout_user, login_required
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_dance.contrib.github import make_github_blueprint, github
from sqlalchemy.exc import NoResultFound

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
