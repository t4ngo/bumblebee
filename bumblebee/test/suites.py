# c:\python26\python C:\data\projects\sr\bumblebee\setup.py test

import os
import sys
import logging
import unittest


#===========================================================================

safe_names         = [
                      "test:test_pep8",
                     ]
unsafe_names       = [
                      "test:test_config",
                     ]
interactive_names  = [
                      "test:test_run_application",
                     ]


#===========================================================================

def build_suite(suite, names):
    """
        Creates tests from the given *names* and adds them to *suite*.

        :param suite: A test suite to which tests are added
        :type suite: unittest.TestSuite or derived class
        :param names: A sequence of names for which tests are to be built
        :type names: sequence of strings

        A string within the *names* sequence can have one of the following
        formats:
         * `doc:`-prefix (e.g. `doc:my_document.txt`)
         * `test:`-prefix will be loaded using
           `unittest.defaultTestLoader.loadTestsFromName`.

    """

    # Determine the root directory of the source code files.  This is
    #  used for finding doctest files specified relative to that root.
    project_root = os.path.join(os.path.dirname(__file__), "..", "..")
    project_root = os.path.abspath(project_root)

    # Load test cases from specified names.
    loader = unittest.defaultTestLoader
    for name in names:
        if name.startswith("test:"):
            name = "bumblebee.test." + name[5:]
            suite.addTests(loader.loadTestsFromName(name))
        elif name.startswith("doc:"):
            path = name[4:]
            path = os.path.join(project_root, *path.split("/"))
            path = os.path.abspath(path)
            suite.addTests(doctest.DocFileSuite(path))
        else:
            raise Exception("Invalid test name: %r." % (name,))
    return suite


def setup_logging():
    """
        Sets up the Python logging infrastructure for testing.

        This function sets up the logging infrastructure to log
        all messages with level ERROR or higher to stderr.

    """

    log = logging.getLogger("")
    log.setLevel(logging.ERROR)
    log.addHandler(logging.StreamHandler())


def default_suite():
    setup_logging()
    return build_suite(unittest.TestSuite(),
                       safe_names + unsafe_names)
