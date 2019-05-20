User
=========================

class user:

    __init__(self) -> None:

        Initializing user

    username(self, username: str):

        Validating user_name

    password(self, password: str):
        
         Validating password


    first_name(self, first_name: str):

         Validating first_name

    last_name(self, last_name: str):

         Validating last_name

    email(self, email: str):

         Validating email

    register(self, username: str, password: str, first_name: str, last_name: str, email: str):

         Setting all validated variables
    
    login(self, username: str, address, face_login: bool = False, password: str = "") -> bool:

         User login to master
     
    connect_to_master_pi(self, address):

         Establishing connection to master