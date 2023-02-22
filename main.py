import json
import time
import subprocess

import pyotp

from constants import fut_insert_query, opt_insert_query
from kite_trade import *
import datetime
import pandas as pd
import pandas_ta as ta
import pymysql
import requests
import socket

pd.options.mode.chained_assignment = None

totpToken = "E6O4KPIAJ35QMZDLSEVUZL42MJUDHPFO"

kiteClientId = "XL0940"
kitePassword = "pooja@#123"


def connectMysql():
    # connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
    #                              autocommit=True, max_allowed_packet=67108864)
    #
    connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
                                 autocommit=True, max_allowed_packet=67108864)

    return connection


def getRefreshTotp():
    totp = pyotp.TOTP(totpToken)
    return totp.now()


kite = KiteApp(enctoken=get_enctoken(kiteClientId, kitePassword, getRefreshTotp()))


def getMargin():
    return kite.margins()


def getOrders():
    return kite.orders()


def getPositions():
    return kite.positions()


def getAllInstruments():
    return kite.instruments()


def getNSEInstruments():
    return kite.instruments("NSE")


def getNFOInstruments():
    return kite.instruments("NFO")


def getLtpInstrument(instrument):
    return kite.ltp("NSE:" + instrument)


def getLtpMultipleInstruments(instruments):
    # return kite.ltp(["NSE:ITC", "NSE:RELIANCE"])
    return kite.ltp(instruments)


def getIndexLtp():
    return kite.ltp(["NSE:NIFTY 50", "NSE:NIFTY BANK"])


def getQuoteOfInstrument():
    kite.quote(["NSE:NIFTY BANK", "NSE:ACC", "NFO:NIFTY22SEPFUT"])


def getHistoricalData(instrumentToken):
    from_datetime = datetime.datetime.now() - datetime.timedelta(days=15)  # From last & days
    to_datetime = datetime.datetime.now()
    interval = "5minute"
    return kite.historical_data(instrumentToken, from_datetime, to_datetime, interval, continuous=False, oi=False)


def placeOrder():
    order = kite.place_order(variety=kite.VARIETY_REGULAR,
                             exchange=kite.EXCHANGE_NSE,
                             tradingsymbol="ACC",
                             transaction_type=kite.TRANSACTION_TYPE_BUY,
                             quantity=1,
                             product=kite.PRODUCT_MIS,
                             order_type=kite.ORDER_TYPE_MARKET,
                             price=None,
                             validity=None,
                             disclosed_quantity=None,
                             trigger_price=None,
                             squareoff=None,
                             stoploss=None,
                             trailing_stoploss=None,
                             tag="TradeViaPython")
    return order


def modifyOrder():
    kite.modify_order(variety=kite.VARIETY_REGULAR,
                      order_id="order_id",
                      parent_order_id=None,
                      quantity=5,
                      price=200,
                      order_type=kite.ORDER_TYPE_LIMIT,
                      trigger_price=None,
                      validity=kite.VALIDITY_DAY,
                      disclosed_quantity=None)


def cancelOrder():
    kite.cancel_order(variety=kite.VARIETY_REGULAR,
                      order_id="order_id",
                      parent_order_id=None)


def calculateIndicators(hisToricData):
    columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    df = pd.DataFrame(hisToricData, columns=columns)
    df['datetime'] = pd.to_datetime(df['date'], format='%Y-%m-%dT%H:%M:%S').dt.tz_localize(None)
    df.set_index(pd.DatetimeIndex(df["datetime"]), inplace=True)
    df.ta.rsi(close=df['close'], length=14, append=True)
    df.ta.stochrsi(close=df['close'], length=14, k=3, d=3, append=True)
    df.ta.ema(close=df['close'], length=9, append=True)
    df.ta.wma(close=df['close'], length=9, append=True)
    df.ta.sma(close=df['close'], length=9, append=True)
    df.ta.atr(high=df['high'], low=df['low'], close=df['close'], timeperiod=14, append=True)
    df.ta.macd(close=df['close'], fast=12, slow=26, signal=9, append=True)
    df.ta.vwap(high=df['high'], low=df['low'], close=df['close'], volume=df['volume'], append=True)
    df.ta.supertrend(high=df['high'], low=df['low'], close=df['close'], period=20, multiplier=2, append=True)
    return df


def calculateIndicatorCrossOvers(dfIndicators):
    dfIndicators['VWAP_CROSS'] = 0
    dfIndicators['SUPERTREND_CROSS'] = 0
    dfIndicators['MACD_CROSS'] = 0
    dfIndicators['EMA_CROSS'] = 0
    dfIndicators['RSI_CROSS'] = 0
    for i in range(len(dfIndicators)):
        if dfIndicators['close'][i - 1] <= dfIndicators['VWAP_D'][i - 1] and dfIndicators['close'][i] > \
                dfIndicators['VWAP_D'][i]:
            dfIndicators['VWAP_CROSS'][i] = 1
        if dfIndicators['close'][i - 1] >= dfIndicators['VWAP_D'][i - 1] and dfIndicators['close'][i] < \
                dfIndicators['VWAP_D'][i]:
            dfIndicators['VWAP_CROSS'][i] = -1
        if dfIndicators['SUPERTd_7_2.0'][i] == -1:
            dfIndicators['SUPERTREND_CROSS'][i] = -1
        if dfIndicators['SUPERTd_7_2.0'][i] == 1:
            dfIndicators['SUPERTREND_CROSS'][i] = 1
        if dfIndicators['MACD_12_26_9'][i - 1] != "nan":
            if dfIndicators['MACD_12_26_9'][i - 1] <= dfIndicators['MACDs_12_26_9'][i - 1] and \
                    dfIndicators['MACD_12_26_9'][i] > dfIndicators['MACDs_12_26_9'][i]:
                dfIndicators['MACD_CROSS'][i] = 1
            if dfIndicators['MACD_12_26_9'][i - 1] >= dfIndicators['MACDs_12_26_9'][i - 1] and \
                    dfIndicators['MACD_12_26_9'][i] < dfIndicators['MACDs_12_26_9'][i]:
                dfIndicators['MACD_CROSS'][i] = -1
        if dfIndicators['close'][i - 1] <= dfIndicators['EMA_9'][i - 1] and dfIndicators['close'][i] > \
                dfIndicators['EMA_9'][i]:
            dfIndicators['EMA_CROSS'][i] = 1
        if dfIndicators['close'][i - 1] >= dfIndicators['EMA_9'][i - 1] and dfIndicators['close'][i] < \
                dfIndicators['EMA_9'][i]:
            dfIndicators['EMA_CROSS'][i] = 1
        if dfIndicators['RSI_14'][i] > 50:
            dfIndicators['RSI_CROSS'][i] = 1
        if dfIndicators['RSI_14'][i] < 40:
            dfIndicators['RSI_CROSS'][i] = -1
    return dfIndicators


def getNearbyoption(orderType, close, instument):
    today = datetime.date.today()
    if instument == "NIFTY" and orderType == "BUY":
        connection = connectMysql()
        cur = connection.cursor()
        nearest_strike_price = (close // 50) * 50
        higher_strike_price = ((close // 50) + 1) * 50
        cur.execute("SELECT * FROM indexopt_instrument_data WHERE tradingsymbol LIKE %s AND strike = %s",
                    ("NIFTY%ce", higher_strike_price))
        allInstrument = cur.fetchall()
        filtered_data = [d for d in allInstrument if d[6] >= today]
        sorted_data = sorted(filtered_data, key=lambda x: x[6])
        upcoming_contract = sorted_data[0]
        return upcoming_contract[3]
    if instument == "NIFTY" and orderType == "SELL":
        connection = connectMysql()
        cur = connection.cursor()
        nearest_strike_price = (close // 50) * 50
        higher_strike_price = ((close // 50) + 1) * 50
        cur.execute("SELECT * FROM indexopt_instrument_data WHERE tradingsymbol LIKE %s AND strike = %s",
                    ("NIFTY%pe", nearest_strike_price))
        allInstrument = cur.fetchall()
        filtered_data = [d for d in allInstrument if d[6] >= today]
        sorted_data = sorted(filtered_data, key=lambda x: x[6])
        upcoming_contract = sorted_data[0]
        return upcoming_contract[3]


    if instument == "BANKNIFTY" and orderType == "BUY":
        connection = connectMysql()
        cur = connection.cursor()
        nearest_strike_price = (close // 50) * 50
        higher_strike_price = ((close // 50) + 1) * 50
        cur.execute("SELECT * FROM indexopt_instrument_data WHERE tradingsymbol LIKE %s AND strike = %s",
                    ("BANKNIFTY%ce", higher_strike_price))
        allInstrument = cur.fetchall()
        filtered_data = [d for d in allInstrument if d[6] >= today]
        sorted_data = sorted(filtered_data, key=lambda x: x[6])
        upcoming_contract = sorted_data[0]
        return upcoming_contract[3]
    if instument == "BANKNIFTY" and orderType == "SELL":
        connection = connectMysql()
        cur = connection.cursor()
        nearest_strike_price = (close // 50) * 50
        higher_strike_price = ((close // 50) + 1) * 50
        cur.execute("SELECT * FROM indexopt_instrument_data WHERE tradingsymbol LIKE %s AND strike = %s",
                    ("BANKNIFTY%pe", nearest_strike_price))
        allInstrument = cur.fetchall()
        filtered_data = [d for d in allInstrument if d[6] >= today]
        sorted_data = sorted(filtered_data, key=lambda x: x[6])
        upcoming_contract = sorted_data[0]
        return upcoming_contract[3]


def placeOrderMockTrade(orderType, close, date,InstrumentType):
    socket_main = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_main.connect(('localhost', 9999))
    connection = connectMysql()
    cur = connection.cursor()
    cur.execute('SELECT * FROM positionsmock WHERE status = %s and orderType = %s', (1, orderType))
    existingPos = cur.fetchone()
    cur.close()
    if not existingPos:
        connection = connectMysql()
        cur = connection.cursor()
        cur.execute('INSERT INTO positionsmock (orderType,orderPrice,time,status) VALUES (%s,%s,%s,%s)',
                    (orderType, close, date, 1))
        cur.close()
        optionName = getNearbyoption(orderType, close, InstrumentType)
        socketTest(optionName, orderType)


def analyzeCrossOvers(crossOverIndicatorsDf,InstrumentType):
    print(InstrumentType)
    # observePositions(crossOverIndicatorsDf.iloc[-1].close)
    if datetime.datetime.now().minute % 5 == 0 and 10 < datetime.datetime.now().second < 20:
        if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == 1 and crossOverIndicatorsDf.iloc[-1].MACD_CROSS == 1:
            placeOrderMockTrade("BUY", crossOverIndicatorsDf.iloc[-1].close, crossOverIndicatorsDf.iloc[-1].date)
        elif crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == -1 and crossOverIndicatorsDf.iloc[-1].MACD_CROSS == -1:
            placeOrderMockTrade("SELL", crossOverIndicatorsDf.iloc[-1].close, crossOverIndicatorsDf.iloc[-1].date)
        else:
            if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == 1:
                for j in range(-1, -1 - 7, -1):
                    if crossOverIndicatorsDf.iloc[j].MACD_CROSS == 1:
                        placeOrderMockTrade("BUY", crossOverIndicatorsDf.iloc[-1].close,
                                            crossOverIndicatorsDf.iloc[-1].date,InstrumentType)
            if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == -1:
                for j in range(-1, -1 - 7, -1):
                    if crossOverIndicatorsDf.iloc[j].MACD_CROSS == -1:
                        placeOrderMockTrade("SELL", crossOverIndicatorsDf.iloc[-1].close,
                                            crossOverIndicatorsDf.iloc[-1].date,InstrumentType)


def getCurrnetExpiryToken(indextype):
    today = datetime.date.today()
    connection = connectMysql()
    cur = connection.cursor()
    cur.execute('SELECT * FROM indexfut_instrument_data')
    allInstrument = cur.fetchall()
    filtered_data = [d for d in allInstrument if d[6] >= today and d[3].startswith(indextype)]
    sorted_data = sorted(filtered_data, key=lambda x: x[6])
    upcoming_contract = sorted_data[0]
    return upcoming_contract[1]


instrumentTokenNiftyFut = getCurrnetExpiryToken('NIFTY')
instrumentTokenBankNiftyFut = getCurrnetExpiryToken('BANKNIFTY')

def observePositions(currentPrice):
    connection = connectMysql()
    cur = connection.cursor()
    cur.execute('SELECT * FROM positionsmock WHERE status = %s', 1)
    existingPos = cur.fetchone()
    cur.close()
    if existingPos:
        buyingPrice = float(existingPos[1]) - 1
        if existingPos[0] == "BUY" and currentPrice - buyingPrice > 30:
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute('UPDATE positionsmock SET status = %s WHERE time = %s', (2, existingPos[2]))
            cur.close()
            print("exit in profit")
        if existingPos[0] == "SELL" and buyingPrice - currentPrice > 30:
            print("exit in profit")
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute('UPDATE positionsmock SET status = %s WHERE time = %s', (2, existingPos[2]))
            cur.close()


def segrigateIndexNFOInstruments(nfoList):
    for instrument in nfoList:
        if instrument['tradingsymbol'].startswith('NIFTY') and instrument['tradingsymbol'].endswith('FUT'):
            print(instrument)
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(fut_insert_query, instrument)
            cur.close()
        elif instrument['tradingsymbol'].startswith('BANKNIFTY') and instrument['tradingsymbol'].endswith('FUT'):
            print(instrument)
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(fut_insert_query, instrument)
            cur.close()
        elif instrument['tradingsymbol'].startswith('NIFTY') and instrument['tradingsymbol'].endswith('CE'):
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(opt_insert_query, instrument)
            cur.close()
        elif instrument['tradingsymbol'].startswith('NIFTY') and instrument['tradingsymbol'].endswith('PE'):
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(opt_insert_query, instrument)
            cur.close()
        elif instrument['tradingsymbol'].startswith('BANKNIFTY') and instrument['tradingsymbol'].endswith('CE'):
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(opt_insert_query, instrument)
            cur.close()
        elif instrument['tradingsymbol'].startswith('BANKNIFTY') and instrument['tradingsymbol'].endswith('PE'):
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute(opt_insert_query, instrument)
            cur.close()
    pass


def socketTest(option, orderType):
    RECEIVER_ADDRESS = 'localhost'
    RECEIVER_PORT = 12345
    sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sender_socket.connect((RECEIVER_ADDRESS, RECEIVER_PORT))
    option = [
        {"type": "Future", "tradingsymbol": option, "transaction_type": orderType, "trigger_price": None,
         "squareoff": None, "stoploss": None},
        {"type": "Options", "tradingsymbol": option, "transaction_type": orderType, "trigger_price": None,
         "squareoff": None, "stoploss": None}]
    json_string = json.dumps(option)
    data = json_string.encode()
    sender_socket.sendall(data)
    sender_socket.close()


def analyzeNiftyFut():
    while True:
        # NIFTY HERE
        dfIndicators = calculateIndicators(getHistoricalData(instrumentTokenNiftyFut))
        crossOverIndicatorsDf = calculateIndicatorCrossOvers(dfIndicators)
        analyzeCrossOvers(crossOverIndicatorsDf, "NIFTY")
        # SLEEP NOW
        time.sleep(1)
        # BANKNIFTY HERE
        dfIndicators = calculateIndicators(getHistoricalData(instrumentTokenBankNiftyFut))
        crossOverIndicatorsDf = calculateIndicatorCrossOvers(dfIndicators)
        analyzeCrossOvers(crossOverIndicatorsDf, "BANKNIFTY")


def check_placeOrder_subprocessor():
    option = [{"type": "Options", "tradingsymbol": "ACC", "transaction_type": "SELL", "trigger_price": None,
         "squareoff": None, "stoploss": None}]
    json_string = json.dumps(option)
    print("------------Main program is calling middelwear to place order by providing the stock for trading-------------------")
    subprocess.Popen(['python', "placeOrder_middlewear.py", json_string])


def check_exitOrder_subprocessor():
    option = [{"type": "Options", "tradingsymbol": "ACC", "transaction_type": "SELL", "trigger_price": None,
               "squareoff": None, "stoploss": None}]
    json_string = json.dumps(option)
    print("------------Main program is calling middelwear to exit order by providing the stock for trading-------------------")
    subprocess.Popen(['python', "exitOrder_middlewear.py", json_string])


if __name__ == '__main__':
    # check_placeOrder_subprocessor()
    check_exitOrder_subprocessor()
    time.sleep(100)
    print("Done sleeping!")

    # analyzeNiftyFut()

