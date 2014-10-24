#!/usr/bin/python

import sys
import csv
from math import isnan

from pandas import *

from researchBook import ResearchBook


timeseries = {}


def appendPoint(quotebook):
    values = {}
    values['timestamp'] = quotebook.lastTimestamp
    values['top_ask'] = quotebook.topAskPrice
    values['top_bid'] = quotebook.topBidPrice
    values['spread'] = quotebook.spread
    values['bid_volume'] = quotebook.bidVolume
    values['ask_volume'] = quotebook.askVolume

    # Note: This will overwrite older values!
    global timeseries
    timeseries[quotebook.lastTimestamp] = values


def sample(quotebook, output_file):
    # resample by seconds
    global timeseries
    sampled = Series(timeseries) \
        .reindex(range(quotebook.openTime, quotebook.closeTime, 1000), \
                 method='backfill')

    with open(output_file, 'w') as infile:
        writer = csv.writer(infile)
        # write header
        writer.writerow(['sample_timestamp'] + \
                        sampled.get(quotebook.openTime).keys())
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
        numLines = 0  # Max lines to read in
        if numLines > 0:
            print "Only reading in %i lines" % numLines
        else:
            numLines = -1
        for line in reader:
            if numLines >= 0:
                if numLines == 0:
                    break
                else:
                    numLines -= 1
            # Process bid/ask/trade
            if line[0] == 'B':
                quotebook.bid(line.rstrip())
            elif line[0] == 'A':
                quotebook.ask(line.rstrip())
            else:
                quotebook.trade(line.rstrip())
            # Append datapoint
            if quotebook.isMarketOpen():
                appendPoint(quotebook)
        reader.close()
        sample(quotebook, sys.argv[2])
    except IOError:
        print 'Cannot open input file "%s"' % sys.argv[1]
        sys.exit(1)
