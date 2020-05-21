import requests

#
# url = "http://ru.percoweb.com"
# params = {
#     "token" : "73e48IB68MwOktCFgIlwpKIT95vU68CJ",
#     "status": "active"
# }
# # response = requests.get(url="http://127.0.0.1/api/users/staff/table", params=params)
# # print(response.json())

url = "localhost:8383/api/v1"
i = 0
employee = "Aitemir%20Kuandyk"
while i < 1:
    requests.post(url=url + "/createAttendance/" + employee)
    requests.post(url=url + "/finishAttendance/" + employee)
    i += 1