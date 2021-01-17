import sys,os
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit,
        QVBoxLayout,QInputDialog,QMainWindow,QTableWidget,QTableWidgetItem)
import sqlite3
from configDetails import ConnectionDetails
from Key import Key
from validation import MasterPwdDailog

class Database():
    def __init__(self):
        print("initializing database connection")
        self.status=0
        super(Database,self).__init__()
        
    def get_credentials(self):
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print("database connected")
            c = conn.cursor()
            sql = 'select dc1.id,dc1.domain,dc1.user_name,dc1.user_pass,dc1.version,dc1.creation_date from domain_credentials as dc1 where 1=1 and dc1.creation_date = (select max(dc2.creation_date) from domain_credentials as dc2 where dc2.domain = dc1.domain ) '
            c.execute(sql)
            row = c.fetchall()
            print(row)
            print(len(row))
            self.status = 1
            conn.close()
            print("committed and closed")
            return row
        except Error as e:
            print(e)
            print("error")
            self.status = 0
            conn.close()
            return 0

    def getStatus(self):
        return self.status

    def getMaxVersion(self,conn,domain):
        try:
            print(conn)
            curr = conn.cursor()
            print("sql")
            print(curr)
            sql = "select version from domain_credentials where creation_date = (select max(creation_date) from domain_credentials where domain='"+ str(domain) +"')"
            curr.execute(sql)
            print(sql)
            versionCount = curr.fetchall()
            print("returning max version ")
            print(versionCount[0][0])
            return versionCount[0][0]
        except e:
            print(e)
            print("error")
            self.status = 0
            return -2

    # function to upsert only if pwd different    
    def doUpsert(self,conn,curr_id,domain,userName,password):
        try:
            print(conn)
            cursor = conn.cursor()
            encryptKey = Key(ConnectionDetails.loggedInPassword).getEncryptedKey()
            print(encryptKey)
            #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
            cipher = encryptKey.encrypt(password.encode('utf8').strip())
            print(cipher)
            val = (domain,userName,curr_id)
            sql = "select count(*),user_pass from domain_credentials where domain='"+ str(domain) +"' and user_name='"+ str(userName) +"' and version='"+ str(curr_id) +"'"
            cursor.execute(sql)
            print(sql)
            rows = cursor.fetchall()
            print(rows)
            if(int(rows[0][0])==0 and str(cipher)!= rows[0][1]):
                sql = " INSERT INTO domain_credentials(domain,user_id,user_name,user_pass,version,creation_date) VALUES(?,?,?,?,?,datetime('now')) "
                cursor.execute(sql,(domain,ConnectionDetails.loggedInUserId,userName,str(cipher),curr_id,))
            elif(str(cipher)!= rows[0][1]):
                print("inside else")
                sql = " update domain_credentials set user_pass = ?,creation_date = datetime('now') where domain=? and user_name=? and version=? "
                print(sql)
                cursor.execute(sql,(str(cipher),domain,userName,str(curr_id),))
            conn.commit()
            self.status=1
        except e:
            print(e)
            self.status=0

    
    def update_credentials(self,curr_id,domain,username,password):
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print(conn)
            cur = conn.cursor()
            self.curr_id = int(curr_id)
            self.domain = str(domain)
            self.username = str(username)
            self.password = str(password)
            print("database connected")
            maxVersion = int(self.getMaxVersion(conn,domain))
            maxVersion+=1
            print(maxVersion%ConnectionDetails.domainCount)
            curr_id = int(maxVersion%ConnectionDetails.domainCount)
            print("curr_id "+str(curr_id))
            self.doUpsert(conn,curr_id,self.domain,self.username,self.password)
            self.status = 1
            conn.commit()
            conn.close()
            print("committed and closed")
            return 1
        except e:
            print(e)
            print("error")
            self.status = 0
            conn.close()
            return 0
    
class MainBox(QWidget):
    def __init__(self):
        super(MainBox,self).__init__()
        self.title = 'Update Password'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(840,950)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.database = Database()
        self.rows = self.database.get_credentials()
        print(self.rows)
        self.createTable(self.rows)

        self.HorizontalGroupBox = QGroupBox("Update Details")
        layout = QFormLayout()
        self.error=QLabel("")
        self.id = QLineEdit()
        self.domain = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        button = QPushButton('Update', self)
        button.clicked.connect(self.update)
        layout.addRow(QLabel("Id"),self.id)
        layout.addRow(QLabel("Domain"),self.domain)
        layout.addRow(QLabel("UserName"),self.username)
        layout.addRow(QLabel("Password"),self.password)
        self.HorizontalGroupBox.setLayout(layout)
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.HorizontalGroupBox)
        self.layout.addWidget(button)
        self.setLayout(self.layout) 
        self.show()
    

    def update(self):
        curr_id = int(self.id.text(),10)
        domain = str(self.domain.text())
        username = str(self.username.text())
        password = str(self.password.text())
        print("comes")
        domain = str(domain)
        username = str(username)
        password = str(password)
        curr_id = int(curr_id)
        self.database = Database()
        self.result = self.database.update_credentials(curr_id,domain,username,password)
        if(self.result == 1):
            print("Updated successfully")
            self.close()
        else:
            self.error.setText("Error Updating")
            print("Error updating")

    def createTable(self,row):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(row))
        self.tableWidget.setColumnCount(7)
        print("fine")
        self.rows = row
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Domain", "UserName", "Password","version","Creation_Date","Status"])

        for i in range(0,len(row)):
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(row[i][0])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(row[i][1]))
            self.tableWidget.setItem(i,2, QTableWidgetItem(row[i][2]))
            self.tableWidget.setItem(i,3, QTableWidgetItem(('*' * len(row[i][3]) )))
            self.tableWidget.setItem(i,4, QTableWidgetItem(str(row[i][4])))
            self.tableWidget.setItem(i,5, QTableWidgetItem(row[i][5]))
            self.tableWidget.setItem(i,6, QTableWidgetItem("copy"))
        print("done setting")
        self.tableWidget.clicked.connect(self.copy)

    def copy(self):
        print(self.id)
        for curr in self.tableWidget.selectedItems():
            self.id.setReadOnly(False)
            self.id.setText(str(self.rows[curr.row()][0]))
            self.id.setReadOnly(True)
            self.domain.setText(self.rows[curr.row()][1])
            self.username.setText(self.rows[curr.row()][2])

            decryptKey = Key(ConnectionDetails.loggedInPassword).getDecryptedKey()
            decodedPwd = decryptKey.decrypt(eval(self.rows[curr.row()][3])).decode("utf8")
            print(decodedPwd)
            self.password.setText(str(decodedPwd))
            
        
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()
        #if(self.submitStatus):
            #print("exiting show main box")
            #event.accept()
        #event.ignore()
        #self.submit()

            
class UpdateMainBox(QWidget):
    def __init__(self):
        super(UpdateMainBox,self).__init__()
        self.create_master_dialog()
        self.create_main_box()
        #self.status = False
    
    def create_master_dialog(self):
        dialog = MasterPwdDailog()
        print("dialog created")
        dialog.exec_()
        self.status = dialog.getStatus()

    def create_main_box(self):
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
    
