#!/usr/bin/python

from pylimitbook.order import Order

class OrderList(object):
    def __init__(self):
        self.head_order = None
        self.tail_order = None
        self.length = 0
        self.volume = 0  # Total share volume
        self.last = None

    def __len__(self):
        return self.length

    def __iter__(self):
        self.last = self.head_order
        return self

    def next(self):
        if self.last == None:
            raise StopIteration
        else:
            return_val = self.last
            self.last = self.last.next_order
            return return_val

    __next__ = next # Python 3.x compatibility

    def append_order(self, order):
        """
        :param order:
        :type order: Order
        :return:
        """
        if len(self) == 0:
            order.next_order = None
            order.prev_order = None
            self.head_order = order
            self.tail_order = order
        else:
            order.prev_order = self.tail_order
            order.next_order = None
            self.tail_order.next_order = order
            self.tail_order = order
        self.length += 1
        self.volume += order.qty

    def remove_order(self, order):
        self.volume -= order.qty
        self.length -= 1
        if len(self) == 0:
            return
        # Remove from list of orders
        next_order = order.next_order
        prev_order = order.prev_order
        if next_order != None and prev_order != None:
            next_order.prev_order = prev_order
            prev_order.next_order = next_order
        elif next_order != None:
            next_order.prev_order = None
            self.head_order = next_order
        elif prev_order != None:
            prev_order.next_order = None
            self.tail_order = prev_order

    def move_tail(self, order):
        if order.prev_order != None:
            order.prev_order.next_order = self.next_order
        else:
            # Update the head order
            self.head_order = order.next_order
        order.next_order.prev_order = order.prev_order
        # Set the previous tail order's next order to this order
        self.tail_order.next_order = order
        self.tail_order = order
        order.prev_order = self.tail_order
        order.next_order = None

    def __str__(self):
        from six.moves import cStringIO as StringIO

        file_str = StringIO()
        for order in self:
            file_str.write("%s\n" % str(order))
        return file_str.getvalue()
