#!/usr/bin/python

class Tick(object):
    def __init__(self, data):
        self.timestamp = int(data['timestamp'])
        self.qty = int(data['qty'])
        self.price = convert_price(data['price'], False)
        self.id_num = data['id_num']

def convert_price(price, use_float):
    """
    Converts price to an integer representing a mil.
    1 mil = 0.0001
    Smallest representable size is 0.0001
    """
    if use_float:
        # Use floats to approximate prices instead of exact representation
        return int(float(price) * float(10000))
    else:
        # Exact representation
        idx = price.index('.')
        concat = "%s%s" % (price[0:idx], price[idx+1:].ljust(4,'0')[0:4])
        return int(concat)
        #from decimal import Decimal
        #return int(Decimal(price) * Decimal(10000))

class Trade(Tick):
    def __init__(self, data):
        super(Trade, self).__init__(data)

class Ask(Tick):
    def __init__(self, data):
        super(Ask, self).__init__(data)
        self.is_bid = False

class Bid(Tick):
    def __init__(self, data):
        super(Bid, self).__init__(data)
        self.is_bid = True
