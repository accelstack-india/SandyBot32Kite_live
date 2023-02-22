import sys
import subprocess
import json

from userController import userController

# receive the stock list in arguments from algorith to execute the stock
arg_str = sys.argv[1]
stocks_list = json.loads(arg_str)

# for each stock received in the arguments get the users subscribed to the stock type and send for order execution
for stocks in stocks_list:
    users_list = userController.get_subscribedUsers("Index " + stocks["type"])
    for user in users_list:
        users_data = json.dumps(user)
        stocks_data = json.dumps(stocks)
        arg_str = f'{users_data}|{stocks_data}'
        # send the stock details and user details to place the order
        subprocess.Popen(['python', "OrderExecution.py", arg_str])

