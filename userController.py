import pymysql


def connectMysql():
    # connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
    #                              autocommit=True, max_allowed_packet=67108864)
    #
    connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="upgrow",
                                 autocommit=True, max_allowed_packet=67108864)

    return connection


class userController:
    @classmethod
    def get_OptionalTradeUsers(cls,tradeSegment):

        connection = connectMysql()
        cur = connection.cursor()
        cur.execute(
            'SELECT * FROM user_broker_details INNER JOIN subscriptions ON subscriptions.user_id = user_broker_details.user_id AND subscriptions.status = %s INNER JOIN subscription_plans ON subscription_plans.plan_id = subscriptions.subscription_id AND subscription_plans.plan_category = %s',
            ("Active", tradeSegment))
        accounts = cur.fetchall()
        cur.close()
        usersList = []
        for account in accounts:
            usersList.append(
                {
                    "user_id": account[0],
                    "totpToken": account[5],
                    "kiteClientId": account[3],
                    "kitePassword": account[4],
                }
            )
        return usersList