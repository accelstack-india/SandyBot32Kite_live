fut_insert_query = '''
INSERT INTO indexFut_instrument_data (
    instrument_token,
    exchange_token,
    tradingsymbol,
    name,
    last_price,
    expiry,
    strike,
    tick_size,
    lot_size,
    instrument_type,
    segment,
    exchange
) VALUES (
    %(instrument_token)s,
    %(exchange_token)s,
    %(tradingsymbol)s,
    %(name)s,
    %(last_price)s,
    %(expiry)s,
    %(strike)s,
    %(tick_size)s,
    %(lot_size)s,
    %(instrument_type)s,
    %(segment)s,
    %(exchange)s
)
'''



opt_insert_query = '''
INSERT INTO indexOpt_instrument_data (
    instrument_token,
    exchange_token,
    tradingsymbol,
    name,
    last_price,
    expiry,
    strike,
    tick_size,
    lot_size,
    instrument_type,
    segment,
    exchange
) VALUES (
    %(instrument_token)s,
    %(exchange_token)s,
    %(tradingsymbol)s,
    %(name)s,
    %(last_price)s,
    %(expiry)s,
    %(strike)s,
    %(tick_size)s,
    %(lot_size)s,
    %(instrument_type)s,
    %(segment)s,
    %(exchange)s
)
'''



