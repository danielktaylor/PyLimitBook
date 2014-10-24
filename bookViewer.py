#!/usr/bin/python

import sys
import traceback
import curses
import cPickle
from collections import deque

from bookViewerBook import BookViewerBook


class BookViewer(object):
    def __init__(self):
        self.help_text = ' n:Next  N:Prev  t:Play for time  T:Go to time  l:Play for lines  L:Play to line  a:Aggregate  .:Repeat'
        self.screen = None
        self.quotebook = BookViewerBook()
        self.max_reverse = 100
        self.quotebookHistory = deque(maxlen=self.max_reverse)
        self.infile = []
        self.currIndex = -1
        self.last_skipped = 0
        self.aggregate = False

        self.keys = {
        'EXIT': 113,  # q
        'REPEAT': 46,  # .
        'PREVIOUS': 78,  # N
        'NEXT': 110,  # n
        'PLAY_FOR_TIME': 116,  # t
        'PLAY_TO_TIME': 84,  # T
        'PLAY_FOR_LINES': 108,  # l
        'PLAY_TO_LINE': 76,  # L
        'AGGREGATE': 97,  # a
        'ESCAPE': 27,  # <ESC>
        }

    def reset(self):
        self.quotebook = BookViewerBook()
        self.quotebookHistory.clear()
        self.currIndex = -1

    def processLine(self, saveHistory=False):
        # Save the history
        if saveHistory:
            self.quotebookHistory.append(cPickle.dumps(self.quotebook, protocol=-1))
        else:
            self.quotebookHistory.clear()

        # Play line
        line = self.infile[self.currIndex + 1]
        if line[0] == 'B':
            self.quotebook.bid(line.rstrip())
        elif line[0] == 'A':
            self.quotebook.ask(line.rstrip())
        else:
            self.quotebook.trade(line.rstrip())

        self.currIndex += 1

    def reverseBook(self):
        if len(self.quotebookHistory) > 0:
            self.quotebook = cPickle.loads(self.quotebookHistory.pop())
            self.currIndex -= 1

    def readFile(self, filename):
        try:
            reader = open(sys.argv[1], 'r')
            for line in reader:
                self.infile.append(line)
        except IOError:
            print 'Cannot open input file: %s' % filename
            sys.exit(1)

    def playLines(self, number):
        targetIndex = self.currIndex + number
        if targetIndex > self.currIndex:
            maxIndex = targetIndex if targetIndex < len(self.infile) else len(self.infile) - 1
            while self.currIndex < maxIndex:
                if maxIndex - self.currIndex <= self.max_reverse:
                    self.processLine(saveHistory=True)
                else:
                    self.processLine(saveHistory=False)
        elif targetIndex < self.currIndex and targetIndex >= 0:
            # Negative lines
            reverseLines = self.currIndex - targetIndex
            while reverseLines > 0 and len(self.quotebookHistory) > 0:
                self.reverseBook()
                reverseLines -= 1

    def playToLine(self, line):
        # subtract 1 because lines start at 1 not 0
        self.playLines(line - self.currIndex - 1)

    def playTime(self, time):
        targetTime = self.quotebook.lastTimestamp + time
        if targetTime >= self.quotebook.lastTimestamp:
            while self.quotebook.lastTimestamp < targetTime and \
                            len(self.infile) > self.currIndex + 1:
                if targetTime - self.quotebook.lastTimestamp <= 5000 \
                        or self.currIndex > len(self.infile) - self.max_reverse:
                    self.processLine(saveHistory=True)
                else:
                    self.processLine(saveHistory=False)
        elif targetTime < self.quotebook.lastTimestamp and targetTime >= 0:
            # Reverse time
            while self.quotebook.lastTimestamp > targetTime \
                    and len(self.quotebookHistory) > 0:
                self.reverseBook()
            if self.quotebook.lastTimestamp > targetTime and self.currIndex > 0:
                # Play up to the line
                self.reset()
                self.playTime(targetTime)

    def playToTime(self, time):
        self.playTime(time - self.quotebook.lastTimestamp)

    def getIntValue(self, message):
        dimensions = self.screen.getmaxyx()
        if len(message) < dimensions[1]:
            empty = dimensions[1] - len(message) - 2
            self.screen.addstr(dimensions[0] - 2, len(message) + 1, \
                               " " * empty, curses.A_STANDOUT)
        self.screen.addstr(dimensions[0] - 2, 1, message, curses.A_STANDOUT)
        curses.curs_set(1);
        curses.echo()  # show cursor
        value = self.screen.getstr()
        self.drawHelp()
        curses.curs_set(0);
        curses.noecho()
        try:
            return int(value)
        except ValueError:
            return None

    def processKey(self, character):
        if character == self.keys['PREVIOUS']:
            self.playLines(-1)
        elif character == self.keys['NEXT']:
            self.playLines(1)
        elif character == self.keys['PLAY_FOR_TIME']:
            value = self.getIntValue('Milliseconds: ')
            if value != None:
                self.last_skipped = value
                self.playTime(value)
        elif character == self.keys['PLAY_TO_TIME']:
            value = self.getIntValue('Milliseconds: ')
            if value != None:
                self.playToTime(value)
        elif character == self.keys['PLAY_FOR_LINES']:
            value = self.getIntValue('Lines: ')
            if value != None:
                self.last_skipped = value
                self.playLines(value)
        elif character == self.keys['PLAY_TO_LINE']:
            value = self.getIntValue('Line: ')
            if value != None:
                self.playToLine(value)
        elif character == self.keys['AGGREGATE']:
            # Toggle tier aggregation
            self.aggregate = True if self.aggregate == False else False

    def drawBook(self):
        dimensions = self.screen.getmaxyx()
        length = dimensions[0] - 5
        width = (dimensions[1] - 3) / 3

        # Bids
        bidWin = curses.newwin(length, width, 3, 2)
        book = ''
        if self.aggregate:
            book = self.quotebook.bidBookAggregatedStr().split('\n')
        else:
            book = self.quotebook.bidBookStr().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                bidWin.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                bidWin.addstr(idx, 1, line)
        bidWin.refresh()

        # Asks
        askWin = curses.newwin(length, width, 3, 3 + width)
        book = ''
        if self.aggregate:
            book = self.quotebook.askBookAggregatedStr().split('\n')
        else:
            book = self.quotebook.askBookStr().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                askWin.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                askWin.addstr(idx, 1, line)
        askWin.refresh()

        # Trades
        tradeWin = curses.newwin(length, width, 3, 3 + (width * 2) - 1)
        book = self.quotebook.tradeBookStr().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                tradeWin.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                tradeWin.addstr(idx, 1, line)
        tradeWin.refresh()

    def drawHelp(self):
        dimensions = self.screen.getmaxyx()
        self.screen.addstr(dimensions[0] - 2, 1, self.help_text, curses.A_STANDOUT)
        if len(self.help_text) < self.screen.getmaxyx()[1] - 4:
            empty = self.screen.getmaxyx()[1] - len(self.help_text) - 3
            self.screen.addstr(dimensions[0] - 2, len(self.help_text) + 1, " " * empty, \
                               curses.A_STANDOUT)

    def drawScreen(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.refresh()
        self.drawHelp()

    def main(self, stdscr):
        # Draw the shortcut key bar
        self.screen = stdscr
        self.drawScreen()

        # Read the file
        self.readFile(sys.argv[1])
        self.playLines(1)

        exit = False
        last_pressed = None
        while not exit:
            self.drawBook()

            # Print current line
            line = self.infile[self.currIndex].rstrip() + ' (line ' \
                   + str(self.currIndex + 1) + ')'
            if self.aggregate:
                line += '  [AGGREGATED VIEW]'
            dimensions = self.screen.getmaxyx()
            if len(line) < dimensions[1] - 4:
                empty = dimensions[1] - len(line) - 10
                line += (" " * empty)
            self.screen.addstr(1, 3, line.replace(',', ', '))

            # Refresh the screen
            self.screen.refresh()
            character = self.screen.getch()

            if character == curses.KEY_RESIZE:
                # Window resize
                self.drawScreen()
                self.drawBook()
            elif character == self.keys['REPEAT'] and last_pressed != None:
                if last_pressed == self.keys['PLAY_FOR_LINES']:
                    self.playLines(self.last_skipped)
                elif last_pressed == self.keys['PLAY_FOR_TIME']:
                    self.playTime(self.last_skipped)
                else:
                    self.processKey(last_pressed)
            elif character == self.keys['EXIT']:
                exit = True
            else:
                last_pressed = character
                self.processKey(character)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: %s input.csv" % sys.argv[0]
        sys.exit(0)

    try:
        # Initiate window
        stdscr = curses.initscr()
        curses.noecho()  # hide cursor

        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho();
        curses.cbreak()
        curses.curs_set(0)  # Hide cursor

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        bookViewer = BookViewer()
        bookViewer.main(stdscr)  # Enter the main loop

        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo();
        curses.nocbreak()
        curses.endwin()  # Terminate curses
    except KeyboardInterrupt:
        # ctrl-c
        stdscr.keypad(0)
        curses.echo();
        curses.nocbreak()
        curses.endwin()
    except:
        # In the event of an error, restore the terminal
        # to a sane state.
        stdscr.keypad(0)
        curses.echo();
        curses.nocbreak()
        curses.endwin()
        traceback.print_exc()  # Print the exception
