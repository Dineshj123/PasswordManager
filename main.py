import sys,os,sqlite3
from PyQt5.QtWidgets import (QApplication)
from Config.configDetails import ConnectionDetails
from DataBase.Database import InitializeDatabase
from Logger.Logs import Logs
from Scripts.backupDB_scheduler import Scheduler
from Scripts.app import App
from pathlib import Path
import threading,time

    
def backUpRun():
    log = None
    conn = sqlite3.connect(ConnectionDetails.sqlite_file)
    try:
        while(True):
            if(ConnectionDetails.backup):
                print("inside backup")
                log = ConnectionDetails.self
                ConnectionDetails.backup = False
                log.addLog("debug","[atexit backUpRun] running backup")
                Scheduler().run()
                log.addLog("debug","[atexit backUpRun] backup completed")
                c = conn.cursor()
                sql = " INSERT INTO backup (creation_date) VALUES(datetime('now')) "
                log.addLog("debug","[atexit backUpRun] sql "+sql)
                c.execute(sql)
                conn.commit()
                log.addLog("debug","[atexit backUpRun] inserted backup")
                conn.close()
            time.sleep(2)
    except sqlite3.Error as e:
        log.addLog("error","[atexit backUpRun] "+e)
        conn.close()

def initializeDB():
    obj = Logs()
    obj.setConfig()
    ConnectionDetails.self = obj
    self = InitializeDatabase()
    InitializeDatabase.create_user_database(self)
    obj.addLog("debug","creating domain credentials")
    InitializeDatabase.create_domain_credentails_database(self)
    obj.addLog("debug","creating backup db")
    InitializeDatabase.create_backup_database(self)

def setUpDB():
    mode = "x"
    path = os.path.join(os.path.abspath(os.getcwd()),ConnectionDetails.connectionPath)
    print(path)
    print("setting up DB")
    if(not(os.path.exists(path))):
        print("creating db path")
        os.makedirs(os.path.join(path))
    if(Path(os.path.join(path,ConnectionDetails.connectionFile)).is_file()):
        mode = "r"
        print("mode changed")
    with open(ConnectionDetails.sqlite_file,mode):
        initializeDB()
        
        
if __name__ == '__main__':
    #setting db path
    d = threading.Thread(name='backupdaemon', target=backUpRun)
    d.setDaemon(True)
    d.start()
    setUpDB()
    app = QApplication(sys.argv)
    ex = App()
