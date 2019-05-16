from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import dateutil.parser as date_parser

api = Blueprint("api", __name__)

db = SQLAlchemy()
ma = Marshmallow()


# Declaring the model.
class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    isbn = db.Column(db.Text, nullable=False, unique=True)
    author = db.Column(db.Text, nullable=False)
    published_date = db.Column(db.Date, nullable=False)

    def __init__(self, title, isbn, author, published_date, book_id=None):
        self.author = author
        self.title = title
        self.isbn = isbn
        self.id = book_id
        self.published_date = published_date


class BookSchema(ma.ModelSchema):

    class Meta:
        model = Book


book_schema = BookSchema()
book_schema_list = BookSchema(many=True)


# Endpoint to show all books.
@api.route("/books", methods=["GET"])
def get_books():
    print('too')
    books = Book.query.all()
    result = book_schema_list.dump(books)
    return jsonify(result.data)


# Endpoint to get book by id.
@api.route("/books/<identifier>", methods=["GET"])
def get_book(identifier: str):
    book = Book.query.get(identifier)

    return book_schema.jsonify(book)


# Endpoint to create a new book.
@api.route("/books", methods=["POST"])
def add_book():
    print(request.json)
    title = request.json["title"]
    isbn = request.json["isbn"]
    author = request.json["author"]
    published_date = date_parser.parse(request.json["publishedDate"])

    new_book = Book(title=title, isbn=isbn, author=author, published_date=published_date)

    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book)


# Endpoint to delete book.
@api.route("/books/<identifier>", methods=["DELETE"])
def delete_book(identifier: str):
    book = Book.query.get(identifier)

    db.session.delete(book)
    db.session.commit()

    return book_schema.jsonify(book)
