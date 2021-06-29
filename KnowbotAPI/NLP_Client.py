import requests
from Feedback import feedback
import json
response = requests.put('http://10.245.167.78:5000/admin/loginadmin',json={"UserId":"superadmin","Password":"password"})
#response = requests.get('http://localhost:5000/admin/download/')
#response=admintask({"question":"what is automation1?","answer":"automation is love1"})
#response=feedback("nilay is das","1")
#a = response.json()
print(response)
