#!/usr/bin/python

class Order(object):
    def __init__(self, tick, order_list):
        self.next_order = None
        self.prev_order = None
        self.tick = tick
        self.order_list = order_list

    def next_order(self):
        return self.next_order

    def prev_order(self):
        return self.prev_order

    def update_qty(self, new_qty, new_timestamp):
        if new_qty > self.qty and self.order_list.tail_order != self:
            # Move order to end of the tier (loses time priority)
            self.order_list.move_tail(self)
        self.order_list.volume -= self.qty - new_qty
        self.tick.timestamp = new_timestamp
        self.tick.qty = new_qty

    @property
    def id_num(self):
        return self.tick.id_num

    @property
    def qty(self):
        return self.tick.qty

    @property
    def price(self):
        return self.tick.price

    @property
    def is_bid(self):
        return self.tick.is_bid

    def __str__(self):
        return "%s\t@\t%.4f" % (self.qty, self.price / float(10000))
