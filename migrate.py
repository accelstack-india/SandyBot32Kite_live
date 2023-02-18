import pymysql


def connectMysql():
    # connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
    #                              autocommit=True, max_allowed_packet=67108864)
    #
    connection = pymysql.connect(host='localhost', port=3306, user='root', password='', db="sandybot32livemock",
                                 autocommit=True, max_allowed_packet=67108864)

    return connection


# Create a cursor object to execute queries
cursor = connectMysql().cursor()
# Define a query to create a table to store the instrument data
create_table_query = '''
CREATE TABLE indexFut_instrument_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instrument_token INT,
    exchange_token VARCHAR(255),
    tradingsymbol VARCHAR(255),
    name VARCHAR(255),
    last_price FLOAT,
    expiry DATE,
    strike FLOAT,
    tick_size FLOAT,
    lot_size INT,
    instrument_type VARCHAR(255),
    segment VARCHAR(255),
    exchange VARCHAR(255)
)
'''
cursor.execute(create_table_query)
cursor.close()


# Create a cursor object to execute queries
cursor = connectMysql().cursor()
# Define a query to create a table to store the instrument data
create_table_query = '''
CREATE TABLE indexOpt_instrument_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    instrument_token INT,
    exchange_token VARCHAR(255),
    tradingsymbol VARCHAR(255),
    name VARCHAR(255),
    last_price FLOAT,
    expiry DATE,
    strike FLOAT,
    tick_size FLOAT,
    lot_size INT,
    instrument_type VARCHAR(255),
    segment VARCHAR(255),
    exchange VARCHAR(255)
)
'''
cursor.execute(create_table_query)
cursor.close()
