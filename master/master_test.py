import unittest
import master
from master import Book
from master import UserBorrowedBooks
from master import LibraryUser
from master import BookStatuses
import datetime

class testMaster(unittest.TestCase):
        
        def setUp(self):
            user = {"_username": "thiennguyen", "_first_name": "Thien", "_last_name": "Nguyen", "_email": "thien.nguyen@gmail.com"}
            master.create_user_if_not_exists(user)
            book = {"_id": 1, "_title": "Book1", "_isbn": "11111111", "_author": "unknown", "_published_date" : "1/1/1999"}
            borrowing_book = Book(id=book["_id"], title=book["_title"], isbn=book["_isbn"], author=book["_author"], published_date=book["_published_date"])
            master.session.add(borrowing_book)
            master.session.commit()
            #master.main()

            
        def test_current_userer(self):
            user = master.session.query(LibraryUser).filter(LibraryUser.username == "thiennguyen").first()
            self.assertTrue(user["_username"] is not None)
            self.assertTrue(user["_first_name"] is not None)
            self.assertTrue(user["_last_name"] is not None)
            self.assertTrue(user["_email"] is not None)

        def test_borrow_book(self):
           borrowing_user =  master.session.query(LibraryUser).filter(LibraryUser.username == "thiennguyen").first()
           borrowing_book = master.session.query(Book).filter(Book.id == 1).first()
           event = master.add_borrowed_event(borrowing_book, borrowing_user)
           borrow = UserBorrowedBooks(library_user_id=borrowing_user.id, book_id=int(borrowing_book.id),status=BookStatuses.borrowed, borrowed_date=datetime.today().date(),calendar_event_id=event.get("id"))
           master.session.add(borrow)
           master.session.commit()
           self.assertTrue(master.session.query(UserBorrowedBooks).filter(UserBorrowedBooks.book_id == 1).first is not None)
        
        def test_return_book(self):
            returning_book = master.session.query(Book).filter(Book.id == 1).first()
            returning_book.status = BookStatuses.returned
            master.session.commit()
            test_book =  master.session.query(Book).filter(Book.id == 1).first()
            self.assertTrue(test_book.status == BookStatuses.returned)