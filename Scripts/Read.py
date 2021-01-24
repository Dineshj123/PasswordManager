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
        super(Database,self).__init__()
        self.status=0
        self.log = ConnectionDetails.self
        self.log.addLog("info","[Database __init__] ====== initalized databased object")
        
    def get_credentials(self):
        self.log = ConnectionDetails.self
        self.status=0
        try:
            conn = sqlite3.connect(ConnectionDetails.sqlite_file)
            print("database connected")
            c = conn.cursor()
            sql = 'select dc1.* from domain_credentials as dc1 where 1=1 and dc1.creation_date = (select max(dc2.creation_date) from domain_credentials as dc2 where dc2.domain = dc1.domain ) '
            c.execute(sql)
            self.log.addLog("debug","[Database get_credentials] ====== sql "+sql)
            row = c.fetchall()
            print(row)
            print(len(row))
            self.log.addLog("info","[Database get_credentials] ====== records count "+str(len(row)))
            self.status = 1
            conn.close()
            return row
        except sqlite3.Error as e:
            self.log.addLog("error","[Database get_credentials] ====== "+e)
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
        self.log = ConnectionDetails.self
        self.initUI()
    def initUI(self):
        self.log = ConnectionDetails.self
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
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MainBox createTable] ====== creating table")
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
            self.log.addLog("debug","[MainBox createTable] ====== decryptKey found")
            decodedPwd = decryptKey.decrypt(eval(row[i][3])).decode("utf8")
            self.tableWidget.setItem(i,3, QTableWidgetItem(('*' * len(row[i][3]))))
            self.tableWidget.setItem(i,4, QTableWidgetItem("copy"))
            self.rows.append( (str(row[i][0]), str(row[i][1]) , str(row[i][2]) , str(decodedPwd)) )
        self.tableWidget.clicked.connect(self.copy)

    def copy(self):
        self.log = ConnectionDetails.self
        for curr in self.tableWidget.selectedItems():
            if (curr.column() == int(4)):
                self.log.addLog("debug","[MainBox copy] ====== copying password to clipboard")
                command = 'echo | set /p nul=' + self.rows[curr.row()][3].strip() + '| clip'
                os.system(command)
            else:
                self.log.addLog("debug","[MainBox copy] ====== pressed outside password column")
                pass

        
    def closeEvent(self,event):
        event.accept()

            
class ReadMainBox(QWidget):
    def __init__(self):
        super(ReadMainBox,self).__init__()
        self.create_master_dialog()
        self.create_main_box()
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[ReadMainBox __init__] ====== inside Read main box")
        #self.status = False
    
    def create_master_dialog(self):
        self.log = ConnectionDetails.self
        dialog = MasterPwdDailog()
        self.log.addLog("debug","[ReadMainBox create_master_dialog] ====== dialog created")
        dialog.exec_()
        self.status = dialog.getStatus()

    def create_main_box(self):
        self.log = ConnectionDetails.self
        while(self.status == 0):
            self.log.addLog("warning","[ReadMainBox create_master_dialog] ====== wrong root credentials for "+str(ConnectionDetails.loggedInUserName))
            self.create_master_dialog()
        if(self.status!=2):
            self.log.addLog("info","[ReadMainBox create_master_dialog] ====== correct root credentials for "+str(ConnectionDetails.loggedInUserName))
            close = self.show_main_box()
        else:
            pass

    def show_main_box(self):
        self.main = MainBox()
        status = self.main.show()
        return 0
    
