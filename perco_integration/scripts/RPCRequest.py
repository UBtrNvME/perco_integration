import xmlrpc.client as rpc


class RPCRequest:
    def __init__(self, url, db, username, password):
        self.db = db
        self.url = url
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        self.common = None

    def setCommon(self):
        self.common = rpc.ServerProxy("{}/xmlrpc/2/common".format(self.url))

    def authenticate(self):
        self.uid = self.common.authenticate(self.db, self.username, self.password, {})

    def setModel(self):
        self.models = rpc.ServerProxy("{}/xmlrpc/2/object".format(self.url))

    def checkAccessToModel(self, model, types):
        if self.models == None:
            raise Exception("Route is not set")
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'check_access_rights', types,
                                      {'raise_exception': False})
    
    def createRecord(self, model, data):
        array = [data]
        if self.models == None:
            raise Exception("Route is not set")
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'create', array)

    def updateRecord(self, model, id, data):
        array = [[id], data]
        if self.models == None:
            raise Exception("Route is not set")
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'write', array)

    def deleteRecord(self, model, id):
        array = [[id]]
        if self.models == None:
            raise Exception("Route is not set")
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'unlink', array)

    def searchRecord(self, model, domain):
        array = [domain]
        if self.models == None:
            raise Exception("Route is not set")
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'search', array)

    def getReady(self):
        self.setCommon()
        self.authenticate()
        self.setModel()
        print(self.common, self.models)

    def __del__(self):
        print("Deleted")
