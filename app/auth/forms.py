from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField
from wtforms.validators import InputRequired, EqualTo


class RegistrationFrom(FlaskForm):
    username = TextField("Username", [InputRequired()])
    password = PasswordField(
        "Password",
        [InputRequired(), EqualTo("confirm", message="Passwords must match")],
    )
    confirm = PasswordField("Confirm password", [InputRequired()])


class LoginForm(FlaskForm):
    username = TextField("Username", [InputRequired()])
    password = PasswordField("Password", [InputRequired()])
