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
        

class MainBox(QWidget):
    def __init__(self):
        super(MainBox,self).__init__()
        self.title = 'Read Password'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setFixedSize(640,800)
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.database = Database()
        self.rows = self.database.get_credentials()
        print(self.rows)
        self.createTable(self.rows)
 
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tableWidget) 
        self.setLayout(self.layout) 
        self.show()

    def createTable(self,row):
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(len(row))
        self.tableWidget.setColumnCount(5)
        self.rows = []
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Domain", "UserName", "Password","Status"])
        for i in range(0,len(row)):
            self.tableWidget.setItem(i,0, QTableWidgetItem(str(row[i][0])))
            self.tableWidget.setItem(i,1, QTableWidgetItem(row[i][1]))
            self.tableWidget.setItem(i,2, QTableWidgetItem(row[i][2]))
            decryptKey = Key(ConnectionDetails.loggedInPassword).getDecryptedKey()
            #print(decryptKey.decrypt(eval(row[i][3])).decode("utf8"))
            #print(type(decryptKey.decrypt(eval(row[i][3])).decode("utf8")))
            decodedPwd = decryptKey.decrypt(eval(row[i][3])).decode("utf8")
            print(decodedPwd)
            #self.rows[i][3] = str(decodedPwd)
            #print(decodedPwd)
            self.tableWidget.setItem(i,3, QTableWidgetItem(('*' * len(row[i][3]))))
            self.tableWidget.setItem(i,4, QTableWidgetItem("copy"))
            print(self.rows)
            print(str(row[i][0]))
            print(str(row[i][1]))
            print(str(row[i][2]))
            print(str(decodedPwd))
            self.rows.append( (str(row[i][0]), str(row[i][1]) , str(row[i][2]) , str(decodedPwd)) )
            print(self.rows)
        self.tableWidget.clicked.connect(self.copy)

    def copy(self):
        for curr in self.tableWidget.selectedItems():
            #print(self.rows[curr.row()][curr.column()])
            print(type(int(curr.column())))
            if (curr.column() == int(4)):
                command = 'echo | set /p nul=' + self.rows[curr.row()][3].strip() + '| clip'
                os.system(command)
            else:
                print("passing")
                pass

        
    def closeEvent(self,event):
        print("preparing to close")
        event.accept()
        #if(self.submitStatus):
            #print("exiting show main box")
            #event.accept()
        #event.ignore()
        #self.submit()

            
class ReadMainBox(QWidget):
    def __init__(self):
        super(ReadMainBox,self).__init__()
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
    
