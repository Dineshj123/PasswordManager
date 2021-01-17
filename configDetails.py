import sys


class ConnectionDetails():
    sqlite_file = 'db/pwd_manager.sqlite'
    loggedInUserId = ""
    loggedInUserName = ""
    loggedInPassword=""
    domainCount=3
    def __init__(self):
        super(ConnectionDetails,self).__init__()    
        print("initialized Connection Details")
