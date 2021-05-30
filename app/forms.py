from decimal import Decimal

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import InputRequired, NumberRange, ValidationError

from .models import Category


def check_duplicate_category():
    def _check_duplicate(form, field):
        res = Category.query.filter(Category.name.ilike("%" + field.data + "%")).first()
        if res:
            raise ValidationError(f"Category named {field.data} already exists")

    return _check_duplicate


class CategoryField(SelectField):
    def iter_choices(self):
        categories = [(c.id, c.name) for c in Category.query.all()]
        for value, label in categories:
            yield (value, label, self.coerce(value) == self.data)

    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in Category.query.all()]:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext("Not a valid choice"))


class NameForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired()])


class ProductForm(NameForm):
    price = DecimalField(
        "Price", validators=[InputRequired(), NumberRange(min=Decimal("0.0"))]
    )
    category = CategoryField("Category", validators=[InputRequired()], coerce=int)
    image = FileField("Product image")


class CategoryForm(NameForm):
    name = StringField("Name", validators=[InputRequired(), check_duplicate_category()])


class SearchForm(FlaskForm):
    query = StringField("Query", validators=[InputRequired()])
