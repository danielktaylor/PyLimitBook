#!/usr/bin/python


class Order(object):
    def __init__(self, tick, orderList):
        self.nextOrder = None
        self.prevOrder = None
        self.tick = tick
        self.orderList = orderList

    def nextOrder(self):
        return self.nextOrder

    def prevOrder(self):
        return self.prevOrder

    def updateQty(self, newQty, newTimestamp):
        if newQty > self.qty and self.orderList.tailOrder != self:
            # Move order to end of the tier (loses time priority)
            self.orderList.moveTail(self)
        self.orderList.volume -= self.qty - newQty
        self.tick.timestamp = newTimestamp
        self.tick.qty = newQty

    @property
    def idNum(self):
        return self.tick.idNum

    @property
    def qty(self):
        return self.tick.qty

    @property
    def price(self):
        return self.tick.price

    @property
    def isBid(self):
        return self.tick.isBid

    def __str__(self):
        return "%s\t@\t%.4f" % (self.qty, self.price / float(10000))
