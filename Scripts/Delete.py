import sys,os
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QPushButton, QTextEdit,
        QVBoxLayout,QInputDialog,QMainWindow,QTableWidget,QTableWidgetItem)
import sqlite3
from Config.configDetails import ConnectionDetails
from Key.Key import Key
from Scripts.validation import MasterPwdDailog

class Database():
    def __init__(self):
        print("initializing database connection")
        self.status=0
        super(Database,self).__init__()
        self.log = ConnectionDetails.self
        self.log.addLog("info","[Database __init__] ====== initalized databased object")


    def get_credentials(self):
        self.log = ConnectionDetails.self
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print("database connected")
            c = conn.cursor()
            sql = 'select dc1.id,dc1.domain,dc1.user_name,dc1.user_pass,dc1.version,dc1.creation_date from domain_credentials as dc1 where 1=1 and dc1.creation_date = (select max(dc2.creation_date) from domain_credentials as dc2 where dc2.domain = dc1.domain ) '
            c.execute(sql)
            self.log.addLog("debug","[Database get_credentials] ====== sql "+sql)
            row = c.fetchall()
            print(row)
            print(len(row))
            self.log.addLog("info","[Database get_credentials] ====== records count "+str(len(row)))
            self.status = 1
            conn.close()
            print("committed and closed")
            return row
        except sqlite3.Error as e:
            self.log.addLog("error","[Database get_credentials] ====== "+e)
            self.status = 0
            conn.close()
            return 0

    def getStatus(self):
        return self.status

    def delete_credentials(self,curr_id):
        self.log = ConnectionDetails.self
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            self.curr_id = int(curr_id)
            cur = conn.cursor()
            sql = """delete from domain_credentials where id=? and user_id = ? """
            cur.execute(sql,(self.curr_id,ConnectionDetails.loggedInUserId,))
            self.log.addLog("info","[Database delete_credentials] ====== deleting id "+str(id)+" for "+ConnectionDetails.loggedInUserName)
            conn.commit()
            ConnectionDetails.backup = True
            conn.close()
            self.status = 1
            return 1
        except sqlite3.Error as e:
            self.log.addLog("error","[Database delete_credentials] ====== "+e)
            self.status = 0
            conn.close()
            return 0
    
class MainBox(QWidget):
    def __init__(self):
        super(MainBox,self).__init__()
        self.title = 'Delete Password'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.log = ConnectionDetails.self
        self.initUI()
    def initUI(self):
        self.log = ConnectionDetails.self
        self.setWindowTitle(self.title)
        self.setFixedSize(600,500)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.database = Database()
        self.rows = self.database.get_credentials()
        print(self.rows)
        self.createTable(self.rows)

        self.HorizontalGroupBox = QGroupBox("Delete Details")
        layout = QFormLayout()
        self.error=QLabel("")
        self.id = QLineEdit()
        self.domain = QLineEdit()
        self.username = QLineEdit()
        self.password = QLineEdit()
        button = QPushButton('Delete', self)
        button.clicked.connect(self.delete)
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
    

    def delete(self):
        self.log = ConnectionDetails.self
        curr_id = self.id.text()
        domain = str(self.domain.text())
        username = str(self.username.text())
        password = str(self.password.text())
        curr_id = int(curr_id.strip())
        self.database = Database()
        self.result = self.database.delete_credentials(curr_id)
        if(self.result == 1):
            self.log.addLog("debug","[Database update_credentials] ====== deleted successfully")
            self.close()
        else:
            self.error.setText("Error Deleting")
            self.log.addLog("error","[Database update_credentials] ====== error deleting")

    def createTable(self,row):
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MainBox createTable] ====== creating table")
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(row))
        self.tableWidget.setColumnCount(5)
        
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
        self.log.addLog("debug","[MainBox createTable] ====== done setting table fields")
        self.tableWidget.clicked.connect(self.copy)

    def copy(self):
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MainBox copy] ====== setting read only fields")
        for curr in self.tableWidget.selectedItems():
            self.id.setReadOnly(False)
            self.id.setText(str(self.rows[curr.row()][0]))
            self.id.setReadOnly(True)
            self.domain.setText(self.rows[curr.row()][1])
            self.username.setText(self.rows[curr.row()][2])
            decryptKey = Key(ConnectionDetails.loggedInPassword).getDecryptedKey()
            decodedPwd = decryptKey.decrypt(eval(self.rows[curr.row()][3])).decode("utf8")
            self.password.setText(str(decodedPwd))

        
    def closeEvent(self,event):
        event.accept()

            
class DeleteMainBox(QWidget):
    def __init__(self):
        super(DeleteMainBox,self).__init__()
        self.create_master_dialog()
        self.create_main_box()
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[DeleteMainBox __init__] ====== inside delete main box")
    
    def create_master_dialog(self):
        self.log = ConnectionDetails.self
        dialog = MasterPwdDailog()
        self.log.addLog("debug","[DeleteMainBox __init__] ====== validator dialg created")
        dialog.exec_()
        self.status = dialog.getStatus()

    def create_main_box(self):
        self.log = ConnectionDetails.self
        while(self.status == 0):
            self.log.addLog("warning","[DeleteMainBox create_master_dialog] ====== wrong root credentials for "+str(ConnectionDetails.loggedInUserName))
            self.create_master_dialog()
        if(self.status!=2):
            self.log.addLog("info","[DeleteMainBox create_master_dialog] ====== correct root credentials for "+str(ConnectionDetails.loggedInUserName))
            close = self.show_main_box()
        else:
            pass

    def show_main_box(self):
        self.main = MainBox()
        status = self.main.show()
        return 0
    
