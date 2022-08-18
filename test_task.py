# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 13:07:51 2022

@author: tanvir
"""

import unittest
import sys
from io import StringIO
import second_task
import pathlib
import os
import sqlite3

if os.path.exists("mock_sqlite_database.db"):
    os.remove("mock_sqlite_database.db")


class MockDB():
    
    def __init__(self):
        self.db_name = "mock_sqlite_database.db"
        self.data = [("2022-08-02", "12:00:00"), ("2022-08-01", "08:00:00"), ("2022-08-01", "12:00:00"),
                     ("2022-08-02", "18:00:00"), ("2022-08-01", "18:00:00"), ("2022-08-02", "08:00:00")]
        self.con = sqlite3.connect(self.db_name)
        self.cursor = self.con.cursor()
        
    def CreateDatabase(self, dates, time, db_name):
        con = sqlite3.connect(db_name)
        cursor = con.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS datetime (id INTEGER PRIMARY KEY, 
                       dates, time, unique(dates, time))''')         
        cursor.execute('''INSERT OR IGNORE INTO datetime(dates, time) VALUES (?, ?)''',
                       (dates, time))    
        con.commit()
        
    def FetchUpcomingDate(self, table_name):
        
        query = 'SELECT * FROM {} ORDER BY dates, time ASC'.format(table_name)    
        #cursor.execute('''SELECT * FROM (table_name) ORDER BY dates, time ASC''')
        self.cursor.execute(query)
        latest_date = self.cursor.fetchall()[0]
        rowid = latest_date[0]
        latest_date_time = latest_date[1]+' '+latest_date[2]
        #latest_date_time = datetime.strptime(latest_date_time, "%Y-%m-%d %H:%M:%S")
        return latest_date_time, rowid
    
    def delete_data(self, rowid):
        self.cursor.execute('''DELETE FROM datetime WHERE id = (?)''', (rowid,))
        
    def search_data(self, rowid):
        self.cursor.execute('''SELECT * FROM datetime WHERE id = (?)''', (rowid,))
        

class TestDateTime(unittest.TestCase):
    
    def setUp(self):
        #self.db_name = "sqlite_database.db"
        self.qr_folder = "qr_codes"
        self.cwd = pathlib.Path().resolve()
        self.path = os.path.join(self.cwd, self.qr_folder)
        self.files = os.listdir(self.path)
        self.out, sys.stdout = sys.stdout, StringIO()
        self.db = MockDB()
        for i in self.db.data:
            self.db.CreateDatabase(i[0], i[1] , self.db.db_name)            
        
    def test_readqrcode(self):                
        self.assertEqual(second_task.ReadQR(self.path, self.files[0]), '2022-08-01 08:00')
        self.assertEqual(second_task.ReadQR(self.path, self.files[5]), '2022-08-02 18:00')
        
    def test_checkdataWithPastDate(self):
        second_task.CheckData("2022-07-27 15:55")
        self.assertEqual(sys.stdout.getvalue().strip(), "please enter a future date & time.")
        
    def test_checkdataWithWrongFormat(self):
        second_task.CheckData("2022-07-27 15.55")
        self.assertEqual(sys.stdout.getvalue().strip(), "please enter the datetime(yyyy-mm-dd hh:mm) in correct format.")
        
    def test_mockdb(self):
        upcoming_data = self.db.FetchUpcomingDate("datetime")
        self.assertEqual(upcoming_data, ("2022-08-01 08:00:00", 2))
        self.db.delete_data(2)
        self.db.con.commit()
        res = self.db.search_data(2)
        self.assertEqual(res, None)
            
    def test_userNotification(self):
        _input = "2022-07-29 11:08:00" # always enter a future date time to test
        second_task.UserNotification(_input) 
                


if __name__ == '__main__':
    unittest.main()
