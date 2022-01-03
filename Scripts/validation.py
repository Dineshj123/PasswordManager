import sys
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
from Config.configDetails import ConnectionDetails
from Key.Key import Key


class MasterPwdDailog(QDialog):
    def __init__(self):
        super(MasterPwdDailog,self).__init__()
        self.log = ConnectionDetails.self
        self.passwordName = QLabel("Enter Root Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.passwordName)
        mainLayout.addWidget(self.password)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.log.addLog("debug","[MasterPwdDailog __init__] ======  inside init")
        self.exitStatus=0

    def closeEvent(self,event):
        if(self.exitStatus == 0):
            self.exitStatus = 2
        event.accept()

    def accept(self):
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MasterPwdDailog accept] ======  accepted "+str(ConnectionDetails.loggedInUserId))
        password = self.password.text()
        if (password == '' or password == ''):
            self.log.addLog("error","[MasterPwdDailog accept] ===== Root password can not be blank")
            #self.error.setText("Error! Root password can not be blank")
        else:
            encryptKey = Key(password).getEncryptedKey()
            self.log.addLog("debug","[MasterPwdDailog accept] ======  got encryptKey ")
            cipher = encryptKey.encrypt(password.encode('utf8').strip())
            try:
                if(ConnectionDetails.loggedInPassword):
                    self.log.addLog("debug","[MasterPwdDailog accept] ======  password found ")
                    if (str(cipher) != str(ConnectionDetails.loggedInPassword)):
                        self.log.addLog("warning","[MasterPwdDailog accept] ======  No such password found in database ")
                        self.exitStatus = 0
                        self.close()
                    else:
                        self.log.addLog("debug","[MasterPwdDailog accept] ======  accepted! proceeding.. ")
                        self.exitStatus = 1
                        self.close()
                else:
                    self.log.addLog("warning","[MasterPwdDailog accept] ======  No such userId/password")
                    self.exitStatus = 0
                    self.close()
            except sqlite3.Error as e:
                self.log.addLog("error","[MasterPwdDailog accept] ======  "+e)
                self.close()
            
    def getStatus(self):
        self.log = ConnectionDetails.self
        self.log.addLog("debug","[MasterPwdDailog getStatus] ======  exitStatus "+str(self.exitStatus))
        return self.exitStatus
