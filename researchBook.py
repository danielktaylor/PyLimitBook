#!/usr/bin/python

from book import Book


class ResearchBook(Book):
    def __init__(self):
        super(ResearchBook, self).__init__()
        self.openTime = 34200000  # 9:30 am
        self.closeTime = 57600000  # 4:00 pm

    def bid(self, bid):
        super(ResearchBook, self).bid(bid)

    def ask(self, ask):
        super(ResearchBook, self).ask(ask)

    def trade(self, trade):
        super(ResearchBook, self).trade(trade)

    def isMarketOpen(self):
        if self.lastTimestamp >= self.openTime and \
                        self.lastTimestamp < self.closeTime:
            return True
        else:
            return False

    @property
    def topBidPrice(self):
        if len(self.bids) == 0:
            return 0
        return max(self.bids.priceTree)

    @property
    def topAskPrice(self):
        if len(self.asks) == 0:
            return 0
        return min(self.asks.priceTree)

    @property
    def bidVolume(self):
        return self.bids.volume

    @property
    def askVolume(self):
        return self.asks.volume

    @property
    def spread(self):
        spread = self.topAskPrice - self.topBidPrice
        return spread if spread > 0 else 0
