from unittest import TestCase
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.testing.file_system_mock import FileSystemMock


class ProgressBarTest(TestCase):
    def test_zero_resolution(self):
        file_system = FileSystemMock()

        expected_lines = [

            "\rstage name   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage name   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage name   ██████████████████████████████████████████████████ 100.00%                   \033[32mdone\033[0m                  \r\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage name', header_padding=12)
        with progress_bar_supplier.create(resolution=0) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))


    def test_nonzero_resolution(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_padding=0)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                short/text               \r",

            "\rstage █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00%                short/text               \r",

            "\rstage █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00% ...ng/to/display/inside/the/progress/bar\r",

            "\rstage ██████████████████████████████████████████████████ 100.00% ...ng/to/display/inside/the/progress/bar\r",

            "\rstage ██████████████████████████████████████████████████ 100.00%                   \033[32mdone\033[0m                  \r\n",

        ]

        with progress_bar_supplier.create(resolution=2) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.update_summary("short/text")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:3]))

            progress_bar.update_summary("long/path/to/file/too/long/to/display/inside/the/progress/bar")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:5]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_early_exit(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_padding=0)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                                         \r",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                  \033[31mhalted\033[0m                 \r\n",

        ]

        with progress_bar_supplier.create(resolution=5) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_exception(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_padding=0)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         \r",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                                         \r",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                  \033[31mhalted\033[0m                 \r\n",

        ]

        class InterruptedException(Exception):
            pass

        try:
            with progress_bar_supplier.create(resolution=5) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

                progress_bar.advance()
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
