#!/usr/bin/python

from collections import deque

from tick import Bid, Ask, Trade
from tree import Tree


def parseCsv(columns, line):
    """
    Parse a CSV line that has ',' as a separator.
    Columns is a list of the column names, must match the number of
    comma-separated values in the input line.
    """
    data = {}
    split = line.split(',')
    for idx, name in enumerate(columns):
        data[name] = split[idx]
    return data


class Book(object):
    def __init__(self):
        self.trades = deque(maxlen=100)  # Index [0] is most recent trade
        self.bids = Tree()
        self.asks = Tree()
        self.lastTick = None
        self.lastTimestamp = 0

    def processBidAsk(self, tick):
        """
        Generic method to process bid or ask.
        """
        tree = self.asks
        if tick.isBid:
            tree = self.bids
        if tick.qty == 0:
            # Quantity is zero -> remove the entry
            tree.removeOrderById(tick.idNum)
        else:
            if tree.orderExists(tick.idNum):
                tree.updateOrder(tick)
            else:
                # New order
                tree.insertTick(tick)

    def bid(self, tick):
        columns = ['event', 'symbol', 'exchange', 'idNum', 'qty', 'price', 'timestamp']
        data = parseCsv(columns, tick)
        bid = Bid(data)
        if bid.timestamp > self.lastTimestamp:
            self.lastTimestamp = bid.timestamp
        self.lastTick = bid
        self.processBidAsk(bid)

    def ask(self, tick):
        columns = ['event', 'symbol', 'exchange', 'idNum', 'qty', 'price', 'timestamp']
        data = parseCsv(columns, tick)
        ask = Ask(data)
        if ask.timestamp > self.lastTimestamp:
            self.lastTimestamp = ask.timestamp
        self.lastTick = ask
        self.processBidAsk(ask)

    def trade(self, tick):
        columns = ['event', 'symbol', 'exchange', 'qty', 'price', 'timestamp']
        data = parseCsv(columns, tick)
        data['idNum'] = 0
        trade = Trade(data)
        if trade.timestamp > self.lastTimestamp:
            self.lastTimestamp = trade.timestamp
        self.lastTick = trade
        self.trades.appendleft(trade)

    def __str__(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------ Bids -------\n")
        if self.bids != None and len(self.bids) > 0:
            for k, v in self.bids.priceTree.items(reverse=True):
                file_str.write('%s' % v)
        file_str.write("\n------ Asks -------\n")
        if self.asks != None and len(self.asks) > 0:
            for k, v in self.asks.priceTree.items():
                file_str.write('%s' % v)
        file_str.write("\n------ Trades ------\n")
        if self.trades != None and len(self.trades) > 0:
            num = 0
            for entry in self.trades:
                if num < 5:
                    file_str.write(str(entry.qty) + " @ " \
                                   + str(entry.price / 10000) \
                                   + " (" + str(entry.timestamp) + ")\n")
                    num += 1
                else:
                    break
        file_str.write("\n")
        return file_str.getvalue()
