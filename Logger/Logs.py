import os,sqlite3
from datetime import date
from datetime import datetime
from Config.configDetails import ConnectionDetails
import logging
from logging.handlers import RotatingFileHandler
from random import choice
from string import ascii_uppercase

class Logs():
    def __init__(self):
        print("Initializing Logs")
        super(Logs,self).__init__()
        print(logging)
        self.logger = logging
        print(self.logger)
        self.id = ""
        self.boolean = False

    def createDirIfNotExists(self):
        path = os.path.join(os.path.abspath(os.getcwd()),"logs")
        if(not(os.path.exists(path))):
            os.makedirs(os.path.join(path))
            print("dir created")
            
    
    def setConfig(self):
        self.createDirIfNotExists()
        instant = datetime.now()
        idx=""
        idx = instant.strftime("%y%b%d")
        self.fileName = os.path.join(os.path.abspath(os.getcwd()),"logs\\"+idx+".log")
        self.id = idx+".log"
        self.logger.basicConfig(handlers=[RotatingFileHandler(self.fileName, maxBytes=1000000, backupCount=10)],format = "%(asctime)s : %(process)d : %(levelname)s : %(message)s" , datefmt='%d-%b-%y %H:%M:%S',level=logging.DEBUG)
    
    def addLog(self,module,msg):
        logVal = "self.logger."+module+"(msg" + (",exc_info=True)" if module=="error" else ")")
        eval(logVal)
            
    def getId(self):
        return self.id if (self.boolean) else ""

        
