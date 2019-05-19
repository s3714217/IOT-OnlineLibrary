import operator
import re
from passlib.hash import sha256_crypt
from db_context import DbContext
from sqlite3 import Error
import socket
import json
import sys
sys.path.append("..")
import socket_utils

class User:
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    NAME_REGEX = re.compile(r"[a-zA-Z0-9]+")
    PASSWORD_REGEX = re.compile(r"[A-Za-z0-9@#$%^&+=]{8,}")
    REGISTER_USER_SQL = 'INSERT INTO Users (username, password, first_name, last_name, email) VALUES(?,?,?,?,?);'
    GET_USER_SQL = 'SELECT * FROM Users WHERE username = ?'
    DBCONTEXT = DbContext("reception.db")

    def __init__(self) -> None:
        self._username = ''
        self._password = ''
        self._first_name = ''
        self._last_name = ''
        self._email = ''

    username = property(operator.attrgetter('_username'))
    email = property(operator.attrgetter('_email'))
    last_name = property(operator.attrgetter('_last_name'))
    first_name = property(operator.attrgetter('_first_name'))
    password = property(operator.attrgetter('_password'))

    @username.setter
    def username(self, username: str):
        if not username:
            raise Exception("Username cannot be empty")
        if not self.NAME_REGEX.fullmatch(username):
            raise Exception("Username can only contain alphanumeric characters")
        self._username = username

    @password.setter
    def password(self, password: str):
        if not password:
            raise Exception("Password cannot be empty")
        if not self.PASSWORD_REGEX.fullmatch(password):
            raise Exception("Password has to be at-least 8 characters and can contain alphabets, "
                            "numbers and special characters")
        self._password = sha256_crypt.hash(password)

    @first_name.setter
    def first_name(self, first_name: str):
        if not first_name:
            raise Exception("First name cannot be empty")
        if not self.NAME_REGEX.fullmatch(first_name):
            raise Exception("First name can only contain alphanumeric characters")
        self._first_name = first_name

    @last_name.setter
    def last_name(self, last_name: str):
        if not last_name:
            raise Exception("Last name cannot be empty")
        if not self.NAME_REGEX.fullmatch(last_name):
            raise Exception("Last name can only contain alphanumeric characters")
        self._last_name = last_name

    @email.setter
    def email(self, email: str):
        if not email:
            raise Exception("Email cannot be empty")
        if not self.EMAIL_REGEX.fullmatch(email):
            raise Exception("Invalid email address")
        self._email = email

    def register(self, username: str, password: str, first_name: str, last_name: str, email: str):
        self.last_name = last_name
        self.first_name = first_name
        self.password = password
        self.email = email
        self.username = username
        try:
            self.DBCONTEXT.insert_into_table(self.REGISTER_USER_SQL,
                                     (self.username, self.password, self.first_name, self.last_name, self.email))
        except Error:
            raise Exception("The username exists and cannot be created")

    def login(self, username: str, address, face_login: bool = False, password: str = "") -> bool:
        self.username = username
        try:
            users = self.DBCONTEXT.query_from_table(self.GET_USER_SQL, (self.username,))
            if len(users) == 0:
                return False
            if not sha256_crypt.verify(password, users[0][1]) and not face_login:
                return False
            self.first_name = users[0][2]
            self.email = users[0][4]
            self.last_name = users[0][3]
            self.connect_to_master_pi(address)
            return True
        except Error as e:
            print(str(e))
            return False

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def connect_to_master_pi(self, address):
        user = self.to_json()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print("Connecting to {}...".format(address))
            s.connect(address)
            print("Connected.")

            print("Logging in as {}".format(user))
            socket_utils.send_json(s, user)

            print("Waiting for Master Pi...")
            while True:
                object_response = socket_utils.recv_json(s)
                if "logout" in object_response:
                    print("Master Pi logged out.")
                    print()
                    break


