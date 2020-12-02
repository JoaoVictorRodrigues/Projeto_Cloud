from sys import argv
from datetime import datetime
import requests
import json

with open("loadBalancer_DNS.txt", "r") as file:
        text = file.readlines()

url = "http://" + text[0] + "/tasks/" 

COMMANDS = ["get", "add", "delete"]

if __name__ == "__main__":
    if argv[1] == COMMANDS[0]:
        response = requests.get(url + "get")
        print(response.text)
    elif argv[1] == COMMANDS[1]:
        if len(argv) == 4:
            title = argv[2]
            desc  = argv[3]
            date = datetime.now().isoformat()
            data = json.dumps({'title':title, 'pub_date':date, 'description': desc})
            response = requests.post(url + "post", data=data)
            print(response.text)
        else:
            print("Numero de argumentos incorreto.")
    elif argv[1] == COMMANDS[2]:
        response = requests.delete(url + "delete")
        print(response.text)
    else:
        print("syntax error: rota invalida")