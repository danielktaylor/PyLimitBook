#!/usr/bin/python

import sys

# Sample:
#
# T, XOM, 0, 70.63000, , BATS, 0
# B, XOM, 683566, 0, 70.48, , BATS, 31212660, 89
# A, XOM, 816267, 100, 70.8200, , BATS, 31340326, 89
#

def parseCsv(columns, line):
    '''
    Parse a CSV line that has ', ' as a separator.
    Columns is a list of the column names, must match the number of
    comma-separated values in the input line.
    '''
    data = {}
    index = 0
    for name in columns:
        value = ''
        for char in line[index:]:
            if char == ',':
                index += 1
                break
            value += char
            index += 1
        index += 1
        data[name] = value
    return data


def bid(tick):
    columns = ['event', 'symbol', 'idNum', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp', 'flags']
    data = parseCsv(columns, tick)
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['idNum'], data['qty'], data['price'], data['timestamp']]))


def ask(tick):
    columns = ['event', 'symbol', 'idNum', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp', 'flags']
    data = parseCsv(columns, tick)
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['idNum'], data['qty'], data['price'], data['timestamp']]))


def trade(tick):
    columns = ['event', 'symbol', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp']
    data = parseCsv(columns, tick)
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['qty'], data['price'], data['timestamp']]))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: %s input.csv output.csv" % sys.argv[0]
        sys.exit(0)
    try:
        reader = open(sys.argv[1], 'r')
        writer = open(sys.argv[2], 'w')
        for line in reader:
            if line[0] == 'B':
                writer.write(bid(line.rstrip()) + '\n')
            elif line[0] == 'A':
                writer.write(ask(line.rstrip()) + '\n')
            else:
                writer.write(trade(line.rstrip()) + '\n')
        reader.close()
        writer.close()
    except IOError:
        print 'Cannot open input file "%s"' % sys.argv[1]
        sys.exit(1)
