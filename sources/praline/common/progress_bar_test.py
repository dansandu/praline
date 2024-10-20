from unittest import TestCase
from praline.common.progress_bar import (
    format_description, format_timedelta, ProgressBarSupplier
)
from praline.common.testing.file_system_mock import FileSystemMock

from datetime import timedelta


class InterruptedException(Exception):
    pass


class ProgressBarTest(TestCase):
    def test_format_empty_description(self):
        description = ""

        self.assertEqual(format_description(description), description)

    def test_format_short_description(self):
        description = "123456789012345678901234567890"

        self.assertEqual(format_description(description), description)

    def test_format_full_description(self):
        description = "1234567890123456789012345678901234567890"

        self.assertEqual(format_description(description), description)

    def test_format_spilling_description(self):
        description = "1234567890123456789012345678901234567890extra"

        self.assertEqual(format_description(description), "...90123456789012345678901234567890extra")

    def test_format_timedelta(self):
        format_time = lambda *args, **kwargs: format_timedelta(timedelta(*args, **kwargs))

        self.assertEqual(format_time(milliseconds=28), "28ms")

        self.assertEqual(format_time(milliseconds=1760), "1s 760ms")

        self.assertEqual(format_time(seconds=10, milliseconds=250), "10s 250ms")

        self.assertEqual(format_time(minutes=7, seconds=27, milliseconds=58), "7m 27s")

        self.assertEqual(format_time(hours=1, minutes=58, seconds=50, milliseconds=900), "1h 58m")

        self.assertEqual(format_time(days=2, minutes=0, seconds=10), "2d")

        self.assertEqual(format_time(days=10, hours=23, minutes=59, seconds=59, milliseconds=999), "10d 23h")

    def test_early_exit(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=2, stage_count=10, 
                                                    stage_name='stage', display_elapsed_time=False)

        expected_lines = [
            " (2/10) stage\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M (2/10) stage\n",
            "  \x1B[34m==========\x1B[0m========================================  20.00%\n",
            "\x1B[2F\x1B[2M (2/10) stage \x1B[32mdone\x1B[0m\n",
        ]

        with progress_bar_supplier.create(resolution=5) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_exception(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=5, stage_count=5, 
                                                    stage_name='stage', display_elapsed_time=False)

        expected_lines = [
            "(5/5) stage\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M(5/5) stage\n",
            "  \x1B[34m==========\x1B[0m========================================  20.00%\n",
            "\x1B[2F\x1B[2M(5/5) stage \x1B[31mfailed\x1B[0m\n",
            "  \x1B[31m==========\x1B[0m========================================  20.00%\n",
        ]

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=5) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

                progress_bar.advance()
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_last_inch_exception(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=50, stage_count=100, 
                                                    stage_name='stage', display_elapsed_time=False)

        expected_lines = [
            " (50/100) stage\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M (50/100) stage short_text\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M (50/100) stage short_text\n",
            "  \x1B[34m=================================================\x1B[0m=  99.99%\n",
            "\x1B[2F\x1B[2M (50/100) stage short_text \x1B[31mfailed\x1B[0m\n",
            "  \x1B[31m=================================================\x1B[0m=  99.99%\n",
        ]

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=1) as progress_bar:
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

                progress_bar.update_description("short_text")
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

                progress_bar.advance()
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:6]))

                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_nonzero_resolution(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=5, stage_count=100, 
                                                    stage_name='stage', display_elapsed_time=False)

        expected_lines = [
            "  (5/100) stage\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M  (5/100) stage short_text\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M  (5/100) stage short_text\n",
            "  \x1B[34m=========================\x1B[0m=========================  50.00%\n",
            "\x1B[2F\x1B[2M  (5/100) stage ...ng_to_display_inside_the_progress_bar\n",
            "  \x1B[34m=========================\x1B[0m=========================  50.00%\n",
            "\x1B[2F\x1B[2M  (5/100) stage ...ng_to_display_inside_the_progress_bar\n",
            "  \x1B[34m=================================================\x1B[0m=  99.99%\n",
            "\x1B[2F\x1B[2M  (5/100) stage \x1B[32mdone\x1B[0m\n",
        ]

        with progress_bar_supplier.create(resolution=2) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.update_description("short_text")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:6]))

            progress_bar.update_description("long_path_to_file_too_long_to_display_inside_the_progress_bar")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:8]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:10]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_zero_resolution_failure(self):
        file_system = FileSystemMock()

        expected_lines = [
            "(1/1) stage name\n",
            "  ==================================================\n",
            "\x1B[2F\x1B[2M(1/1) stage name \x1B[31mfailed\x1B[0m\n",
            "  \x1B[31m==================================================\x1B[0m\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=1, stage_count=1, 
                                                    stage_name='stage name', display_elapsed_time=False)

        exception_raised = False
        try:
            with progress_bar_supplier.create(resolution=0):
                self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))
                raise InterruptedException()
        except InterruptedException:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
            exception_raised = True
        self.assertTrue(exception_raised)

    def test_zero_resolution_success(self):
        file_system = FileSystemMock()

        expected_lines = [
            "(2/2) stage name\n",
            "  ==================================================\n",
            "\x1B[2F\x1B[2M(2/2) stage name \x1B[32mdone\x1B[0m\n",
        ]

        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=2, stage_count=2, 
                                                    stage_name='stage name', display_elapsed_time=False)
        with progress_bar_supplier.create(resolution=0) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            self.assertRaises(ValueError, progress_bar.advance)
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))

    def test_summary(self):
        file_system = FileSystemMock()
        progress_bar_supplier = ProgressBarSupplier(file_system, stage_index=11, stage_count=12, 
                                                    stage_name='test', display_elapsed_time=False)

        expected_lines = [
            "(11/12) test\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M(11/12) test myTestCase\n",
            "  ==================================================   0.00%\n",
            "\x1B[2F\x1B[2M(11/12) test myTestCase\n",
            "  \x1B[34m=================================================\x1B[0m=  99.99%\n",
            "\x1B[2F\x1B[2M(11/12) test myTestCase\n",
            "  \x1B[34m=================================================\x1B[0m=  99.99%\n",
            "\x1B[2F\x1B[2M(11/12) test 5356 asserts in 21 tests \x1B[32mdone\x1B[0m\n",
        ]

        with progress_bar_supplier.create(resolution=1) as progress_bar:
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:2]))

            progress_bar.update_description("myTestCase")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:4]))

            progress_bar.advance()
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:6]))

            progress_bar.update_summary("5356 asserts in 21 tests")
            self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines[:8]))
        
        self.assertEqual(file_system.stdout.getvalue(), ''.join(expected_lines))
