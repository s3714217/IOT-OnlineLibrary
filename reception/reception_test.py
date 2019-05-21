import reception
import unittest
import sqlite3
from db_context import DbContext
from user import User
import reception

class testReception(unittest.TestCase):
    DBCONTEXT = DbContext("reception_test.db")

    def setUp(self):
        if self.get_user("user1") is None:
          self.DBCONTEXT.create_table(self.DBCONTEXT.sql_create_users_table)
          self.DBCONTEXT.insert_into_table(User.REGISTER_USER_SQL, ("user1", "11111111","User1", "Test1", "user1@gmail.com"))
          self.DBCONTEXT.insert_into_table(User.REGISTER_USER_SQL, ("user2", "22222222","User2", "Test2", "user2@gmail.com"))
          self.DBCONTEXT.insert_into_table(User.REGISTER_USER_SQL, ("user3", "33333333","User3", "Test3", "user3@gmail.com"))  
         
    
    def get_user(self, username):
        return self.DBCONTEXT.query_from_table(User.GET_USER_SQL, (username,))


    def test_user_exist(self):
        self.assertTrue(self.get_user("user1") is not None)
        self.assertTrue(self.get_user("user2") is not None)
        self.assertTrue(self.get_user("user3") is not None)

    def test_login(self):
       self.assertTrue(User.login("user1", reception.ADDRESS, "11111111"))
       self.assertTrue(User.login("user2", reception.ADDRESS, "22222222"))
       self.assertFalse(User.login("user2", reception.ADDRESS, "11111111"))
       self.assertFalse(User.login("user1", reception.ADDRESS, "22222222"))
      

    def test_register_user(self):
        
        if self.get_user("user4") is None:
            User.register("user4", "44444444","User4", "Test4", "user4@gmail.com")
            User.register("user5", "55555555","User5", "Test5", "user5@gmail.com")

        self.assertTrue(self.get_user("user4") is not None)
        self.assertTrue(self.get_user("user5") is not None)
       
      

       
if __name__ == "__main__":
    unittest.main()