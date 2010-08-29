
import unittest


#===========================================================================

class TestRun(unittest.TestCase):

    def test_run(self):
        import bumblebee.application
        bumblebee.application.run_application()
