import os,sqlite3
from datetime import date
from datetime import datetime
from configDetails import ConnectionDetails

class InitializeDatabase():
    def __init__(self):
        super(InitializeDatabase,self).__init__()
        self.log = ConnectionDetails.self
        self.log.addLog("debug","Initializing Database")
    
    def create_user_database(self):
        table_name = 'users'  
        field1 = 'user_id' 
        field1_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        field2 = 'user_name' 
        field2_type = 'VARCHAR(100) NOT NULL'
        field3 = 'user_pass' 
        field3_type = 'VARCHAR(100) NOT NULL'
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3})'\
                    .format(tn=table_name, nf1=field1, ft1=field1_type,nf2=field2, ft2=field2_type,nf3=field3, ft3=field3_type))
            conn.commit()
            self.log.addLog("info","user Database created")
        except sqlite3.Error as e:
            self.log.addLog("error","[InitializeDatabase create_user_database] ====== "+e)

    def create_domain_credentails_database(self):
        table_name = 'domain_credentials'  
        field1 = 'id' 
        field1_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        field2 = 'domain' 
        field2_type = 'VARCHAR(100) NOT NULL'
        field3 = 'user_name' 
        field3_type = 'VARCHAR(100) NOT NULL'
        field4 = 'user_pass' 
        field4_type = 'VARCHAR(100) NOT NULL'
        field5 = 'user_id' 
        field5_type = 'INTEGER NOT NULL'
        field6 = 'creation_date' 
        field6_type = "TEXT"
        field7 = 'version' 
        field7_type = "INTEGER" 
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)            
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3},{nf4} {ft4},{nf5} {ft5},{nf6} {ft6},{nf7} {ft7})'\
                    .format(tn=table_name, nf1=field1, ft1=field1_type,nf2=field2, ft2=field2_type,nf3=field3, ft3=field3_type,nf4=field4, ft4=field4_type,
                            nf5=field5, ft5=field5_type,nf6=field6, ft6=field6_type,nf7=field7, ft7=field7_type))
            conn.commit()
            self.log.addLog("info","domain Database created")
        except sqlite3.Error as e:
            self.log.addLog("error","[InitializeDatabase create_domain_credentails_database] ====== "+e)
            
        
