import pyotp
from kite_trade import *
import datetime
import pandas as pd
import pandas_ta as ta
import pymysql
import requests

pd.options.mode.chained_assignment = None

instrumentTokenNiftyFut = 8972290
instrumentTokenBankNiftyFut = 8972034

totpToken = "E6O4KPIAJ35QMZDLSEVUZL42MJUDHPFO"

kiteClientId = "XL0940"
kitePassword = "pooja@#123"

# Telegram cred
telegramToken = "5664182614:AAG6-knt9P9whHXgD6XD887yzf0cmB_oJwY"
chatId = "-1001871994988"


def connectMysql():
    connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
                                 autocommit=True, max_allowed_packet=67108864)
    #
    # connection = pymysql.connect(host='localhost', port=3306, user='root', password='password', db="sandybot32livemock",
    #                              autocommit=True, max_allowed_packet=67108864)

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


def placeOrderMockTrade(orderType, close, date):
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
        base_url = requests.get(
            "https://api.telegram.org/bot" + telegramToken + "/sendMessage?chat_id=" + chatId + "&text=" + orderType + " NIFTYFUT" +
            "\nat " + str(close) + "\nFor 30 points" + "\n" + str(date))
        print(
            "https://api.telegram.org/bot" + telegramToken + "/sendMessage?chat_id=" + chatId + "&text=" + orderType + " NIFTYFUT" +
            "\nat " + str(close) + "\nFor 30 points" + "\n" + str(date))
        print(base_url)


def analyzeCrossOvers(crossOverIndicatorsDf):
    observePositions(crossOverIndicatorsDf.iloc[-1].close)
    if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == 1 and crossOverIndicatorsDf.iloc[-1].MACD_CROSS == 1:
        placeOrderMockTrade("BUY", crossOverIndicatorsDf.iloc[-1].close, crossOverIndicatorsDf.iloc[-1].date)
    elif crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == -1 and crossOverIndicatorsDf.iloc[-1].MACD_CROSS == -1:
        placeOrderMockTrade("SELL", crossOverIndicatorsDf.iloc[-1].close, crossOverIndicatorsDf.iloc[-1].date)
    else:
        if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == 1:
            for j in range(-1, -1 - 7, -1):
                if crossOverIndicatorsDf.iloc[j].MACD_CROSS == 1:
                    placeOrderMockTrade("BUY", crossOverIndicatorsDf.iloc[-1].close,
                                        crossOverIndicatorsDf.iloc[-1].date)
        if crossOverIndicatorsDf.iloc[-1].SUPERTREND_CROSS == -1:
            for j in range(-1, -1 - 7, -1):
                if crossOverIndicatorsDf.iloc[j].MACD_CROSS == -1:
                    placeOrderMockTrade("SELL", crossOverIndicatorsDf.iloc[-1].close,
                                        crossOverIndicatorsDf.iloc[-1].date)


def analyzeNiftyFut():
    while True:
        dfIndicators = calculateIndicators(getHistoricalData(instrumentTokenNiftyFut))
        crossOverIndicatorsDf = calculateIndicatorCrossOvers(dfIndicators)
        crossOverIndicatorsDf.to_csv("NIFTY.csv")
        analyzeCrossOvers(crossOverIndicatorsDf)


def analyzeBankNiftyFut():
    dfIndicators = calculateIndicators(getHistoricalData(instrumentTokenBankNiftyFut))
    crossOverIndicatorsDf = calculateIndicatorCrossOvers(dfIndicators)
    crossOverIndicatorsDf.to_csv("BANKNIFTY.csv")


def observePositions(currentPrice):
    if datetime.datetime.now().minute % 5 == 0 and datetime.datetime.now().second < 10:
        print(currentPrice, datetime.datetime.now().minute)
        base_url = requests.get(
            "https://api.telegram.org/bot" + telegramToken + "/sendMessage?chat_id=" + chatId + "&text=" + str(
                currentPrice))
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
            base_url = requests.get(
                "https://api.telegram.org/bot" + telegramToken + "/sendMessage?chat_id=" + chatId + "&text=Target acheived")
            print(base_url)
        if existingPos[0] == "SELL" and buyingPrice - currentPrice > 30:
            print("exit in profit")
            connection = connectMysql()
            cur = connection.cursor()
            cur.execute('UPDATE positionsmock SET status = %s WHERE time = %s', (2, existingPos[2]))
            cur.close()
            base_url = requests.get(
                "https://api.telegram.org/bot" + telegramToken + "/sendMessage?chat_id=" + chatId + "&text=Target acheived")
            print(base_url)


if __name__ == '__main__':
    analyzeNiftyFut()
    # print(getNFOInstruments())
