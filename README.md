# PasswordManager
A customized desktop app to store and manage your enterprise passwords in local system.

Features Available:
1. Add, read, update, delete domain passwords
2. Each domain userName password has 3 versions of it maintained in DB.
3. Auto Backup of DB program

Download instructions:
1. git clone <git-repo.git>
2. cd PasswordManager
   install python and pip manually in windows
   In Linux:
      - sudo apt-get install -y python3
      - sudo apt-get install -y python3-pip
      - pip3 install PyQt5
      - pip3 install pycrypto
      - pip3 install db-sqlite3
3. python3 main.py
