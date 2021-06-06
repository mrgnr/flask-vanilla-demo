from app import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float)
    image_path = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship(
        "Category", backref=db.backref("products", lazy="dynamic")
    )

    def __init__(self, name, price, category, image_path):
        self.name = name
        self.price = price
        self.category = category
        self.image_path = image_path

    def __repr__(self):
        return f"{self.name}"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"{self.name}"
