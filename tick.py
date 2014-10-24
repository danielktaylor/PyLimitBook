#!/usr/bin/python


class Tick(object):
    def __init__(self, data):
        self.useFloat = True  # Use floats to approximate prices instead of Decimals
        self.timestamp = int(data['timestamp'])
        self.qty = int(data['qty'])
        self.price = self.convertPrice(data['price'])
        self.idNum = data['idNum']

    def convertPrice(self, price):
        """Converts price to an integer representing a mil.
        1 mil = 0.0001
        Smallest representable size is 0.0001
        """
        if self.useFloat:
            return int(float(price) * float(10000))
        else:
            # Exact representation
            from decimal import Decimal

            return int(Decimal(price) * Decimal(10000))


class Trade(Tick):
    def __init__(self, data):
        super(Trade, self).__init__(data)


class Ask(Tick):
    def __init__(self, data):
        super(Ask, self).__init__(data)
        self.isBid = False


class Bid(Tick):
    def __init__(self, data):
        super(Bid, self).__init__(data)
        self.isBid = True
