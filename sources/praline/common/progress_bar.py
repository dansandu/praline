from praline.common.file_system import FileSystem
from enum import Enum


filled_bar_character = '='

empty_bar_character = '='

bar_length = 50

summary_length = 40

status_length = 6

show_cursor = '\033[?25h'

hide_cursor = '\033[?25l'


class TextHighlight(Enum):
    No        = 0
    Red       = 1
    Green     = 2
    Blue      = 3


def format_text(text: str, highlight=TextHighlight.No):
    if not text:
        return text

    if highlight == TextHighlight.No:
        return text
    elif highlight == TextHighlight.Red:
        return '\033[31m' + text + '\033[0m'
    elif highlight == TextHighlight.Green:
        return '\033[32m' + text + '\033[0m'
    elif highlight == TextHighlight.Blue:
        return '\033[34m' + text + '\033[0m'
    else:
        raise ValueError(f"invalid TextHighlight provided: {highlight}")  


def format_summary(text: str, highlight: TextHighlight = TextHighlight.No):
    if len(text) > summary_length:
        shortened_prefix  = '...'
        shortened         = shortened_prefix + text[len(shortened_prefix) - summary_length:]
        summary           = format_text(shortened, highlight)
    else:
        padding_character = ' '
        padding = summary_length - len(text)
        left_padding  = padding // 2
        right_padding = padding // 2 + padding % 2
        summary = padding_character * left_padding + format_text(text, highlight) + padding_character * right_padding
    return summary


class ProgressBar:
    def __init__(self, file_system: FileSystem, header: str, header_length: int, resolution: int):
        if header_length <= 0:
            raise ValueError("progress bar header length must be greater than 0")
        
        if resolution < 0:
            raise ValueError("progress bar resolution must be greater or equal to 0")
        
        self.file_system   = file_system
        self.header        = header
        self.header_length = header_length
        self.resolution    = resolution
        self.progress      = 0
        self.summary       = ''

    def __enter__(self):
        self.file_system.print(hide_cursor, end='')
        self.display()
        return self
    
    def update_summary(self, summary: str):
        self.summary = summary
        self.display()

    def advance(self, amount: int = 1):
        if self.resolution == 0:
            raise ValueError("cannot advance if progress bar resolution is 0 -- the bar will be filled on successful __exit__")

        if amount <= 0:
            raise ValueError("progress bar advance amount must be greater than 0")

        self.progress = min(self.progress + amount, self.resolution)
        self.display()
    
    def display(self, exiting: bool = False, success: bool = False):
        bar = ''
        status = status_length * ' '
        summary = format_summary('', TextHighlight.No)
        ending = ''

        if exiting:
            if success:
                bar = format_text(bar_length * filled_bar_character, TextHighlight.Green)
            else:
                if self.resolution > 0:
                    percentage = self.progress / self.resolution
                    filled_length = min(int(percentage * bar_length), bar_length - 1)
                    bar = format_text(filled_length * filled_bar_character, TextHighlight.Red) + (bar_length - filled_length) * empty_bar_character
                    status = f"{percentage:6.2%}" if percentage < 1.00 else "99.99%"
                else:
                    bar = format_text(bar_length * filled_bar_character, TextHighlight.Red)
            ending = '\n'
        else:
            if self.resolution > 0:
                percentage = self.progress / self.resolution
                filled_length = min(int(percentage * bar_length), bar_length - 1)
                bar = format_text(filled_length * filled_bar_character, TextHighlight.Blue) + (bar_length - filled_length) * empty_bar_character
                status = f"{percentage:6.2%}" if percentage < 1.00 else "99.99%"
            else:
                bar = format_text(bar_length * empty_bar_character, TextHighlight.No)

            summary = format_summary(self.summary, TextHighlight.No)
        
        self.file_system.print(f"\r{self.header: <{self.header_length}} {bar} {status} {summary}\r", end=ending, flush=True, clear_current_line=False)

    def __exit__(self, type, value, traceback):
        self.display(exiting=True, success=type == None)
        self.file_system.print(show_cursor, end='', clear_current_line=False)


class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, header: str, header_length: int):
        self.file_system   = file_system
        self.header        = header
        self.header_length = header_length
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(self.file_system, self.header, self.header_length, resolution)
