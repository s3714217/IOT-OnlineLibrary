Master
=========================

class BookStatuses(enum.Enum):

    Initializing book status

class UserBorrowedBooks(Base):

    Borrowing book function

class Book(Base):

    Book object variables

        def list(self):

            Return book variables

class LibraryUser(Base):

    LibraryUser objects variables
    
main():

    Connecting to reception pi

create_user_if_not_exists(user):

    Creating a new user if current user doesn't exist

menu(user):

    User interface including all functions

add_borrowed_event(book, user):

    booking borrowing event