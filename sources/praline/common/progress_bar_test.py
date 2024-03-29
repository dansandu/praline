from unittest import TestCase
from praline.common.progress_bar import ProgressBarSupplier
from praline.common.testing.file_system_mock import FileSystemMock


class InterruptedException(Exception):
    pass


class ProgressBarTest(TestCase):
    def test_zero_resolution_success(self):
        file_system = FileSystemMock()

        expected_lines = [
            "\rstage name   ==================================================                                                \r",
            "\rstage name   \033[32m==================================================\033[0m                                                \r\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage name', header_length=12)
        with progress_bar_supplier.create(resolution=0) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

            self.assertRaises(ValueError, progress_bar.advance)
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_zero_resolution_failure(self):
        file_system = FileSystemMock()

        expected_lines = [
            "\rstage name   ==================================================                                                \r",
            "\rstage name   \033[31m==================================================\033[0m                                                \r\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage name', header_length=12)

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=0) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])
                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_nonzero_resolution(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_length=5)

        expected_lines = [
            "\rstage ==================================================  0.00%                                         \r",
            "\rstage ==================================================  0.00%                short_text               \r",
            "\rstage \033[34m=========================\033[0m========================= 50.00%                short_text               \r",
            "\rstage \033[34m=========================\033[0m========================= 50.00% ...ng_to_display_inside_the_progress_bar\r",
            "\rstage \033[34m=================================================\033[0m= 99.99% ...ng_to_display_inside_the_progress_bar\r",
            "\rstage \033[32m==================================================\033[0m                                                \r\n",
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
            "\rstage ==================================================  0.00%                                         \r",
            "\rstage \033[34m==========\033[0m======================================== 20.00%                                         \r",
            "\rstage \033[32m==================================================\033[0m                                                \r\n",
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
            "\rstage ==================================================  0.00%                                         \r",
            "\rstage \033[34m==========\033[0m======================================== 20.00%                                         \r",
            "\rstage \033[31m==========\033[0m======================================== 20.00%                                         \r\n",
        ]

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=5) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

                progress_bar.advance()
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_last_inch_exception(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, header='stage', header_length=5)

        expected_lines = [
            "\rstage ==================================================  0.00%                                         \r",
            "\rstage ==================================================  0.00%                short_text               \r",
            "\rstage \033[34m=================================================\033[0m= 99.99%                short_text               \r",
            "\rstage \033[31m=================================================\033[0m= 99.99%                short_text               \r\n",
        ]

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=1) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), expected_lines[0])

                progress_bar.update_summary("short_text")
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

                progress_bar.advance()
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:3]))

                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)
