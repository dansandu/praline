from praline.common.file_system import FileSystem


empty_bar_character = '\u2592'

filled_bar_character = '\u2588'

bar_length = 50

summary_length = 40


class ProgressBar:
    def __init__(self, file_system: FileSystem, stage_name: str, stage_name_padding: int, replace_header_underscores_with_spaces: bool, resolution: int):
        self.file_system = file_system
        self.stage_name = stage_name
        self.stage_name_padding = stage_name_padding
        self.replace_header_underscores_with_spaces = replace_header_underscores_with_spaces
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
    
    def display(self, force_completion: bool = False):
        if force_completion:
            self.progress = self.resolution = 100
        percentage    = self.progress / self.resolution if self.resolution > 0 else 0.0
        filled_length = round(percentage * bar_length)
        empty_length  = bar_length - filled_length

        if self.replace_header_underscores_with_spaces:
            header = self.stage_name.replace('_', ' ')
        else:
            header = self.stage_name

        if self.progress < self.resolution:
            prefix = '...'
            shortened_summary = prefix + self.summary[len(prefix) - summary_length:] if len(self.summary) > summary_length else self.summary
        else:
            shortened_summary = ''

        self.file_system.print(f"\r{header: <{self.stage_name_padding}} {filled_bar_character * filled_length + empty_bar_character * empty_length} {percentage:7.2%} {shortened_summary: ^{summary_length}}", end='\r', flush=True)

    def __exit__(self, type, value, traceback):
        self.display(force_completion=True)
        self.file_system.print()


class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, stage_name: str, stage_name_padding: int, replace_header_underscores_with_spaces: bool):
        self.file_system                            = file_system
        self.stage_name                             = stage_name
        self.stage_name_padding                     = stage_name_padding
        self.replace_header_underscores_with_spaces = replace_header_underscores_with_spaces
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(self.file_system, self.stage_name, self.stage_name_padding, self.replace_header_underscores_with_spaces, resolution)
