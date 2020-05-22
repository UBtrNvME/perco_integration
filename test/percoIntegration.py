import requests
import time

#
# url = "http://ru.percoweb.com"
# params = {
#     "token" : "73e48IB68MwOktCFgIlwpKIT95vU68CJ",
#     "status": "active"
# }
# # response = requests.get(url="http://127.0.0.1/api/users/staff/table", params=params)
# # print(response.json())

# url = "https://pasport.qzhub.com/api/v1"
url = "https://pasport.qzhub.com/api/v1"
i = 0
employee = "Marc%20Demo"
headers = {
    'Content-Type': 'message/http'
}
params = {
    "employeeName": "Mitchell Admin"
}
while i < 2:
    response = False
    response = requests.post(url=url + "/createAttendance", headers=headers, params=params)
    print(response.url)
    response = requests.post(url=url + "/finishAttendance", headers=headers, params=params)
    i += 1
    print(response.reason)

