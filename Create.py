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
        self.status=0
        super(Database,self).__init__()
        self.log = ConnectionDetails.self
        
    def create_credentials_database(self,domain,userId,userName,password):
            
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
            print("table created")
            sql = " INSERT INTO domain_credentials(domain,user_id,user_name,user_pass,version,creation_date) VALUES(?,?,?,?,?,datetime('now')) "
            c.execute(sql,val)
            self.log.addLog("debug","[Database create_credentials_database] ===== sql "+sql)
            self.status = 1
            conn.commit()
            self.log.addLog("info","[Database create_credentials_database] ===== credentials inserted ")
            conn.close()
        except sqlite3.Error as e:
            self.log.addLog("error","[Database create_credentials_database] =====  "+e)
            self.status = 0
            conn.close()

    def getStatus(self):
        return self.status

    def getVersionCount(self):
        try:            
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            sql= "select version_count + 1 from users where user_id = " + str(ConnectionDetails.loggedInUserId) 
            self.log.addLog("debug","[Database getVersionCount] =====  sql "+sql)
            c.execute(sql)
            vc = c.fetchall()
            conn.close()
            print(vc)
            return vc[0][0]
        except sqlite3.Error as e:
            print(e)
            self.log.addLog("error","[Database getVersionCount] ===== "+e)
            self.log.addLog("error","[Database getVersionCount] =====  error while getting version count "+str(userId))
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
        print(ConnectionDetails.self)
        self.log = ConnectionDetails.self
        self.initUI()
    def initUI(self):
        self.log = ConnectionDetails.self
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        self.submitStatus = False
        self.createFormGroupBox()
        button = QPushButton('submit', self)
        button.clicked.connect(self.submit)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(button)
        self.log.addLog("debug","[MainBox initUI] ====== opening validator box")
        self.setLayout(mainLayout)
        self.show()
 
    def createFormGroupBox(self):
        self.log = ConnectionDetails.self
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
        self.log.addLog("debug","[MainBox createFormGroupBox] ====== create form")
        
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()

    def submit(self):
        self.log = ConnectionDetails.self
        domain = self.domain.text()
        userName = self.userName.text()
        password = self.password.text()
        encryptKey = Key(ConnectionDetails.loggedInPassword).getEncryptedKey()
        self.log.addLog("debug","[MainBox submit] ====== got encryptedKey")
        cipher = encryptKey.encrypt(password.encode('utf8').strip())
        self.log.addLog("debug","[MainBox submit] ====== retrieved cipher")
        self.database = Database()
        self.database.create_credentials_database(domain,ConnectionDetails.loggedInUserId,userName,str(cipher))
        self.log.addLog("debug","[MainBox submit] ====== credentials inserted for "+str(ConnectionDetails.loggedInUserName))

        if (self.database.getStatus() == 1):
            self.log.addLog("debug","[MainBox submit] ====== Saved credentials successfully")
            self.submitStatus = True
            self.close()
        else:
            self.log.addLog("error","[MainBox submit] ====== error inserting credentials"+str(self.database.getStatus()))
            
class CreateMainBox(QWidget):
    def __init__(self):
        super(CreateMainBox,self).__init__()
        self.create_master_dialog()
        self.create_main_box()
        print("self")
        print(self)
        self.log = ConnectionDetails.self
        self.log.addLog("info","[CreateMainBox __init__] ====== inside create domain forms ")
    
    def create_master_dialog(self):
        self.log = ConnectionDetails.self
        dialog = MasterPwdDailog()
        self.log.addLog("debug","[CreateMainBox create_master_dialog] ====== dialog created")
        dialog.exec_()
        self.status = dialog.getStatus()

    def create_main_box(self):
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[CreateMainBox create_master_dialog] ====== inside main box")
        print(self.status)
        while(self.status == 0):
            self.log.addLog("warning","[CreateMainBox create_master_dialog] ====== wrong root credentials for "+str(ConnectionDetails.loggedInUserName))
            self.create_master_dialog()
        if(self.status!=2):
            self.log.addLog("info","[CreateMainBox create_master_dialog] ====== correct root credentials for "+str(ConnectionDetails.loggedInUserName))
            close = self.show_main_box()
        else:
            pass
            

    def show_main_box(self):
        self.main = MainBox()
        status = self.main.show()
        return 0
    
