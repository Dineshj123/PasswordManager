
class ConnectionDetails():
    self = None
    backup = False
    title = "Password Manager"
    sqlite_file = "db/pwd_manager.sqlite"
    connectionPath= sqlite_file.split("/")[0]
    connectionFile = sqlite_file.split("/")[1]
    loggedInUserId = ""
    loggedInUserName = ""
    loggedInPassword=""
    domainCount=3
    def __init__(self):
        super(ConnectionDetails,self).__init__()    
        print("initialized Connection Details")
