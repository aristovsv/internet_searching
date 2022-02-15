import requests
import json
username = input("Enter the github username:")
request = requests.get('https://api.github.com/users/'+username+'/repos')
list = request.json()

for i in range(0,len(list)):
  print("Project Number:",i+1)
  print("Project Name:",list[i]['name'])
  print("Project URL:",list[i]['svn_url'],"\n")

with open ('C:\GB\json_dump\lesson_1', 'w') as file:
  json.dump(list, file)
