import curses
from curses import wrapper
import json
import logging
import os
import random
import time

class Application:
    _config = None
    def __init__(self, config_filename):
        with open(config_filename) as f:
            self._config = json.loads(f.read())

    def pick_file(self):
        files = list()
        with open("filenames") as f:
            for line in f:
                files.append(line)
        n = random.randint(0, len(files))
        return files[n].strip()

    def get_text(self):
        text_size_lines = self._config["text_size_lines"]

        filename = self.pick_file()
        logging.info(f"opening {filename}")
        with open(filename) as f:
            lines = f.readlines()
        start = random.randint(0, len(lines) - text_size_lines)
        end = start + min(text_size_lines, len(lines) - start)
        logging.info(f"start {start} end {end}")
        text = ''.join(lines[start:end])
        logging.info(f"text is {text}")
        return text

    def typing_screen(self, window):
        window.clear()
        untyped = 1
        curses.init_pair(untyped, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        typed = 2
        curses.init_pair(typed, curses.COLOR_GREEN, curses.COLOR_BLACK)
        mistyped = 3
        curses.init_pair(mistyped, curses.COLOR_RED, curses.COLOR_BLACK)
        text = self.get_text()
        window.addstr(text, curses.color_pair(untyped))
        window.move(0,0)

        try:
            line = 0
            position = 0
            key = None
            while position < len(text):
                key = window.getkey()
                logging.debug(f"key is '{key}'")
                if key == 'KEY_BACKSPACE' or key == curses.KEY_BACKSPACE:
                    (y,x) = curses.getsyx()
                    window.move(y,x-1)
                    position -= 1
                elif key == '\t':
                    logging.info('tab')
                    while text[position] == ' ':
                        position += 1
                        (y,x) = curses.getsyx()
                        window.move(y,x+1)
                        window.refresh()
                else:
                    if key == text[position]:
                        colors = typed
                    else:
                        colors = mistyped
                    window.addstr(key, curses.color_pair(colors))
                    position += 1
                window.refresh()
        except KeyboardInterrupt:
            # clean up and exit
            return

    def splash_screen(self, window):
        window.clear()
        window.addstr("press CTRL-C to exit")
        window.refresh()
        time.sleep(1)

    def run(self, window):
        self.splash_screen(window)
        self.typing_screen(window)

def main(stdscr):
    typo = Application(config_filename = "typo.conf")
    typo.run(stdscr)

if __name__ == "__main__":
    logging.basicConfig(filename="typo.log", level=logging.DEBUG)
    wrapper(main)