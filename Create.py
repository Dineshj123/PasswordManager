import sys
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout,QInputDialog,QMainWindow)
import sqlite3
from configDetails import ConnectionDetails
from Key import Key
from validation import MasterPwdDailog

class Database():
    def __init__(self):
        print("initializing database connection")
        self.status=0
        super(Database,self).__init__()
        
    def create_credentials_database(self,domain,userId,userName,password):
            
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
        self.status=0
        
        try:
            print("getVersionCount")
            #vc = self.getVersionCount()
            #print("version count")
            #print(vc)
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print("database connected")
            c = conn.cursor()
            val = (domain,userId,userName,password,0)
            print("creating table")
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3},{nf4} {ft4},{nf5} {ft5},{nf6} {ft6},{nf7} {ft7})'\
                    .format(tn=table_name, nf1=field1, ft1=field1_type,nf2=field2, ft2=field2_type,nf3=field3, ft3=field3_type,nf4=field4, ft4=field4_type,
                            nf5=field5, ft5=field5_type,nf6=field6, ft6=field6_type,nf7=field7, ft7=field7_type))
            print("table created")
            sql = " INSERT INTO domain_credentials(domain,user_id,user_name,user_pass,version,creation_date) VALUES(?,?,?,?,?,datetime('now')) "
            c.execute(sql,val)
            print("credentials inserted")
            self.status = 1
            conn.commit()
            print("version updated")
            conn.close()
            
            print("committed and closed")
        except Error as e:
            print(e)
            print("error")
            self.status = 0
            conn.close()

    def getStatus(self):
        return self.status

    def getVersionCount(self):
        try:            
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            sql= "select version_count + 1 from users where user_id = " + str(ConnectionDetails.loggedInUserId) 
            print(sql)
            c.execute(sql)
            vc = c.fetchall()
            conn.close()
            print(vc)
            return vc[0][0]
        except Error as e:
            print(e)
            print("error getting version count of userId "+str(userId))
            return -1

class MainBox(QWidget):
    def __init__(self):
        super(MainBox,self).__init__()
        print("inside")
        self.title = 'Create Password'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.submitStatus = False
        self.createFormGroupBox()
        button = QPushButton('submit', self)
        button.clicked.connect(self.submit)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(button)
        print("entering group")
        self.setLayout(mainLayout)
        print("entering group")
        self.show()
 
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Enter Domain UserName Password")
        layout = QFormLayout()
        self.domain = QLineEdit()
        self.userName = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.error = QLabel("Credentials are saved if closed without submitting")
        layout.addRow(QLabel("Domain:"),self.domain)
        layout.addRow(QLabel("UserName:"), self.userName)
        layout.addRow(QLabel("Password:"), self.password)
        self.formGroupBox.setLayout(layout)
        
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()
        #if(self.submitStatus):
            #print("exiting show main box")
            #event.accept()
        #event.ignore()
        #self.submit()

    def submit(self):
        domain = self.domain.text()
        userName = self.userName.text()
        password = self.password.text()
        encryptKey = Key(ConnectionDetails.loggedInPassword).getEncryptedKey()
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(password.encode('utf8').strip())
        print(str(cipher))
        self.database = Database()
        self.database.create_credentials_database(domain,ConnectionDetails.loggedInUserId,userName,str(cipher))

        if (self.database.getStatus() == 1):
            print("Saved credentials successfully")
            self.submitStatus = True
            #print(self.main)
            #del self.main
            #print("deleted")
            self.close()
        else:
            print("error inserting credentials")
            
class CreateMainBox(QWidget):
    def __init__(self):
        super(CreateMainBox,self).__init__()
        self.create_master_dialog()
        self.create_main_box()
        #self.status = False
    
    def create_master_dialog(self):
        dialog = MasterPwdDailog()
        print("dialog created")
        dialog.exec_()
        self.status = dialog.getStatus()

    def create_main_box(self):
        print("main box inside")
        print(self.status)
        '''
        if(self.status == False):
            print("no error")
            self.create_master_dialog()
        else:
            close = self.show_main_box()
            print("close is "+str(close))
        '''
        while(self.status == 0):
            self.create_master_dialog()
        if(self.status!=2):
            close = self.show_main_box()
            print("close is "+str(close))
        else:
            pass
            

    def show_main_box(self):
        self.main = MainBox()
        #main = self.main
        #print(main)
        #self.main.post(main)
        status = self.main.show()
        return 0
    
