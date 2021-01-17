import sys
from PyQt5.QtWidgets import (QApplication, QWidget,QComboBox, QDialog,
        QDialogButtonBox, QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
        QLabel, QLineEdit, QMenu, QMenuBar, QPushButton, QSpinBox, QTextEdit,
        QVBoxLayout)
from configDetails import ConnectionDetails
from Key import Key


class MasterPwdDailog(QDialog):
    def __init__(self):
        super(MasterPwdDailog,self).__init__()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.password)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        self.exitStatus=0

    def closeEvent(self,event):
        print("accepting event")
        if(self.exitStatus == 0):
            self.exitStatus = 2
        event.accept()

    def accept(self):
        print("accepted for userId ")
        password = self.password.text()
        encryptKey = Key(password).getEncryptedKey()
        print(encryptKey)
        #obj = AES.new(encryptKey, AES.MODE_CFB, encryptKey)
        cipher = encryptKey.encrypt(password.encode('utf8').strip())
        print(cipher)
        try:
            if(ConnectionDetails.loggedInPassword):
                print(cipher)
                if (str(cipher) != str(ConnectionDetails.loggedInPassword)):
                    print("No such password exists")
                    self.exitStatus = 0
                    self.close()
                else:
                    print("Proceeding...")
                    self.exitStatus = 1
                    self.close()
            else:
                print("No such userId / password")
                self.exitStatus = 0
                self.close()
        except Error as e:
            print(e)
            print("error connecting to database")
            self.close()
            
    def getStatus(self):
        print("returning status "+str(self.exitStatus))
        return self.exitStatus
