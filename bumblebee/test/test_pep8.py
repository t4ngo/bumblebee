
import unittest
import os.path


#===========================================================================

class TestPep8(unittest.TestCase):

    def test_pep8(self):
        import pep8

        pep8_args = [
                     "--show-source",
                     "ignored",  # Ignored argument, but needed
                                 #  by pep8.process_options()
                    ]
        directory = os.path.split(os.path.abspath(__file__))[0]
        directory = os.path.split(directory)[0]

        pep8.process_options(pep8_args)
        pep8.input_dir(directory)
        output = pep8.get_statistics()
        for line in output:
            print line
        self.assertFalse(output)
