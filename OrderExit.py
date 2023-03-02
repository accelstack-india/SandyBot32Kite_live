import sys
import json
from kite_trade import *
import pyotp

# Retrieve the two objects from sys.argv
arg_str = sys.argv[1]
json_strs = arg_str.split('|')

user_data = json.loads(json_strs[0])
stock_data = json.loads(json_strs[1])

# python programm using the API
arg_str = sys.argv[1]
json_strs = arg_str.split('|')

user_data = json.loads(json_strs[0])
stock_data = json.loads(json_strs[1])

# user details for whom the trade should get executed
user_id = user_data['user_id']
TOTP_token = user_data['totpToken']
kite_client_id = user_data['kiteClientId']
kite_password = user_data['kitePassword']

# stock whoich should be executed
trading_symbol = stock_data['tradingsymbol']
transaction_type = stock_data['transaction_type']
trigger_price = stock_data['trigger_price']
square_off = stock_data['squareoff']
stop_loss = stock_data['stoploss']

endpoint = "http://127.0.0.1:5000/placeOrder"
data = {"kite_client_id": kite_client_id, "kite_password": kite_password, "totp_token": TOTP_token, "trade_symbol":trading_symbol}
response = requests.post(endpoint, json=data)
print(response.text)
