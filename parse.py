#!/usr/bin/python

import sys

from book import Book

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: %s input.csv" % sys.argv[0]
        sys.exit(0)
    try:
        reader = open(sys.argv[1], 'r')
        quotebook = Book()
        for line in reader:
            if line[0] == 'B':
                quotebook.bid(line.rstrip())
            elif line[0] == 'A':
                quotebook.ask(line.rstrip())
            else:
                quotebook.trade(line.rstrip())

            # Manual Debugging
            print "\n"
            print "Input: " + line
            print quotebook
            raw_input("Press enter to continue.")
        reader.close()
    except IOError:
        print 'Cannot open input file "%s"' % sys.argv[1]
        sys.exit(1)
