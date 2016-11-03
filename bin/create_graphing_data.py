#!/usr/bin/python

'''
This script takes in a level II data file and outputs a CSV of
best bid/ask and some other data. This is useful for graphing
the state of the book. It's easy to add more data points to the file.
'''

import sys
import csv
from math import isnan

from pylimitbook.researchBook import ResearchBook

CREATE_ON_NBBO_CHANGE_ONLY = True # only output generate lines if the top of the book changes?
timeseries = []

def convert_time(t):
    x = t / 1000
    ms = t % x
    seconds = x % 60
    x = x/60
    minutes = x % 60
    x = x / 60
    hours = x % 24
    formatted = "%02d:%02d:%02d.%03d" % (hours, minutes, seconds, ms)
    return formatted

def append_point(quotebook):
    values = {}
    values['timestamp'] = convert_time(quotebook.last_timestamp)
    values['top_bid'] = quotebook.top_bid_price / 10000.0
    values['top_ask'] = quotebook.top_ask_price / 10000.0
    values['spread'] = quotebook.spread / 10000.0
    values['bid_volume'] = quotebook.bid_volume
    values['ask_volume'] = quotebook.ask_volume

    global timeseries
    timeseries.append(values)

def sample(quotebook, output_file):
    global timeseries, CREATE_ON_NBBO_CHANGE_ONLY
    with open(output_file, 'w') as infile:
        writer = csv.writer(infile)
        # write header
        writer.writerow(['timestamp','top_bid','top_ask','spread','bid_volume','ask_volume'])

        # write values
        previous = None
        for data in timeseries:
            if previous != None and CREATE_ON_NBBO_CHANGE_ONLY and \
                    previous['top_bid'] == data['top_bid'] and \
                    previous['top_ask'] == data['top_ask']:
                continue
            x = []
            x.append(data['timestamp'])
            x.append(data['top_bid'])
            x.append(data['top_ask'])
            x.append(data['spread'])
            x.append(data['bid_volume'])
            x.append(data['ask_volume'])
            writer.writerow(x)
            previous = data

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("usage: %s input.csv output.csv" % sys.argv[0])
        sys.exit(0)
    try:
        reader = open(sys.argv[1], 'r')
        quotebook = ResearchBook()
        num_lines = 0  # Max lines to read in
        if num_lines > 0:
            print("Only reading in %i lines" % num_lines)
        else:
            num_lines = -1
        for line in reader:
            if num_lines >= 0:
                if num_lines == 0:
                    break
                else:
                    num_lines -= 1
            # Process bid/ask/trade
            if line[0] == 'B':
                quotebook.bid(line.rstrip())
            elif line[0] == 'A':
                quotebook.ask(line.rstrip())
            else:
                quotebook.trade(line.rstrip())
            # Append datapoint
            if quotebook.is_market_open():
                append_point(quotebook)
        reader.close()
        sample(quotebook, sys.argv[2])
    except IOError:
        print ('Cannot open input file "%s"' % sys.argv[1])
        sys.exit(1)
