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

    def progress(self,status, remaining, total):
        print(f'Copied {total-remaining} of {total} pages...')
    
    def run(self):
        instant = datetime.now()
        yr = instant.strftime("%Y")
        month = self.monthNames[str(instant.strftime("%m"))]
        dt = instant.strftime("%d")
        now = instant.strftime("%H_%M_%S")
        fileName = now+".sqlite"
        print(fileName)
        try:
            print("connecting to source "+str(ConnectionDetails.sqlite_file))
            con = sqlite3.connect(ConnectionDetails.sqlite_file)
            print(con)
            path = os.path.join(os.getcwd(),"backup",yr,month,dt)
            print(path)
            if(os.path.exists(path)):
                print("passing")
                pass
            else:
                os.makedirs(os.path.join(os.getcwd(),path))
            with open(os.path.join(os.getcwd(),path,fileName),"x"):
                print("file created")
                pass
            print("directory created.. connecting to backup sqlite file")
            backup = sqlite3.connect(os.path.join(os.getcwd(),path,fileName))
            with backup:
                con.backup(backup, pages=1, progress=self.progress)
            backup.close()
            con.close()         
        except:
            print("error occurred")

if __name__ == '__main__':
    Scheduler().run()
            
        
