import json

from flask import abort, request
from flask_restful import Resource, reqparse
from flask_httpauth import HTTPBasicAuth

from app import db
from .models import Category, Product
from .auth.models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return True
    return False


parser = reqparse.RequestParser()
parser.add_argument("name", type=str)
parser.add_argument("price", type=float)
parser.add_argument("category", type=dict)


class ProductApi(Resource):
    decorators = [auth.login_required]

    def get(self, id=None):
        if id:
            products = [Product.query.get_or_404(id)]
        else:
            try:
                page = int(request.args.get("page", 1))
                limit = int(request.args.get("limit", 20))
            except ValueError:
                abort(400)
            products = Product.query.paginate(page, limit).items
        res = {}
        for product in products:
            res[product.id] = {
                "name": product.name,
                "price": product.price,
                "category": product.category.name,
            }
        return json.dumps(res)

    def post(self):
        args = parser.parse_args()
        name = args["name"]
        price = args["price"]
        category_name = args["category"]["name"]

        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(category_name)
        product = Product(name, price, category, image_path=None)
        db.session.add(product)
        db.session.commit()

        res = {}
        res[product.id] = {
            "name": product.name,
            "price": product.price,
            "category": product.category.name,
        }
        return json.dumps(res)

    def put(self, id):
        args = parser.parse_args()
        name = args["name"]
        price = args["price"]
        category_name = args["category"]["name"]

        category = Category.query.filter_by(name=category_name).first()
        Product.query.filter_by(id=id).update(
            {"name": name, "price": price, "category_id": category.id}
        )
        db.session.commit()

        product = Product.query.get_or_404(id)
        res = {}
        res[product.id] = {
            "name": product.name,
            "price": product.price,
            "category": product.category.name,
        }
        return json.dumps(res)

    def delete(self, id):
        product = Product.query.get_or_404(id)
        db.session.delete(product)
        db.session.commit()
        return json.dumps({"response": "Success"})
