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
    Blue  = 3

    @classmethod
    def highlight_text(cls, text: str, highlight):
        if not text or highlight == TextHighlight.No:
            return text
        if highlight == TextHighlight.Red:
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
        summary           = TextHighlight.highlight_text(shortened, highlight)
    else:
        padding_character = ' '
        padding = summary_length - len(text)
        left_padding  = padding // 2
        right_padding = padding // 2 + padding % 2
        summary = padding_character * left_padding + TextHighlight.highlight_text(text, highlight) + padding_character * right_padding
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
        if exiting:
            if success and self.progress == self.resolution:
                self.progress = self.resolution = 100
                summary = format_summary(completed_summary, TextHighlight.Green)
            else:
                summary = format_summary(cancelled_summary, TextHighlight.Red)
            ending = '\n'
        else:
            summary = format_summary(self.summary, TextHighlight.Blue)
            ending = ''

        percentage    = self.progress / self.resolution if self.resolution > 0 else 0.0
        filled_length = round(percentage * bar_length)
        empty_length  = bar_length - filled_length

        self.file_system.print(f"\r{self.header: <{self.header_length}} {filled_bar_character * filled_length + empty_bar_character * empty_length} {percentage:7.2%} {summary}", end=ending, flush=True)

    def __exit__(self, type, value, traceback):
        self.display(exiting=True, success=type == None)
 

class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, header: str, header_length: int):
        self.file_system   = file_system
        self.header        = header
        self.header_length = header_length
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(self.file_system, self.header, self.header_length, resolution)
