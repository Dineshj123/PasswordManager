import sys,os,sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
#from PyQt5 import QtWidgets , QApplication, QWidget,QComboBox, QDialog,QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,QVBoxLayout
from Create import CreateMainBox
from Read import ReadMainBox
from Update import UpdateMainBox
from Delete import DeleteMainBox
from configDetails import ConnectionDetails
from Key import Key

class Database():
    def __init__(self):
        print("initializing database connection")
        super(Database,self).__init__()
        self.username=""        
        
    def create_users_database(self,userName,password):
        table_name = 'users'  
        field1 = 'user_id' 
        field1_type = 'INTEGER PRIMARY KEY AUTOINCREMENT'
        field2 = 'user_name' 
        field2_type = 'VARCHAR(100) NOT NULL'
        field3 = 'user_pass' 
        field3_type = 'VARCHAR(100) NOT NULL'
        #changed here
        self.status = 0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            val = (userName,password)
            c.execute('CREATE TABLE IF NOT EXISTS {tn} ({nf1} {ft1}, {nf2} {ft2}, {nf3} {ft3})'\
                    .format(tn=table_name, nf1=field1, ft1=field1_type,nf2=field2, ft2=field2_type,nf3=field3, ft3=field3_type))
            print("database created")
            if(self.checkUserName(userName) is not None):
                self.status = 2
            else:                
                sql = ''' INSERT INTO users(user_name,user_pass)
                          VALUES(?,?) '''
                c.execute(sql,val)
                print("user inserted")
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
        except Error as e:
            print(e)
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
            print(sql)
            userPassword = c.fetchall()
            if(userPassword):
                print("checked userName "+str(userPassword[0][0]))
                return userPassword[0]
            return None
        except:
            print("error checking userName")
            return None
    def checkCredentials(self,userName,password):
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            print(userName+"  "+password)
            userPassword,userId = self.checkUserName(userName)
            if(userPassword):
                self.username= userName
                ConnectionDetails.loggedInUserName = userName
                ConnectionDetails.loggedInUserId = userId
                print("loggedInUser")
                return (userPassword == password) 
            return False
        except:
            print("check credentials error")
            return False

    def getUserDetails(self,userName):
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            sql= "select user_id,user_name from users where user_name = '"+ ConnectionDetails.loggedInUserName +"'"
            print(sql)
            c.execute("select user_id,user_name from users where user_name = '"+ ConnectionDetails.loggedInUserName +"'")
            user = c.fetchall()
            print(user)
            self.status=1
            conn.commit()
            conn.close()
            return user[0][0]
            
        except Error as e:
            print(e)
            self.status = 0
            print("error")
            conn.close()
            return ""
        
      
class MasterPwdDailog(QDialog):
    def __init__(self):
        super(MasterPwdDailog,self).__init__()
        self.password = QLineEdit()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.password)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.exitStatus=False

    def closeEvent(self,event):
        print("closing dialog")
        event.accept()

    def accept(self):
        print("accepted")
        password = self.password.text()
        encryptKey = Key(password).getEncryptedKey()
        print(encryptKey)
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(password.encode('utf8').strip())
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            c = conn.cursor()
            c.execute("select count(*) from users where user_pass=?",(str(cipher),))
            row = c.fetchall()
            print(row[0][0])
            if(row[0][0] == 0):
                self.close()
            else:            
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
        except e:
            print("error connecting to database")
            self.exitStatus = False
            self.close()
            
    def getStatus(self):
        print("returning status "+str(self.exitStatus))
        return self.exitStatus


class NewUserDialogBox(QDialog):
    
 
    def __init__(self):
        super(NewUserDialogBox, self).__init__()
        self.createFormGroupBox()
        print("creating new user dialog box")
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
 
        self.setWindowTitle("New User Account")
 
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("User Credentials")
        layout = QFormLayout()
        self.userName = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.error = QLabel("Credentials are saved if closed without submitting")
        layout.addRow(self.error)
        layout.addRow(QLabel("UserName:"), self.userName)
        layout.addRow(QLabel("Password:"), self.password)
        self.formGroupBox.setLayout(layout)

    #predefined function on closing a dialog box
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()
        #if (self.exitStatus):
            #event.accept()
        #event.ignore()
        #self.accept()

    def getExitStatus(self):
        return self.exitStatus


    def acceptRegister(self):
        print("accepted")
        self.username = self.userName.text()
        self.pwd = str(self.password.text())
        self.exitStatus = False
        encryptKey = Key(self.pwd).getEncryptedKey()
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(self.pwd.encode('utf8').strip())
        print("accepted after")
        if (self.username.strip() == '' or self.pwd.strip() == ''):
            print("Stripping error")
            self.error.setText("Error!")
        else:
            self.database = Database()
            self.database.create_users_database(self.username,str(cipher))
            if self.database.get_status() == 1:
                self.error.setText("Saving credentials")
                ConnectionDetails.loggedInPassword = str(cipher)
                self.exitStatus = True
                print("exiting")
                self.close()
            elif self.database.get_status() == 2:
                print("user already exists")
                self.error.setText("User Already exists")
                #self.closeEvent()
            else:
                print("There was error creating database! Retry again")
                #self.closeEvent()
        
    def getUserName(self):
        return self.username
    #triggered when user submits credentials
    def accept(self):
        print("accepted")
        self.username = self.userName.text()
        self.pwd = str(self.password.text())
        encryptKey = Key(self.pwd).getEncryptedKey()
        print("encryptKey")
        print(encryptKey)
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(self.pwd.encode('utf8').strip())
        print("accepted after")
        if (self.username.strip() == '' or self.pwd.strip() == ''):
            print("Stripping error")
            self.error.setText("Error!")
        else:
            self.database = Database()
            loginStatus = self.database.checkCredentials(self.username,str(cipher))
            print("loginStatus ")
            if(loginStatus):
                self.error.setText("Saving credentials")
                ConnectionDetails.loggedInPassword = str(cipher)
                self.exitStatus = True
                print("exiting")
                self.close()
            else:
                self.error.setText("UserName/password is incorrect")
                self.exitStatus = False
 
class App(QWidget):
 
    def __init__(self):
        super(App,self).__init__()
        self.title = 'Password Manager'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        #code the logic to check if an account exists in DB
        #account_exists = True
        print("attempt")
        self.database = Database()
        '''
        self.status = int(self.database.check_user())
        print(self.status)
        if self.status == 0:
            self.show_login_box()
        else:
            self.show_main_box()
        '''
        self.show_login_box()
        #while(self.database.check_user() == 1):
            #print("login box")
            #self.show_login_box()
    #creating a groupbox of 4 buttons (CRUD)
    def show_main_box(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        self.createHorizontalGroupBox()
        self.database = Database()
        
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


        self.horizontalgroupbox.setLayout(layout)
            
    def show_create_dialog_box(self):
        self.create_main_box = CreateMainBox()
        #status = self.create_main_box.show()
        #print("status of mainbox creation is "+str(status))
    def show_read_dialog_box(self):
        self.read_main_box = ReadMainBox()
    def show_update_dialog_box(self):
        self.update_main_box = UpdateMainBox()
    def show_delete_dialog_box(self):
        self.delete_main_box = DeleteMainBox()
    def show_delete_acc_dialog_box(self):
        dialog = MasterPwdDailog()
        print("dialog created")
        dialog.exec_()
        self.status = dialog.getStatus()
        if(self.status == True):
            print("exiting")
            sys.exit(0)
    
    def show_login_box(self):
        new_user_dialog = NewUserDialogBox()
        status = new_user_dialog.exec_()
        print("status is "+ str(status))
        print(new_user_dialog.getExitStatus())
        if (new_user_dialog.getExitStatus()):
            print("exited try to reopen")
            print(new_user_dialog.getUserName())
            userName = new_user_dialog.getUserName()
            self.show_main_box()
 
if __name__ == '__main__':
    #setting db path
    path = os.path.join(os.getcwd(),"db")
    if(not(os.path.exists(path))):
        print("creating db path")
        os.makedirs(os.path.join(path))
        with open(os.path.join(path,"pwd_manager.sqlite"),"x"):
            print("file created")
            pass
    app = QApplication(sys.argv)
    ex = App()
    #print("closing application")
