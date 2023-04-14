from praline.common.file_system import FileSystem
from enum import Enum


filled_bar_character = '\u2588'

empty_bar_character = '\u2592'

bar_length = 50

summary_length = 40

completed_summary = 'done'

cancelled_summary = 'halted'


class TextHighlight(Enum):
    No    = 0
    Red   = 1
    Green = 2


def format_summary(text: str, highlight: TextHighlight = TextHighlight.No):
    if highlight == TextHighlight.Green:
        color_prefix = '\033[32m'
        color_suffix = '\033[0m'
    elif highlight == TextHighlight.Red:
        color_prefix = '\033[31m'
        color_suffix = '\033[0m'
    else:
        color_prefix = ''
        color_suffix = ''
    if len(text) > summary_length:
        shortened_prefix  = '...'
        summary = color_prefix + shortened_prefix + text[len(shortened_prefix) - summary_length:] + color_suffix
    else:
        padding_character = ' '
        padding = summary_length - len(text)
        left_padding  = padding // 2
        right_padding = padding // 2 + padding % 2
        summary = padding_character * left_padding + color_prefix + text + color_suffix + padding_character * right_padding
    return summary


class ProgressBar:
    def __init__(self, file_system: FileSystem, header: str, header_padding: int, resolution: int):
        self.file_system = file_system
        self.header = header
        self.header_padding = header_padding
        self.resolution = resolution
        self.progress = 0
        self.summary = ''

    def __enter__(self):
        self.display()
        return self
    
    def update_summary(self, summary: str):
        self.summary = summary
        self.display()

    def advance(self, amount: int = 1):
        self.progress = min(self.progress + amount, self.resolution)
        self.display()
    
    def display(self, exiting: bool = False, success: bool = False):
        if exiting:
            if success and self.progress == self.resolution:
                self.progress = self.resolution = 100
                summary = format_summary(completed_summary, TextHighlight.Green)
            else:
                summary = format_summary(cancelled_summary, TextHighlight.Red)
            ending = '\r\n'
        else:
            summary = format_summary(self.summary)
            ending = '\r'

        percentage    = self.progress / self.resolution if self.resolution > 0 else 0.0
        filled_length = round(percentage * bar_length)
        empty_length  = bar_length - filled_length

        self.file_system.print(f"\r{self.header: <{self.header_padding}} {filled_bar_character * filled_length + empty_bar_character * empty_length} {percentage:7.2%} {summary}", end=ending, flush=True)

    def __exit__(self, type, value, traceback):
        self.display(exiting=True, success=type == None)
 

class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, header: str, header_padding: int):
        self.file_system    = file_system
        self.header         = header
        self.header_padding = header_padding
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(self.file_system, self.header, self.header_padding, resolution)
