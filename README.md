# PasswordManager
A customized desktop app to store, manage and secure your enterprise passwords in local system.

Features Available:
1. Add, read, update, delete domain passwords
2. Each domain userName password has 3 versions of it maintained in DB.
3. Auto Backup of DB program

Download instructions:
1. git clone <git-repo.git> --branch master --single-branch .
2. cd PasswordManager
   Install python and pip manually in windows.<br>
   Linux: <br>
      sudo apt-get update <br>
      sudo apt-get install -y python3  <br>
      sudo apt-get install -y python3-pip  <br>
      sudo apt-get install -y python3-pyqt5 <br>
   Python Dependencies:
      pip3 install PyQt5  <br>
      pip3 install pycrypto  <br>
      pip3 install db-sqlite3 <br>
      pip3 install pyperclip <br>
3. python3 main.py
