# !/usr/bin/env python3
import json
from user import User

with open("config.json", "r") as file:
    data = json.load(file)

HOST = data["master_pi_ip"]  # The server's hostname or IP address.
PORT = 63000  # The port used by the server.
ADDRESS = (HOST, PORT)
user = User()


def main():
    while True:
        print("1. Register new User")
        print("2. Login using password")
        print("3. Login using facial recognition")
        print("0. Quit")
        print()

        text = input("Select an option: ")
        print()

        if text == "1":
            username = input("Username:")
            password = input("Password:")
            first_name = input("First name:")
            last_name = input("Last name:")
            email = input("Email:")
            try:
                user.register(username, password, first_name, last_name, email)
            except Exception as e:
                print('Invalid data: ' + str(e))
            print('success')
        elif text == "2":
            username = input("Username:")
            password = input("Password:")
            try:
                login = user.login(username, password, ADDRESS)
                if not login:
                    print('Invalid login credentials')
            except Exception as e:
                print('Invalid data: ' + str(e))
            print('success')
        elif text == "3":
            print("Please stand in front of the camera..")
            print()
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
