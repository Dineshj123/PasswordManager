import sys,os,sqlite3,time
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
from Scripts.Create import CreateMainBox
from Scripts.Read import ReadMainBox
from Scripts.Update import UpdateMainBox
from Scripts.Delete import DeleteMainBox
from Config.configDetails import ConnectionDetails
from DataBase.Database import InitializeDatabase
from Key.Key import Key
from pathlib import Path
from Logger.Logs import Logs

class Database():
    def __init__(self):
        super(Database,self).__init__()
        self.username=""
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[Database __ini__] ===== Database object created")
        
    def create_users_database(self,userName,password):
        self.status = 0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            val = (userName,password)
            if(not(self.checkUserName(userName))):
                self.status = 2
            else:                
                sql = ''' INSERT INTO users(user_name,user_pass)
                          VALUES(?,?) '''
                c.execute(sql,val)
                self.log.addLog("info","[create_users_database] ===== user "+str(userName)+" inserted")
                ConnectionDetails.loggedInUserName = userName
                self.status=1
                conn.commit()
                sql = "select user_id from users where user_name = '"+str(userName)+"'"
                c.execute(sql)
                print(sql)
                userIdList = c.fetchall()
                print(userIdList)
                ConnectionDetails.loggedInUserId = str(userIdList[0][0])
                conn.close()
        except sqlite3.Error as e:
            print(e)
            self.log.addLog("error","[create_users_database] ===== error ")
            self.log.addLog("error",e)
            self.status = 0
            print("error")
            conn.close()
            
        
    def get_status(self):
        return self.status
    #returns password if user is valid
    def checkUserName(self,userName):
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            sql = "select user_pass,user_id from users where user_name = '"+ str(userName) +"'"
            print(sql)
            c.execute(sql)
            self.log.addLog("debug","[checkUserName] ===== sql "+sql)
            userPassword = c.fetchall()
            if(userPassword):
                print("checked userName "+str(userPassword[0][0]))
                return userPassword[0]
            return ["",-1]
        except sqlite3.Error as e:
            print("error checking userName")
            self.log.addLog("error","[checkUserName] ==== error in checkUserName")
            self.log.addLog("error",e)
            return None
    def checkCredentials(self,userName,password):
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            self.log.addLog("debug","[checkCredentials] ===== checking userName ")
            userPassword,userId = self.checkUserName(userName)
            if(userPassword):
                self.username= userName
                ConnectionDetails.loggedInUserName = userName
                ConnectionDetails.loggedInUserId = userId
                self.log.addLog("debug","[checkCredentials] ===== checking userPassword ")
                return (userPassword == password) 
            return False
        except sqlite3.Error as e:
            print("check credentials error")
            self.log.addLog("error","[checkCredentials] ===== error in checking credentials ")
            self.log.addLog("error",e)
            print(e)
            return False

    def getUserDetails(self,userName):
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            sql= "select user_id,user_name from users where user_name = '"+ ConnectionDetails.loggedInUserName +"'"
            self.log.addLog("debug","[getUserDetails] ===== sql "+sql)
            c.execute("select user_id,user_name from users where user_name = '"+ ConnectionDetails.loggedInUserName +"'")
            user = c.fetchall()
            print(user)
            self.status=1
            conn.commit()
            conn.close()
            return user[0][0]
            
        except sqlite3.Error as e:
            print(e)
            self.status = 0
            print("error")
            conn.close()
            return ""
        
      
class MasterPwdDailog(QDialog):
    def __init__(self):
        super(MasterPwdDailog,self).__init__()
        self.log = ConnectionDetails.self
        self.password = QLineEdit()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.password)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.exitStatus=False
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MasterPwdDailog __ini__] ===== ")

    def closeEvent(self,event):
        print("closing dialog")
        event.accept()

    def accept(self):
        self.log.addLog("debug","[MasterPwdDailog : accept] ===== accepted")
        password = self.password.text()
        encryptKey = Key(password).getEncryptedKey()
        print(encryptKey)
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(password.encode('utf8').strip())
        self.log.addLog("debug","[MasterPwdDailog : accept] ===== cipher ")
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            if (str(cipher) == str(ConnectionDetails.loggedInPassword)):
                self.log.addLog("warning","[MasterPwdDailog : accept] ===== dropping all tables ")
                c.execute('delete from users')
                conn.commit()
                c.execute('drop table users')
                conn.commit()
                print("users deleted")
                c.execute('delete from domain_credentials')
                conn.commit()
                c.execute('drop table domain_credentials')
                conn.commit()
                print("credentials deleted")
                self.exitStatus = True
                conn.close()
                self.close()
                ConnectionDetails.loggedInUserName = ""
                ConnectionDetails.loggedInPassword = ""
        except sqlite3.Error as e:
            print("error connecting to database")
            self.log.addLog("error","[MasterPwdDailog : accept] ===== error while deleting tables")
            self.log.addLog("error","[MasterPwdDailog : accept] ===== "+e)
            self.exitStatus = False
            self.close()
            
    def getStatus(self):
        return self.exitStatus


class NewUserDialogBox(QDialog):
    def __init__(self):
        super(NewUserDialogBox, self).__init__()
        self.createFormGroupBox()
        self.log = ConnectionDetails.self
        print(self.log)
        self.log.addLog("debug","[NewUserDialogBox __init__] ===== ")
        self.exitStatus = False
        Hlayout = QHBoxLayout()

        register_button = QPushButton('Register',self)
        register_button.clicked.connect(self.acceptRegister)
        Hlayout.addWidget(register_button)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        Hlayout.addWidget(register_button)
        Hlayout.addWidget(buttonBox)
 
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addLayout(Hlayout)
        self.setLayout(mainLayout)
        self.log.addLog("debug","[NewUserDialogBox __init__] ===== register/login box set")
 
        self.setWindowTitle("New User Account")
 
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("User Credentials")
        layout = QFormLayout()
        self.log = ConnectionDetails.self
        self.userName = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.error = QLabel("Credentials are saved if closed without submitting")
        layout.addRow(self.error)
        layout.addRow(QLabel("UserName:"), self.userName)
        layout.addRow(QLabel("Password:"), self.password)
        self.formGroupBox.setLayout(layout)
        self.log.addLog("debug","[NewUserDialogBox createFormGroupBox] ===== register/login box set")

    #predefined function on closing a dialog box
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()

    def getExitStatus(self):
        return self.exitStatus


    def acceptRegister(self):
        print("accepted")
        self.username = self.userName.text()
        self.pwd = str(self.password.text())
        self.exitStatus = False
        encryptKey = Key(self.pwd).getEncryptedKey()
        self.log.addLog("debug","[NewUserDialogBox acceptRegister] ===== got encrypt Key")
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(self.pwd.encode('utf8').strip())
        print("accepted after")
        if (self.username.strip() == '' or self.pwd.strip() == ''):
            self.log.addLog("error","[NewUserDialogBox acceptRegister] ===== striperror")
            self.error.setText("Error! userName/password should not be blank")
        else:
            self.database = Database()
            self.database.create_users_database(self.username,str(cipher))
            if self.database.get_status() == 1:
                self.log.addLog("debug","[NewUserDialogBox acceptRegister] ===== saving credentials")
                ConnectionDetails.loggedInPassword = str(cipher)
                self.exitStatus = True
                print("exiting")
                self.close()
            elif self.database.get_status() == 2:
                self.log.addLog("debug","[NewUserDialogBox acceptRegister] ===== user already exists")
                self.error.setText("User Already exists")
            else:
                self.log.addLog("debug","[NewUserDialogBox acceptRegister] ===== inside else "+str(self.database.get_status()))
        
    def getUserName(self):
        return self.username
    
    #triggered when user submits credentials
    def accept(self):
        print("accepted")
        self.username = self.userName.text()
        self.pwd = str(self.password.text())
        encryptKey = Key(self.pwd).getEncryptedKey()
        self.log.addLog("debug","[NewUserDialogBox accept] ===== got excrypted Key")
        cipher = encryptKey.encrypt(self.pwd.encode('utf8').strip())
        if (self.username.strip() == '' or self.pwd.strip() == ''):
            self.log.addLog("error","[NewUserDialogBox accept] ===== striperror")
            self.error.setText("Error! userName/password should not be blank")
        else:
            self.database = Database()
            loginStatus = self.database.checkCredentials(self.username,str(cipher))
            self.log.addLog("debug","[NewUserDialogBox accept] ===== loginstatus "+str(loginStatus))
            if(loginStatus):
                self.log.addLog("debug","[NewUserDialogBox acceptRegister] ===== saving credentials")
                ConnectionDetails.loggedInPassword = str(cipher)
                self.exitStatus = True
                print("exiting")
                self.close()
            else:
                self.log.addLog("error","[NewUserDialogBox acceptRegister] ===== UserName/password not Valid. If new please register")
                self.error.setText("UserName/password not Valid. If new please register")
                self.exitStatus = False
 
class App(QWidget):
 
    def __init__(self):
        super(App,self).__init__()
        self.title = ConnectionDetails.title
        self.left = 100
        self.top = 100
        self.width = 640
        self.height = 480
        print(self)
        self.log = ConnectionDetails.self
        self.initUI()
 
    def initUI(self):
        self.log = ConnectionDetails.self
        print(self)
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        self.show()
        print(self.log)
        self.log.addLog("debug","[App initUI] ===== opening app login page")
        self.database = Database()
        self.show_login_box()
        
    #creating a groupbox of 4 buttons (CRUD)
    def show_main_box(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(800,400)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        self.createHorizontalGroupBox()
        self.database = Database()
        self.log.addLog("debug","[App show_main_box] ===== opening main box")
        self.user = QLabel("Hi, "+str(ConnectionDetails.loggedInUserName))
        layout = QVBoxLayout()
        layout.addWidget(self.user)
        layout.addWidget(self.horizontalgroupbox)
        self.setLayout(layout)
                        
    def createHorizontalGroupBox(self):
        self.horizontalgroupbox = QGroupBox()
        layout = QHBoxLayout()

        create_button = QPushButton('Create',self)
        create_button.clicked.connect(self.show_create_dialog_box)
        layout.addWidget(create_button)

        read_button = QPushButton('Read',self)
        read_button.clicked.connect(self.show_read_dialog_box)
        layout.addWidget(read_button)

        update_button = QPushButton('Update',self)
        update_button.clicked.connect(self.show_update_dialog_box)
        layout.addWidget(update_button)

        delete_button = QPushButton('Delete',self)
        delete_button.clicked.connect(self.show_delete_dialog_box)
        layout.addWidget(delete_button)

        delete_acc_button = QPushButton('Delete Account',self)
        delete_acc_button.clicked.connect(self.show_delete_acc_dialog_box)
        layout.addWidget(delete_acc_button)

        self.log.addLog("debug","[App createHorizontalGroupBox] ===== created CRUD buttons")

        self.horizontalgroupbox.setLayout(layout)
    
            
    def show_create_dialog_box(self):
        self.log.addLog("debug","[App show_create_dialog_box] ===== opening create forms")
        self.create_main_box = CreateMainBox()
    def show_read_dialog_box(self):
        self.read_main_box = ReadMainBox()
    def show_update_dialog_box(self):
        self.update_main_box = UpdateMainBox()
    def show_delete_dialog_box(self):
        self.delete_main_box = DeleteMainBox()
    def show_delete_acc_dialog_box(self):
        dialog = MasterPwdDailog()
        self.log.addLog("warning","[show_delete_acc_dialog_box] ===== delete account dialog box created")
        dialog.exec_()
        self.status = dialog.getStatus()
        if(self.status == True):
            self.log.addLog("warning","[App show_delete_acc_dialog_box] ===== exiting")
            sys.exit(0)
                        
    
    
    def show_login_box(self):
        new_user_dialog = NewUserDialogBox()
        status = new_user_dialog.exec_()
        print(new_user_dialog.getExitStatus())
        if (new_user_dialog.getExitStatus()):
            self.log.addLog("debug","[show_login_box] ===== exited trying to open")
            userName = new_user_dialog.getUserName()
            self.show_main_box()
