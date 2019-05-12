#!/usr/bin/env python3
# Documentation: https://docs.python.org/3/library/socket.html
import socket, sys, json

sys.path.append("..")
import socket_utils

HOST = ""     # Empty string means to listen on all IP's on the machine, also works with IPv6.
              # Note "0.0.0.0" also works but only with IPv4.
PORT = 63000  # Port to listen on (non-privileged ports are > 1023).
ADDRESS = (HOST, PORT)


def main():
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
        elif text == "3":
            print("borrow book/books")
        elif text == "4":
            print("return book/books")
        elif text == "0":
            print("Goodbye.")
            print()
            break
        else:
            print("Invalid input, try again.")
            print()


# Execute program.
if __name__ == "__main__":
    main()
