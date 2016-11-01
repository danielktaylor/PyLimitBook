#!/usr/bin/python

import sys
import traceback
import curses
from six.moves import cPickle
from collections import deque

from bookViewerBook import BookViewerBook

class BookViewer(object):
    def __init__(self):
        self.help_text = ' n:Next  N:Prev  t:Play for time  T:Go to time  l:Play for lines  L:Play to line  a:Aggregate  .:Repeat'
        self.screen = None
        self.quotebook = BookViewerBook()
        self.max_reverse = 100
        self.quotebook_history = deque(maxlen=self.max_reverse)
        self.infile = []
        self.curr_index = -1
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
        self.quotebook_history.clear()
        self.curr_index = -1

    def process_line(self, save_history=False):
        # Save the history
        if save_history:
            self.quotebook_history.append(cPickle.dumps(self.quotebook, protocol=-1))
        else:
            self.quotebook_history.clear()

        # Play line
        line = self.infile[self.curr_index + 1]
        if line[0] == 'B':
            self.quotebook.bid(line.rstrip())
        elif line[0] == 'A':
            self.quotebook.ask(line.rstrip())
        else:
            self.quotebook.trade(line.rstrip())

        self.curr_index += 1

    def reverse_book(self):
        if len(self.quotebook_history) > 0:
            self.quotebook = cPickle.loads(self.quotebook_history.pop())
            self.curr_index -= 1

    def read_file(self, filename):
        try:
            reader = open(sys.argv[1], 'r')
            for line in reader:
                self.infile.append(line)
        except IOError:
            print('Cannot open input file: %s' % filename)
            sys.exit(1)

    def play_lines(self, number):
        target_index = self.curr_index + number
        if target_index > self.curr_index:
            max_index = target_index if target_index < len(self.infile) else len(self.infile) - 1
            while self.curr_index < max_index:
                if max_index - self.curr_index <= self.max_reverse:
                    self.process_line(save_history=True)
                else:
                    self.process_line(save_history=False)
        elif target_index < self.curr_index and target_index >= 0:
            # Negative lines
            reverse_lines = self.curr_index - target_index
            while reverse_lines > 0 and len(self.quotebook_history) > 0:
                self.reverse_book()
                reverse_lines -= 1

    def play_to_line(self, line):
        # subtract 1 because lines start at 1 not 0
        self.play_lines(line - self.curr_index - 1)

    def play_time(self, time):
        target_time = self.quotebook.last_timestamp + time
        if target_time >= self.quotebook.last_timestamp:
            while self.quotebook.last_timestamp < target_time and \
                            len(self.infile) > self.curr_index + 1:
                if target_time - self.quotebook.last_timestamp <= 5000 \
                        or self.curr_index > len(self.infile) - self.max_reverse:
                    self.process_line(save_history=True)
                else:
                    self.process_line(save_history=False)
        elif target_time < self.quotebook.last_timestamp and target_time >= 0:
            # Reverse time
            while self.quotebook.last_timestamp > target_time \
                    and len(self.quotebook_history) > 0:
                self.reverse_book()
            if self.quotebook.last_timestamp > target_time and self.curr_index > 0:
                # Play up to the line
                self.reset()
                self.play_time(target_time)

    def play_to_time(self, time):
        self.play_time(time - self.quotebook.last_timestamp)

    def get_int_value(self, message):
        dimensions = self.screen.getmaxyx()
        if len(message) < dimensions[1]:
            empty = dimensions[1] - len(message) - 2
            self.screen.addstr(dimensions[0] - 2, len(message) + 1, \
                               " " * empty, curses.A_STANDOUT)
        self.screen.addstr(dimensions[0] - 2, 1, message, curses.A_STANDOUT)
        curses.curs_set(1);
        curses.echo()  # show cursor
        value = self.screen.getstr()
        self.draw_help()
        curses.curs_set(0);
        curses.noecho()
        try:
            return int(value)
        except ValueError:
            return None

    def process_key(self, character):
        if character == self.keys['PREVIOUS']:
            self.play_lines(-1)
        elif character == self.keys['NEXT']:
            self.play_lines(1)
        elif character == self.keys['PLAY_FOR_TIME']:
            value = self.get_int_value('Milliseconds: ')
            if value != None:
                self.last_skipped = value
                self.play_time(value)
        elif character == self.keys['PLAY_TO_TIME']:
            value = self.get_int_value('Milliseconds: ')
            if value != None:
                self.play_to_time(value)
        elif character == self.keys['PLAY_FOR_LINES']:
            value = self.get_int_value('Lines: ')
            if value != None:
                self.last_skipped = value
                self.play_lines(value)
        elif character == self.keys['PLAY_TO_LINE']:
            value = self.get_int_value('Line: ')
            if value != None:
                self.play_to_line(value)
        elif character == self.keys['AGGREGATE']:
            # Toggle tier aggregation
            self.aggregate = True if self.aggregate == False else False

    def draw_book(self):
        dimensions = self.screen.getmaxyx()
        length = int(dimensions[0] - 5)
        width = int((dimensions[1] - 3) / 3)

        # Bids
        bid_win = curses.newwin(length, width, 3, 2)
        book = ''
        if self.aggregate:
            book = self.quotebook.bid_book_aggregated_str().split('\n')
        else:
            book = self.quotebook.bid_book_str().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                bid_win.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                bid_win.addstr(idx, 1, line)
        bid_win.refresh()

        # Asks
        ask_win = curses.newwin(length, width, 3, 3 + width)
        book = ''
        if self.aggregate:
            book = self.quotebook.ask_book_aggregated_str().split('\n')
        else:
            book = self.quotebook.ask_book_str().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                ask_win.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                ask_win.addstr(idx, 1, line)
        ask_win.refresh()

        # Trades
        trade_win = curses.newwin(length, width, 3, 3 + (width * 2) - 1)
        book = self.quotebook.trade_book_str().split('\n')
        for idx, line in enumerate(book):
            if idx == 0:
                trade_win.addstr(idx, 1, line, curses.A_STANDOUT)
            elif idx == length:
                break
            else:
                trade_win.addstr(idx, 1, line)
        trade_win.refresh()

    def draw_help(self):
        dimensions = self.screen.getmaxyx()
        self.screen.addstr(dimensions[0] - 2, 1, self.help_text, curses.A_STANDOUT)
        if len(self.help_text) < self.screen.getmaxyx()[1] - 4:
            empty = self.screen.getmaxyx()[1] - len(self.help_text) - 3
            self.screen.addstr(dimensions[0] - 2, len(self.help_text) + 1, " " * empty, \
                               curses.A_STANDOUT)

    def draw_screen(self):
        self.screen.clear()
        self.screen.border(0)
        self.screen.refresh()
        self.draw_help()

    def main(self, stdscr):
        # Draw the shortcut key bar
        self.screen = stdscr
        self.draw_screen()

        # Read the file
        self.read_file(sys.argv[1])
        self.play_lines(1)

        exit = False
        last_pressed = None
        while not exit:
            self.draw_book()

            # Print current line
            line = self.infile[self.curr_index].rstrip() + ' (line ' \
                   + str(self.curr_index + 1) + ')'
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
                self.draw_screen()
                self.draw_book()
            elif character == self.keys['REPEAT'] and last_pressed != None:
                if last_pressed == self.keys['PLAY_FOR_LINES']:
                    self.play_lines(self.last_skipped)
                elif last_pressed == self.keys['PLAY_FOR_TIME']:
                    self.play_time(self.last_skipped)
                else:
                    self.process_key(last_pressed)
            elif character == self.keys['EXIT']:
                exit = True
            else:
                last_pressed = character
                self.process_key(character)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: %s input.csv" % sys.argv[0])
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
