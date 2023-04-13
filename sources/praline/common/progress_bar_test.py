from unittest import TestCase
from praline.common.progress_bar import ProgressBarSupplier, empty_bar_character
from praline.common.testing.file_system_mock import FileSystemMock


class ProgressBarTest(TestCase):
    def test_zero_resolution(self):
        file_system = FileSystemMock()

        expected_lines = [

            "\rstage name ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage name ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage name ██████████████████████████████████████████████████ 100.00%                                         \r\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, 'stage_name', 10, True)
        with progress_bar_supplier.create(0) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:3]))


    def test_nonzero_resolution(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, 'stage_name', 12, False)

        expected_lines = [

            "\rstage_name   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage_name   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                   0001                  \r",

            "\rstage_name   █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00%                   0001                  \r",

            "\rstage_name   █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00% ...ng/to/display/inside/the/progress/bar\r",

            "\rstage_name   ██████████████████████████████████████████████████ 100.00%                                         \r",

            "\rstage_name   ██████████████████████████████████████████████████ 100.00%                                         \r\n",

        ]

        with progress_bar_supplier.create(2) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.update_summary("0001")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:3]))

            progress_bar.update_summary("long/path/to/file/too/long/to/display/inside/the/progress/bar")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:5]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:6]))
