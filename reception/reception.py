# !/usr/bin/env python3
import json
from user import User
from facial_recognition import FacialRecognition
import _thread


with open("config.json", "r") as file:
    data = json.load(file)

HOST = data["master_pi_ip"]  # The server's hostname or IP address.
PORT = 63000  # The port used by the server.
ADDRESS = (HOST, PORT)
user = User()
facial_login = FacialRecognition(data["encodings"], data["classifier"], data["dataset"],
                                 data["detection_method"], data["resolution"], data["output"], data["display"])


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
            facial_recognition = input("Do you want to use face login. press [y]:yes or [n]:no:")
            if facial_recognition == "y" or facial_recognition == "yes":
                facial_login.capture(username)
                _thread.start_new_thread(facial_login.encode, ())
            try:
                user.register(username, password, first_name, last_name, email)
            except Exception as e:
                print('Invalid data: ' + str(e))
            print('success')
        elif text == "2":
            username = input("Username:")
            password = input("Password:")
            try:
                login = user.login(username, ADDRESS, password=password)
                if not login:
                    print('Invalid login credentials')
            except Exception as e:
                print('Invalid data: ' + str(e))
            print('success')
        elif text == "3":
            print("Please stand in front of the camera..")
            username = facial_login.recognise()
            if username != "":
                login = user.login(username, ADDRESS, face_login=True)
                if not login:
                    print('Invalid login credentials')
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
