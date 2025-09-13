from praline.common.file_system import FileSystem
from enum import Enum
from datetime import datetime, timedelta

import math


filled_bar_character = '='

empty_bar_character = '='

bar_length = 50

maximum_description_length = 40

success_text = 'done'

failure_text = 'failed'

move_cursor_up_two_lines = "\x1B[2F"

delete_two_lines = "\x1B[2M"


class TextHighlight(Enum):
    No        = 0
    Red       = 1
    Green     = 2
    Blue      = 3


def format_text(text: str, highlight=TextHighlight.No):
    if len(text) == 0 or highlight == TextHighlight.No:
        return text
    elif highlight == TextHighlight.Red:
        return '\x1B[31m' + text + '\x1B[0m'
    elif highlight == TextHighlight.Green:
        return '\x1B[32m' + text + '\x1B[0m'
    elif highlight == TextHighlight.Blue:
        return '\x1B[34m' + text + '\x1B[0m'
    else:
        raise ValueError(f"Invalid TextHighlight provided: {highlight}")  


def format_title(stage_name):
    return stage_name.replace('_', ' ')


def format_description(text: str):
    if len(text) > maximum_description_length:
        prefix = '...'
        return prefix + text[len(prefix) - maximum_description_length:]
    return text


def format_timedelta(td: timedelta):
    promotions = [(1000, 's'), (60, 'm'), (60, 'h'), (24, 'd')]
    elapsed = int(td / timedelta(milliseconds=1))
    elapsed_unit = 'ms'
    elapsed_remainder = 0
    elapsed_remainder_unit = None
    for factor, unit in promotions:
        if elapsed >= factor:
            elapsed_remainder = elapsed % factor
            elapsed_remainder_unit = elapsed_unit
            elapsed = elapsed // factor
            elapsed_unit = unit
        else:
            break
    
    if elapsed_remainder > 0:
        return f"{elapsed}{elapsed_unit} {elapsed_remainder}{elapsed_remainder_unit}"
    else:
        return f"{elapsed}{elapsed_unit}"


class ProgressBar:
    def __init__(self, file_system: FileSystem, stage_name: str, resolution: int, display_elapsed_time: bool):        
        if resolution < 0:
            raise ValueError("Progress bar resolution must be greater or equal to 0")
        
        self.file_system          = file_system
        self.stage_name           = stage_name
        self.resolution           = resolution
        self.progress             = 0
        self.description          = ''
        self.summary              = ''
        self.time_start           = datetime.now()
        self.display_elapsed_time = display_elapsed_time

    def __enter__(self):
        self.display(first_print=True)
        return self
    
    def update_description(self, description: str):
        self.description = description
        self.display()

    def update_summary(self, summary: str):
        self.summary = summary
        self.display()

    def advance(self, amount: int = 1):
        if self.resolution == 0:
            raise ValueError("Cannot advance if progress bar resolution is 0 -- the bar will be filled on successful __exit__")

        if amount <= 0:
            raise ValueError("Progress bar advance amount must be greater than 0")

        self.progress = min(self.progress + amount, self.resolution)
        self.display()
    
    def display(self, first_print: bool = False):
        header = f" {format_title(self.stage_name)}"

        if len(self.description) > 0:
            header = f"{header} {format_description(self.description)}"

        if not first_print:
            header = f"{move_cursor_up_two_lines}{delete_two_lines}{header}"

        if self.resolution > 0:
            percentage = self.progress / self.resolution
            filled_length = min(round(percentage * bar_length), bar_length - 1)
            bar = format_text(filled_length * filled_bar_character, TextHighlight.Blue) + (bar_length - filled_length) * empty_bar_character
            status = f"{percentage:6.2%}" if percentage < 1.00 else "99.99%"
            footer = f"  {bar}  {status}"
        else:
            footer = f"  {bar_length * empty_bar_character}"
        
        self.file_system.print(header, footer, sep='\n', flush=True)

    def __exit__(self, type, value, traceback):
        header = f"{move_cursor_up_two_lines}{delete_two_lines} {format_title(self.stage_name)}"

        success = type == None
        if success:
            if len(self.summary) > 0:
                header = f"{header} {self.summary}"

            header = f"{header} {format_text(success_text, TextHighlight.Green)}"

            if self.display_elapsed_time:
               header = f"{header} {format_timedelta(datetime.now() - self.time_start)}"

            self.file_system.print(header, flush=True)
        else:
            if len(self.description) > 0:
                header = f"{header} {format_description(self.description)}"

            header = f"{header} {format_text(failure_text, TextHighlight.Red)}"

            if self.resolution > 0:
                percentage = self.progress / self.resolution
                filled_length = min(round(percentage * bar_length), bar_length - 1)
                bar = format_text(filled_length * filled_bar_character, TextHighlight.Red) + (bar_length - filled_length) * empty_bar_character
                status = f"{percentage:6.2%}" if percentage < 1.00 else "99.99%"
                footer = f"  {bar}  {status}"
            else:
                footer = f"  {format_text(bar_length * filled_bar_character, TextHighlight.Red)}"
            
            self.file_system.print(header, footer, sep='\n', flush=True)


class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, stage_name: str, display_elapsed_time: bool = True):
        self.file_system          = file_system
        self.stage_name           = stage_name
        self.display_elapsed_time = display_elapsed_time
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(
            self.file_system,
            self.stage_name, 
            resolution, 
            self.display_elapsed_time
        )
