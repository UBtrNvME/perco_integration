import os, sys

sys.path.append(os.getcwd())
import RPCRequest as req
from datetime import datetime

url = "https://pasport.qzhub.com"
db = "hrm-test1all"
username = "admin"
password = "Z3iuXfJQ35"
print(url)


class AttendanceSystem:
    def __init__(self, url, db, username, password):
        self.attendance_ids = {}
        self.employee_ids = {}
        self.rpc = req.RPCRequest(url, db, username, password)
        self.rpc.getReady()

    def createAttendance(self, name):
        employee_id = self.getEmployeeId(name=name)
        data = {
            'employee_id': employee_id
        }
        attendance_id = self.rpc.createRecord(model='hr.attendance', data=data)
        self.pushToEmployeeIds(name, employee_id)
        self.pushToAttendanceIds(name, attendance_id)

    def finishAttendance(self, name):
        attendance_id = self.getAttendanceId(name=name)
        checkOutTime = datetime.utcnow().replace(microsecond=0)

        data = {
            'check_out': str(checkOutTime)
        }
        self.rpc.updateRecord(model='hr.attendance', id=attendance_id, data=data)
        self.deleteAttendanceId(name=name)

    def pushToEmployeeIds(self, name, id):
        if name not in self.employee_ids:
            self.employee_ids[name] = id

    def pushToAttendanceIds(self, name, id):
        if name not in self.employee_ids:
            self.attendance_ids[name] = id

    def getEmployeeId(self, name):
        MODEL = 'hr.employee'

        def _getFromDictionary(name):
            return self.employee_ids[name]

        def _getFromOdoo(name):
            return self.rpc.searchRecord(model=MODEL, domain=[['name', '=', name]])[0]

        if name in self.employee_ids:
            return _getFromDictionary(name)
        else:
            return _getFromOdoo(name)

    def getAttendanceId(self, name):
        MODEL = 'hr.attendance'

        def _getFromDictionary(name):
            return self.employee_ids[name]

        def _getFromOdoo(name):
            return self.rpc.searchRecord(model=MODEL, domain=[['employee_id.name', '=', name]])[0]

        if name in self.attendance_ids:
            return _getFromDictionary(name)
        else:
            return _getFromOdoo(name)

    def deleteAttendanceId(self, name):
        if name in self.attendance_ids:
            self.attendance_ids.pop(name)
    #
    # def getTimeNow(self):
    #     pass
    #
    # def getTimeZoneDifference(self):
    #
    #     return
