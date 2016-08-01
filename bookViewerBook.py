#!/usr/bin/python

from book import Book

class BookViewerBook(Book):
    def __init__(self):
        super(BookViewerBook, self).__init__()

    def bid_book_str(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------- Bids --------\n")
        if self.bids != None and len(self.bids) > 0:
            for k, v in self.bids.price_tree.items(reverse=True):
                file_str.write('%s' % v)
        return file_str.getvalue()

    def bid_book_aggregated_str(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------- Bids --------\n")
        if self.bids != None and len(self.bids) > 0:
            for k, v in self.bids.price_tree.items(reverse=True):
                # aggregate
                file_str.write("%s\t@\t%.4f\n" % \
                               (v.volume, v.head_order.price / float(10000)))
        return file_str.getvalue()

    def ask_book_str(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------- Asks --------\n")
        if self.asks != None and len(self.asks) > 0:
            for k, v in self.asks.price_tree.items():
                file_str.write('%s' % v)
        return file_str.getvalue()

    def ask_book_aggregated_str(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------- Asks --------\n")
        if self.asks != None and len(self.asks) > 0:
            for k, v in self.asks.price_tree.items():
                # aggregate
                file_str.write("%s\t@\t%.4f\n" % \
                               (v.volume, v.head_order.price / float(10000)))
        return file_str.getvalue()

    def trade_book_str(self):
        # Efficient string concat
        from cStringIO import StringIO

        file_str = StringIO()
        file_str.write("------ Trades ------\n")
        if self.trades != None and len(self.trades) > 0:
            num = 0
            for entry in self.trades:
                if num < 10:
                    file_str.write(str(entry.qty) + " @ " \
                                   + '%f' % (entry.price / float(10000)) \
                                   + " (" + str(entry.timestamp) + ")\n")
                    num += 1
                else:
                    break
        return file_str.getvalue()
