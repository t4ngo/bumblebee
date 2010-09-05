
import unittest
import os.path


#===========================================================================

class TestPep8(unittest.TestCase):

    def test_pep8(self):
        """ Verify that source code complies with PEP 8 formatting. """
        import pep8

        ignored_codes = [
                         "E221",
                         "E241",
                        ]

        # Setup pep8 processing options.
        pep8_args = [
                     "--show-source",
                     "--repeat",
                     "--ignore=" + ",".join(ignored_codes),
                     "ignored",  # Ignored argument, but needed
                                 #  by pep8.process_options()
                    ]
        pep8.process_options(pep8_args)

        # Call pep8 to process local files.
        directory = os.path.split(os.path.abspath(__file__))[0]
        directory = os.path.split(directory)[0]
        pep8.input_dir(directory)
        statistics = pep8.get_statistics()

        filtered_statistics = []
        for line in statistics:
            code = line[8:12]
            if code not in ignored_codes:
                filtered_statistics.append(line)

        self.assertFalse(filtered_statistics)
