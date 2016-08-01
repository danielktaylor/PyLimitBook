#!/usr/bin/python

import sys, os

# Sample:
#
# T, XOM, 0, 70.63000, , BATS, 0
# B, XOM, 683566, 0, 70.48, , BATS, 31212660, 89
# A, XOM, 816267, 100, 70.8200, , BATS, 31340326, 89
#
# Input filenames:
#
# XOM_2010-02-25
# XOM_BATS_2010-07-16

def parse_csv(columns, line):
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
    columns = ['event', 'symbol', 'id_num', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp', 'flags']
    data = parse_csv(columns, tick)
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['id_num'], data['qty'], data['price'], data['timestamp']]))


def ask(tick):
    columns = ['event', 'symbol', 'id_num', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp', 'flags']
    data = parse_csv(columns, tick)
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['id_num'], data['qty'], data['price'], data['timestamp']]))


def trade(tick):
    columns = ['event', 'symbol', 'qty', 'price', 'garbage', \
               'exchange', 'timestamp']
    data = parse_csv(columns, tick)
    data['id_num'] = ""
    return ','.join(list([data['event'], data['symbol'], data['exchange'], \
                          data['id_num'], data['qty'], data['price'], data['timestamp']]))

def get_filename(infile):
  # XOM_2010-02-25
  # XOM_BATS_2010-07-16
  parts = os.path.basename(infile).split("_")
  if len(parts) == 2:
    symbol = parts[0]
    date = parts[1]
    exchange = "BATS"
  elif len(parts) == 3:
    symbol = parts[0]
    date = parts[2]
    exchange = parts[1]
  converted = "%s_%s_%s.csv" % (symbol, exchange, date)
  return os.path.join(os.path.dirname(infile), converted)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: %s input_file" % sys.argv[0]
        sys.exit(0)
    try:
        reader = open(sys.argv[1], 'r')

        outfile = get_filename(sys.argv[1])
        writer = open(outfile, 'w')
        for line in reader:
            if line[0] == 'B':
                writer.write(bid(line.rstrip().replace('1.0E-4','0.0001')) + '\n')
            elif line[0] == 'A':
                writer.write(ask(line.rstrip().replace('1.0E-4','0.0001')) + '\n')
            else:
                writer.write(trade(line.rstrip().replace('1.0E-4','0.0001')) + '\n')
        reader.close()
        writer.close()
    except IOError:
        print 'Cannot open input file "%s"' % sys.argv[1]
        sys.exit(1)
