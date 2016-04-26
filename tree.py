#!/usr/bin/python

from bintrees import FastRBTree

from orderList import OrderList
from order import Order


class Tree(object):
    def __init__(self):
        self.priceTree = FastRBTree()
        self.volume = 0
        self.priceMap = {}  # Map from price -> orderList object
        self.orderMap = {}  # Order ID to Order object
        self.minPrice = None
        self.maxPrice = None

    def __len__(self):
        return len(self.orderMap)

    def getPrice(self, price):
        return self.priceMap[price]

    def getOrder(self, idNum):
        return self.orderMap[idNum]

    def createPrice(self, price):
        newList = OrderList()
        self.priceTree.insert(price, newList)
        self.priceMap[price] = newList
        if self.maxPrice == None or price > self.maxPrice:
            self.maxPrice = price
        if self.minPrice == None or price < self.minPrice:
            self.minPrice = price

    def removePrice(self, price):
        self.priceTree.remove(price)
        del self.priceMap[price]

        if self.maxPrice == price:
            try:
                self.maxPrice = max(self.priceTree)
            except ValueError:
                self.maxPrice = None
        if self.minPrice == price:
            try:
                self.minPrice = min(self.priceTree)
            except ValueError:
                self.minPrice = None

    def priceExists(self, price):
        return price in self.priceMap

    def orderExists(self, idNum):
        return idNum in self.orderMap

    def insertTick(self, tick):
        if tick.price not in self.priceMap:
            self.createPrice(tick.price)
        order = Order(tick, self.priceMap[tick.price])
        self.priceMap[order.price].appendOrder(order)
        self.orderMap[order.idNum] = order
        self.volume += order.qty

    def updateOrder(self, tick):
        order = self.orderMap[tick.idNum]
        originalVolume = order.qty
        if tick.price != order.price:
            # Price changed
            orderList = self.priceMap[order.price]
            orderList.removeOrder(order)
            if len(orderList) == 0:
                self.removePrice(order.price)
            self.insertTick(tick)
        else:
            # Quantity changed
            order.updateQty(tick.qty, tick.price)
        self.volume += order.qty - originalVolume

    def removeOrderById(self, idNum):
        order = self.orderMap[idNum]
        self.volume -= order.qty
        order.orderList.removeOrder(order)
        if len(order.orderList) == 0:
            self.removePrice(order.price)
        del self.orderMap[idNum]

    def max(self):
        return self.maxPrice

    def min(self):
        return self.minPrice
