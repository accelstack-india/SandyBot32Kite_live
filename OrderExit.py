import sys
import json
from kite_trade import *
import pyotp

# Retrieve the two objects from sys.argv
arg_str = sys.argv[1]
json_strs = arg_str.split('|')

user_data = json.loads(json_strs[0])
stock_data = json.loads(json_strs[1])

# Print the objects to confirm they were passed correctly
print(f"This is subprocess for option execution received the data: {user_data} and {stock_data}")

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

def getRefreshTotp(totpToken):
    totp = pyotp.TOTP(totpToken)
    return totp.now()


kite = KiteApp(enctoken=get_enctoken(kite_client_id, kite_password, getRefreshTotp(TOTP_token)))

# get the positions for the user
def getPositions():
    return kite.positions()
print(getPositions())
# place the order for the user
# def placeOrder():
#     order = kite.place_order(variety="GTT",
#                              exchange=kite.EXCHANGE_NSE,
#                              tradingsymbol=trading_symbol,
#                              transaction_type=transaction_type,
#                              quantity=50,
#                              product=kite.PRODUCT_MIS,
#                              order_type=kite.ORDER_TYPE_MARKET,
#                              price=None,
#                              validity=None,
#                              disclosed_quantity=None,
#                              trigger_price=trigger_price,
#                              squareoff=square_off,
#                              stoploss=stop_loss,
#                              trailing_stoploss=None,
#                              tag="TradeViaPython")
#     return order
#
#
# print(placeOrder())
