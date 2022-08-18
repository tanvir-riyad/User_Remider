# -*- coding: utf-8 -*-
"""
Created on Sun Jul 24 15:14:07 2022

@author: tanvir
"""

import cv2
import os
import pathlib
from datetime import datetime
import sqlite3
import time
from plyer import notification
from gtts import gTTS
from queue import Queue
from playsound import playsound

#%%Check data
def CheckData(Data):
    try:
        dt = datetime.strptime(Data, "%Y-%m-%d %H:%M")
        DateTimeNow = datetime.strptime(datetime.now().strftime("%d.%m.%Y %H:%M"),
                                        "%d.%m.%Y %H:%M")
        assert dt > DateTimeNow
        
    except ValueError:
        print("please enter the datetime(yyyy-mm-dd hh:mm) in correct format.")              
    
    except AssertionError:
        print("please enter a future date & time.") 
                
    else:
        return str(dt.date()), str(dt.time())


#%% Read QR 

def ReadQR(path, file):      
    img = cv2.imread(os.path.join(path, file))
    detect = cv2.QRCodeDetector()
    Data, points, st_code = detect.detectAndDecode(img)
    return Data
                           
#%% Create database

def CreateDatabase(dates, time, db_name):
    con = sqlite3.connect(db_name)
    cursor = con.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS datetime (id INTEGER PRIMARY KEY, 
                   dates, time, unique(dates, time))''')         
    cursor.execute('''INSERT OR IGNORE INTO datetime(dates, time) VALUES (?, ?)''',
                   (dates, time))    
    con.commit()

    
    
#%%Fetch data   
def FetchUpcomingDate(table_name):
    
    query = 'SELECT * FROM {} ORDER BY dates, time ASC'.format(table_name)    
    #cursor.execute('''SELECT * FROM (table_name) ORDER BY dates, time ASC''')
    cursor.execute(query)
    latest_date = cursor.fetchall()[0]
    rowid = latest_date[0]
    latest_date_time = latest_date[1]+' '+latest_date[2]
    latest_date_time = datetime.strptime(latest_date_time, "%Y-%m-%d %H:%M:%S")
    return latest_date_time, rowid

    
#%%Queue
def CreateQueueAndNotify(que_size):
    que = Queue(maxsize = que_size)
    carry_on = True
    while carry_on:
        result, rowid = FetchUpcomingDate("datetime")
        que.put(result)
        cursor.execute('''DELETE FROM datetime WHERE id = (?)''', (rowid,))
        con.commit()
        upcoming_dt = que.queue[0]
        UserNotification(str(upcoming_dt))
        que.get()
        cursor.execute('''SELECT * FROM datetime''')
        res = cursor.fetchall()
        if len(res) == 0:
            carry_on = False
    
#%%User Notification

def UserNotification(_input):
        #text = "time to take the medicine"
        #language = 'en'
        dt = datetime.strptime(_input, "%Y-%m-%d %H:%M:%S")
        dt_now = datetime.strptime(datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
                              "%d.%m.%Y %H:%M:%S")
        diff = (dt - dt_now).total_seconds()
        time.sleep(diff)
        try:
            notification.notify(title = 'medication reminder', 
                                message = 'time to take medicine',
             app_icon ='pill_icon-icons.com_53621.ico', timeout = 10)
            
        except FileNotFoundError:
            print("app icon file not found")
        else:
            try:                
                playsound('reminder.mp3')                
            except:
                print("Audio file not found or playsound module not working")


            
if __name__ == "__main__":
    
    db_name = "sqlite_database.db"
    language = 'en'
    text = "time to take the medicine"
    obj = gTTS(text = text, lang = language, slow = False)
    obj.save("reminder.mp3")
    if os.path.exists(db_name):
        os.remove(db_name)
    qr_folder = "qr_codes"
    cwd = pathlib.Path().resolve()
    path = os.path.join(cwd, qr_folder )    
    
    try:    
        assert os.path.exists(path) == True 
        assert len(os.listdir(path)) != 0 
        
    except AssertionError:
        print("No such file or directory or the directory is empty")
          
    else:
        try:
            for file in os.listdir(path):
                Data = ReadQR(path, file)
                date_str, time_str = CheckData(Data)
                db = CreateDatabase(date_str, time_str, db_name)
            if os.path.isfile(db_name) == True :
                con = sqlite3.connect(db_name)
                cursor = con.cursor()
                cursor.execute('''SELECT * FROM datetime''')
                CreateQueueAndNotify(1)
                con.close()                
            else:
                print("No such database file or directory exists")
        except:
            print('Mentioned exceptions need to be fixed first.')
        
        
