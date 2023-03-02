import sys
import subprocess
import json
import requests
from userController import userController

# receive the stock list in arguments from algorith to execute the stock
arg_str = sys.argv[1]
stocks_list = json.loads(arg_str)

endpoint = "http://127.0.0.1:5000/users_list"
for stocks in stocks_list:
    data = {"kite_client_id":"Index " + stocks["type"]}
    response = requests.post(endpoint, json=data)
    print(response.json())
    user_list = response.json()
    for user in user_list:
        users_data = json.dumps(user)
        stocks_data = json.dumps(stocks)
        arg_str = f'{users_data}|{stocks_data}'
        # send the stock details and user details to place the order
        for i in range(5):
            subprocess.Popen(['python', "OrderExecution.py", arg_str])