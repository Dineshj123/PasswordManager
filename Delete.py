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
            sql = 'select dc1.* from domain_credentials as dc1 where 1=1 and dc1.creation_date = (select max(dc2.creation_date) from domain_credentials as dc2 where dc2.domain = dc1.domain ) '
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

    def delete_credentials(self,curr_id):
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print(conn)
            self.curr_id = int(curr_id)
            print(self.curr_id)
            print(type(self.curr_id))
            cur = conn.cursor()
            print("database connected")
            sql = """delete from domain_credentials where id=? and user_id = ? """
            cur.execute(sql,(self.curr_id,ConnectionDetails.loggedInUserId,))
            conn.commit()
            conn.close()
            self.status = 1
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
        self.title = 'Delete Password'
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
        curr_id = self.id.text()
        domain = str(self.domain.text())
        username = str(self.username.text())
        password = str(self.password.text())
        curr_id = int(curr_id.strip())
        self.database = Database()
        self.result = self.database.delete_credentials(curr_id)
        if(self.result == 1):
            print("Deleted successfully")
            self.close()
        else:
            self.error.setText("Error Deleting")
            print("Error Deleting")

    def createTable(self,row):
        print("comes")
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(row))
        self.tableWidget.setColumnCount(5)
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

            
class DeleteMainBox(QWidget):
    def __init__(self):
        super(DeleteMainBox,self).__init__()
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
    
