
import sys
import unittest


#===========================================================================

test_module_names = [
                     "test_pep8",
                     "test_run_application",
                    ]


def build_suite():
    try:
        import bumblebee.test
        for name in test_module_names:
            __import__("bumblebee.test." + name)
        test_modules = [getattr(bumblebee.test, name)
                        for name in test_module_names]
    except Exception, e:
        print "Exception during importing test modules: {0}".format(e)
        sys.exit(1)

    loader = unittest.defaultTestLoader
    test_suite = unittest.TestSuite()
    for module in test_modules:
        module_tests = loader.loadTestsFromModule(module)
        test_suite.addTest(module_tests)

    return test_suite

test_suite = build_suite()
