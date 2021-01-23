import os,sqlite3
from datetime import date
from datetime import datetime
from configDetails import ConnectionDetails

class Scheduler():
    def __init__(self):
        print("Initializing Scheduler")
        super(Scheduler,self).__init__()
        self.monthNames={
            "01" : "Jan","02" : "Feb","03" : "Mar",
            "04" : "Apr","05" : "May","06" : "Jun",
            "07" : "Jul","08" : "Aug","09" : "Sept",
            "10" : "Oct","11" : "Nov","12" : "Dec",
        }
        self.log = ConnectionDetails.self

    def progress(self,status, remaining, total):
        print(f'Copied {total-remaining} of {total} pages...')
        self.log.addLog("info","[Scheduler progress] copied "+str(total-remaining)+" of "+str(total)+" pages..")
    
    def run(self):
        self.log = ConnectionDetails.self
        instant = datetime.now()
        yr = instant.strftime("%Y")
        month = self.monthNames[str(instant.strftime("%m"))]
        dt = instant.strftime("%d")
        now = instant.strftime("%H_%M_%S")
        fileName = now+".sqlite"
        self.log.addLog("debug","[Scheduler run] fileName "+fileName)
        try:
            con = sqlite3.connect(ConnectionDetails.sqlite_file)
            print(con)
            path = os.path.join(os.getcwd(),"backup",yr,month,dt)
            self.log.addLog("debug","[Scheduler run] path "+ str(path))
            if(os.path.exists(path)):
                self.log.addLog("debug","[Scheduler run] path already exists ")
                pass
            else:
                os.makedirs(os.path.join(os.getcwd(),path))
                self.log.addLog("debug","[Scheduler run] path created ")
            with open(os.path.join(path,fileName),"x"):
                self.log.addLog("debug","[Scheduler run] file created ")
                pass
            self.log.addLog("debug","[Scheduler run] directory created.. connecting to backup sqlite file ")
            backup = sqlite3.connect(os.path.join(os.getcwd(),path,fileName))
            with backup:
                self.log.addLog("debug","[Scheduler run] starting backup ")
                con.backup(backup, pages=1, progress=self.progress)
            backup.close()
            con.close()         
        except Exception as e:
            self.log.addLog("error","[Scheduler run]"+e)

if __name__ == '__main__':
    Scheduler().run()
            
        
