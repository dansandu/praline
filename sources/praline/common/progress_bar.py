from praline.common.file_system import FileSystem


empty_bar_character = '\u2592'

filled_bar_character = '\u2588'

bar_length = 50

summary_length = 40

class ProgressBar:
    def __init__(self, file_system: FileSystem, stage_name: str, resolution: int):
        self.file_system = file_system
        self.stage_name = stage_name
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
        if self.progress < self.resolution:
            shortened_summary = '...' + self.summary[3-summary_length:] if len(self.summary) > summary_length else self.summary
        else:
            shortened_summary = ''
        self.file_system.print(f"\r{self.stage_name} {filled_bar_character * filled_length + empty_bar_character * empty_length} {percentage:7.2%} {shortened_summary: ^{summary_length}}", end='\r', flush=True)

    def __exit__(self, type, value, traceback):
        self.display(force_completion=True)
        self.file_system.print()


class ProgressBarSupplier:
    def __init__(self, file_system: FileSystem, stage_name: str):
        self.file_system = file_system
        self.stage_name  = stage_name
    
    def create(self, resolution: int) -> ProgressBar:
        return ProgressBar(self.file_system, self.stage_name, resolution)
