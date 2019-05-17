#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html
import enum
import json
import socket
import sys
from datetime import timedelta, datetime

from sqlalchemy import Column, Integer, String, Date, Enum, ForeignKey, create_engine, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from tabulate import tabulate

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


sys.path.append("..")
import socket_utils

HOST = ""     # Empty string means to listen on all IP's on the machine, also works with IPv6.
              # Note "0.0.0.0" also works but only with IPv4.
PORT = 63000  # Port to listen on (non-privileged ports are > 1023).
ADDRESS = (HOST, PORT)

DB_HOST = "35.189.7.222"
DB_USER = "root"
DB_PASSWORD = "admin@1234"
DATABASE = "Library"
SCOPES = 'https://www.googleapis.com/auth/calendar'
store = file.Storage("token.json")
credentials = store.get()
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets("credentials.json", SCOPES)
    credentials = tools.run_flow(flow, store)
service = build("calendar", "v3", http=credentials.authorize(Http()))
engine = create_engine("mysql://{}:{}@{}/{}".format(DB_USER, DB_PASSWORD, DB_HOST, DATABASE))
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class BookStatuses(enum.Enum):
    borrowed = 1
    returned = 2


class UserBorrowedBooks(Base):
    __tablename__ = "user_borrowed_books"
    borrow_id = Column(Integer, autoincrement=True, primary_key=True)
    library_user_id = Column(Integer, ForeignKey('library_users.id'))
    book_id = Column(Integer, ForeignKey('books.id'))
    status = Column(Enum(BookStatuses), nullable=False)
    borrowed_date = Column(Date, nullable=False)
    returned_date = Column(Date, nullable=True)
    calendar_event_id = Column(String(255), nullable=False)
    borrowed_book = relationship("Book", back_populates="borrowed_users")
    borrowing_user = relationship("LibraryUser", back_populates="books_borrowed")


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    isbn = Column(String(255), nullable=False, unique=True)
    author = Column(String(255), nullable=False)
    published_date = Column(Date, nullable=False)
    borrowed_users = relationship("UserBorrowedBooks", back_populates="borrowed_book")

    def list(self):
        return [self.id, self.title, self.isbn, self.author, str(self.published_date)]


class LibraryUser(Base):
    __tablename__ = "library_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    books_borrowed = relationship("UserBorrowedBooks", back_populates="borrowing_user")


def main():
    Base.metadata.create_all(engine)
    # user = {"_username": "jamirineni", "_first_name": "jaya", "_last_name": "amirineni", "_email": "jayasai.amerineni@gmail.com"}
    while True:
        # menu(user)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(ADDRESS)
            s.listen()

            print("Listening on {}...".format(ADDRESS))
            while True:
                print("Waiting for Reception Pi...")
                conn, addr = s.accept()
                with conn:
                    print("Connected to {}".format(addr))
                    print()

                    user = socket_utils.recv_json(conn)
                    menu(user)

                    socket_utils.send_json(conn, json.dumps({"logout": True}))


def create_user_if_not_exists(user):
    library_user = session.query(LibraryUser).filter(LibraryUser.username == user["_username"]).first()
    if not library_user:
        user = LibraryUser(username=user["_username"], email=user["_email"],
                           first_name=user["_first_name"], last_name=user["_last_name"])
        session.add(user)
        session.commit()
        return user
    return library_user


def menu(user):
    while True:
        print("Welcome {}".format(user["_username"]))
        print("1. Display user details")
        print("2. Search for book catalogues based on ISBN/Author name/Book name")
        print("3. Borrow book/books")
        print("4. Return book/books")
        print("0. Logout")
        print()

        text = input("Select an option: ")
        print()

        if text == "1":
            print("Username  : {}".format(user["_username"]))
            print("First Name: {}".format(user["_first_name"]))
            print("Last Name : {}".format(user["_last_name"]))
            print("Email : {}".format(user["_email"]))
            print()
        elif text == "2":
            book_filter = input("Enter ISBN/Author name/Book name: ")
            book_filter = '%'+book_filter+'%'
            books = session.query(Book).filter(or_(Book.title.like(book_filter), Book.author.like(book_filter),
                                                   Book.isbn.like(book_filter)))
            formatted_books = [book.list() for book in books]
            print(tabulate(formatted_books, headers=["BookID", "Title", "ISBN", "Author", "Published Date"]))
            print("Note the BookIDs to borrow them!")
            print()
        elif text == "3":
            borrowing_user = create_user_if_not_exists(user)
            while True:
                book_id = input("Enter the BookID to borrow or enter 0 to go back:")
                if book_id == "0":
                    break
                borrowed_book = session.query(UserBorrowedBooks).filter(
                    and_(UserBorrowedBooks.book_id == book_id, UserBorrowedBooks.status == BookStatuses.borrowed))\
                    .first()
                if borrowed_book:
                    print("The selected book has been borrowed and is due to be returned on "
                          + str(borrowed_book.borrowed_date + timedelta(days=7)))
                else:
                    borrowing_book = session.query(Book).filter(Book.id == book_id).one()
                    event = add_borrowed_event(borrowing_book, borrowing_user)
                    borrow = UserBorrowedBooks(library_user_id=borrowing_user.id, book_id=int(book_id),
                                               status=BookStatuses.borrowed, borrowed_date=datetime.today().date(),
                                               calendar_event_id=event.get("id"))
                    session.add(borrow)
                    session.commit()

                    print("Book successfully borrowed and is due in one week from today")
                print()
        elif text == "4":
            returning_user = create_user_if_not_exists(user)
            while True:
                book_id = input("Enter the BookID to return or enter 0 to go back:")
                if book_id == "0":
                    break
                returning_book = session.query(UserBorrowedBooks).filter(
                    and_(UserBorrowedBooks.book_id == book_id,
                         UserBorrowedBooks.status == BookStatuses.borrowed,
                         UserBorrowedBooks.library_user_id == returning_user.id)) \
                    .first()
                if not returning_book:
                    print("The selected book is either not borrowed or is borrowed by someone else")
                else:
                    returning_book.status = BookStatuses.returned
                    returning_book.returned_date = datetime.today().date()
                    session.commit()
                    print(returning_book.calendar_event_id)
                    service.events().delete(calendarId='primary', eventId=returning_book.calendar_event_id).execute()
                    print("Book successfully returned")
                print()
        elif text == "0":
            print("Goodbye.")
            print()
            break
        else:
            print("Invalid input, try again.")
            print()


def add_borrowed_event(book, user):
    week_from_now = datetime.today().date() + timedelta(7)
    time_start = "{}T00:00:00+10:00".format(week_from_now)
    time_end = "{}T12:00:00+10:00".format(week_from_now)
    event = {
        "summary": "Library book return reminder event",
        "location": "Library",
        "description": "Return {} by {} to the library".format(book.title, book.author),
        "start": {
            "dateTime": time_start,
            "timeZone": "Australia/Melbourne",
        },
        "end": {
            "dateTime": time_end,
            "timeZone": "Australia/Melbourne",
        },
        "attendees": [
            {
                "email": user.email,
                "displayName": user.first_name + " " + user.last_name
            }
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24*60},
                {"method": "popup", "minutes": 24*60}
            ],
        }
    }
    event = service.events().insert(calendarId='primary', body=event, sendNotifications=True).execute()
    print('Event added to your calendar: %s' % event.get('htmlLink'))
    print(event)
    return event


# Execute program.
if __name__ == "__main__":
    main()
