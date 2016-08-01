#!/usr/bin/python

import sys
import csv
from math import isnan

from pandas import *

from researchBook import ResearchBook

timeseries = {}

def append_point(quotebook):
    values = {}
    values['timestamp'] = quotebook.last_timestamp
    values['top_ask'] = quotebook.top_ask_price
    values['top_bid'] = quotebook.top_bid_price
    values['spread'] = quotebook.spread
    values['bid_volume'] = quotebook.bid_volume
    values['ask_volume'] = quotebook.ask_volume

    # Note: This will overwrite older values!
    global timeseries
    timeseries[quotebook.last_timestamp] = values

def sample(quotebook, output_file):
    # resample by seconds
    global timeseries
    sampled = Series(timeseries) \
        .reindex(range(quotebook.open_time, quotebook.close_time, 1000), \
                 method='backfill')

    with open(output_file, 'w') as infile:
        writer = csv.writer(infile)
        # write header
        writer.writerow(['sample_timestamp'] + \
                        sampled.get(quotebook.open_time).keys())
        # write values
        for index, values in sampled.iteritems():
            if type(values) == float and isnan(values):
                break
            writer.writerow([index] + values.values())

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "usage: %s input.csv output.csv" % sys.argv[0]
        sys.exit(0)
    try:
        reader = open(sys.argv[1], 'r')
        quotebook = ResearchBook()
        num_lines = 0  # Max lines to read in
        if num_lines > 0:
            print "Only reading in %i lines" % num_lines
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
        print 'Cannot open input file "%s"' % sys.argv[1]
        sys.exit(1)
