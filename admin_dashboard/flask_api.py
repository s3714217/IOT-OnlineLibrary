from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

api = Blueprint("api", __name__)

db = SQLAlchemy()
ma = Marshmallow()


# Declaring the model.
class Book(db.Model):
    __tablename__ = "Book"
    BookID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    BookName = db.Column(db.Text, nullable=False)
    ISBN = db.Column(db.Text, nullable=False, unique=True)
    AuthorName = db.Column(db.Text, nullable=False)

    def __init__(self, book_name, isbn, author_name, book_id=None):
        self.AuthorName = author_name
        self.BookName = book_name
        self.ISBN = isbn
        self.BookID = book_id


class BookSchema(ma.Schema):
    def __init__(self, strict=True, **kwargs):
        super().__init__(strict=strict, **kwargs)

    class Meta:
        fields = ("BookID", "ISBN", "AuthorName", "BookName")


bookSchema = BookSchema(many=True)


# Endpoint to show all people.
@api.route("/books", methods=["GET"])
def get_books():
    print('here')
    books = Book.query.all()
    result = bookSchema.dump(books)
    return jsonify(result.data)


# Endpoint to get person by id.
@api.route("/books/<identifier>", methods=["GET"])
def get_book(identifier: str):
    book = Book.query.get(identifier)

    return bookSchema.jsonify(book)


# Endpoint to create a new book.
@api.route("/books", methods=["POST"])
def add_book():
    book_name = request.json["bookName"]
    isbn = request.json["isbn"]
    author_name = request.json["authorName"]

    new_book = Book(book_name=book_name, isbn=isbn, author_name=author_name)

    db.session.add(new_book)
    db.session.commit()

    return bookSchema.jsonify(new_book)


# Endpoint to delete book.
@api.route("/books/<identifier>", methods=["DELETE"])
def delete_book(identifier: str):
    book = Book.query.get(identifier)

    db.session.delete(book)
    db.session.commit()

    return bookSchema.jsonify(book)
