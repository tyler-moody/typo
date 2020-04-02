import curses
from curses import wrapper
import json
import logging
import os
import random
import time

class Application:
    _colors = dict()
    _config = None
    _files = list()
    def __init__(self, config_filename):
        with open(config_filename) as f:
            self._config = json.loads(f.read())
        self.make_files_list()
        self._colors["untyped"] = 1
        curses.init_pair(self._colors["untyped"], curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self._colors["typed"] = 2
        curses.init_pair(self._colors["typed"], curses.COLOR_GREEN, curses.COLOR_BLACK)
        self._colors["mistyped"] = 3
        curses.init_pair(self._colors["mistyped"], curses.COLOR_RED, curses.COLOR_BLACK)

    def make_files_list(self):
        source_root = self._config["source_root"]
        omit_dir_pattern = self._config["omit_dir_pattern"]
        filetype_pattern = self._config["filetype_pattern"]
        command = f"find {source_root} -not -path \"{omit_dir_pattern}\" -regextype posix-extended -regex \"{filetype_pattern}\""
        logging.info(f"running command: {command}")
        stream = os.popen(command)
        for filename in stream:
            self._files.append(filename.strip())
        logging.info(f"found {len(self._files)} source files")

    def pick_file(self):
        n = random.randint(0, len(self._files))
        return self._files[n]

    def get_text(self):
        text_size_lines = self._config["text_size_lines"]

        filename = self.pick_file()
        logging.info(f"opening {filename}")
        with open(filename) as f:
            lines = f.readlines()
        start = random.randint(0, len(lines) - text_size_lines)
        end = start + min(text_size_lines, len(lines) - start)
        logging.info(f"start {start} end {end}")
        return (filename, lines[start:end], start, end)

    def typing_screen(self, window):
        window.clear()
        (filename, text, start, end) = self.get_text()
        window.addstr(curses.LINES-1, 0, f"{filename}:{start}:{end}")
        window.move(0,0)
        logging.info(f"num lines is {len(text)}")
        window.addstr(''.join(text), curses.color_pair(self._colors["untyped"]))
        window.move(0,0)

        try:
            current_line = 0
            current_char = 0
            error_count = 0
            key = None
            while True:
                logging.info(f"line {current_line} char {current_char}")
                key = window.getkey()
                logging.debug(f"key is '{key}'")
                if key == 'KEY_BACKSPACE' or key == curses.KEY_BACKSPACE:
                    (y,x) = window.getyx()
                    if x > 0:
                        window.move(y,x-1)
                        current_char -= 1
                        window.addch(text[current_line][current_char], curses.color_pair(self._colors["untyped"]))
                        window.move(y,x-1)
                elif key == "KEY_NPAGE":
                    logging.info("page down")
                    return

                elif key == '\t':
                    logging.info('tab')
                    while text[current_line][current_char] == ' ':
                        current_char += 1
                        (y,x) = window.getyx()
                        window.move(y,x+1)
                        window.refresh()
                else:
                    if current_char >= len(text[current_line]):
                        colors = self._colors["mistyped"]
                        error_count += 1
                    elif key == text[current_line][current_char]:
                        colors = self._colors["typed"]
                    else:
                        colors = self._colors["mistyped"]
                        error_count += 1
                    window.addstr(key, curses.color_pair(colors))
                    current_char += 1
                    if key == '\n': 
                        logging.info("ENTER")
                        current_line += 1
                        current_char = 0
                        if current_line >= len(text):
                            return
                        window.refresh()
                        while text[current_line][current_char] == ' ':
                            current_char += 1
                            (y,x) = window.getyx()
                            window.move(y,x+1)
                            window.refresh()
                    (y,x) = window.getyx()
                    window.addstr(curses.LINES-1, curses.COLS-10, f"errors:{error_count}")
                    window.move(y,x)
                window.refresh()
        except KeyboardInterrupt:
            # clean up and exit
            return

    def splash_screen(self, window):
        window.clear()
        window.addstr("press CTRL-C to exit\n")
        window.addstr("press PAGE DOWN to skip to the next text\n")
        window.refresh()
        time.sleep(1)

    def run(self, window):
        self.splash_screen(window)
        while True:
            self.typing_screen(window)

def main(stdscr):
    typo = Application(config_filename = "typo.conf")
    typo.run(stdscr)

if __name__ == "__main__":
    logging.basicConfig(filename="typo.log", level=logging.DEBUG)
    wrapper(main)
