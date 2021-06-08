import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from app import ALLOWED_EXTENSIONS, db
from .models import Category, Product
from .forms import CategoryForm, ProductForm, SearchForm

bp = Blueprint("main", __name__)


def allowed_file(filename):
    return (
        filename
        and "." in filename
        and filename.lower().rsplit(".", 1)[1] in ALLOWED_EXTENSIONS
    )


def bad_request(_):
    return render_template("400.html", search_form=SearchForm), 400


def page_not_found(_):
    return render_template("404.html", search_form=SearchForm), 404


@bp.context_processor
def search_form():
    def _search_form():
        return SearchForm()

    return {"search_form": _search_form}


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/search", methods=["POST"])
def search():
    query = request.form.get("query")
    products = Product.query.filter(Product.name.contains(query))
    categories = Category.query.filter(Category.name.contains(query))
    return render_template("search.html", products=products, categories=categories)


@bp.route("/products")
@bp.route("/products/<int:page>")
def products(page=1):
    # products = Product.query.all()
    products = Product.query.paginate(page, 12)
    return render_template("products.html", products=products)


@bp.route("/categories")
def categories():
    categories = Category.query.all()
    return render_template("categories.html", categories=categories)


@bp.route("/product/<id>")
def product(id):
    product = Product.query.get_or_404(id)
    return render_template("product.html", product=product)


@bp.route("/category/<id>")
def category(id):
    category = Category.query.get_or_404(id)
    return render_template("category.html", category=category)


@bp.route("/create-product", methods=["GET", "POST"])
def create_product():
    form = ProductForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = Category.query.get_or_404(form.category.data)
        image = form.image.data

        if image:
            if allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            else:
                flash("Invalid image", "negative")
                return render_template("create-product.html", form=form), 400
        else:
            filename = None

        product = Product(name, price, category, filename)
        db.session.add(product)
        db.session.commit()

        flash(f"Product {name} created!", "positive")
        return redirect(url_for("main.product", id=product.id))

    if form.errors:
        flash(form.errors, "negative")

    return render_template("create-product.html", form=form)


@bp.route(
    "/create-category",
    methods=[
        "GET",
        "POST",
    ],
)
def create_category():
    form = CategoryForm()

    if form.validate_on_submit():
        name = form.name.data
        category = Category(name)
        db.session.add(category)
        db.session.commit()
        flash(f"Category {name} created!", "positive")
        return redirect(url_for("main.category", id=category.id))

    if form.errors:
        flash(form.errors, "negative")

    return render_template("create-category.html", form=form)
