from unittest import TestCase
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.testing.file_system_mock import FileSystemMock


class ProgressBarTest(TestCase):
    def test_zero_resolution(self):
        file_system = FileSystemMock()

        expected_lines = [

            "\rstage name   ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         ",

            "\rstage name   ██████████████████████████████████████████████████ 100.00%                   \033[32mdone\033[0m                  \n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage name', header_length=12)
        with progress_bar_supplier.create(resolution=0) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            self.assertRaises(ValueError, progress_bar.advance)
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))


    def test_nonzero_resolution(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_length=5)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         ",

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                \033[34mshort_text\033[0m               ",

            "\rstage █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00%                \033[34mshort_text\033[0m               ",

            "\rstage █████████████████████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  50.00% \033[34m...ng_to_display_inside_the_progress_bar\033[0m",

            "\rstage ██████████████████████████████████████████████████ 100.00% \033[34m...ng_to_display_inside_the_progress_bar\033[0m",

            "\rstage ██████████████████████████████████████████████████ 100.00%                   \033[32mdone\033[0m                  \n",

        ]

        with progress_bar_supplier.create(resolution=2) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.update_summary("short_text")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:3]))

            progress_bar.update_summary("long_path_to_file_too_long_to_display_inside_the_progress_bar")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:5]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_early_exit(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_length=5)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         ",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                                         ",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                  \033[31mhalted\033[0m                 \n",

        ]

        with progress_bar_supplier.create(resolution=5) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_exception(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_length=5)

        expected_lines = [

            "\rstage ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒   0.00%                                         ",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                                         ",

            "\rstage ██████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  20.00%                  \033[31mhalted\033[0m                 \n",

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
