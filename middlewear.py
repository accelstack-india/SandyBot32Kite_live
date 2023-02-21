import sys
import subprocess
import json

from userController import userController

arg_str = sys.argv[1]
stocks_list = json.loads(arg_str)

for stocks in stocks_list:
    users_list = userController.get_OptionalTradeUsers("Index " + stocks["type"])
    for user in users_list:
        users_data = json.dumps(user)
        stocks_data = json.dumps(stocks)
        arg_str = f'{users_data}|{stocks_data}'
        print("------------middlewear subprocess received stock and calling another subprocess to execute the stock for user----------------------")
        subprocess.Popen(['python', "Options_OrderExecution.py", arg_str])

