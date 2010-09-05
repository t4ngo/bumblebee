
import os
from setuptools import setup, find_packages


#---------------------------------------------------------------------------
# Set up package.

def read(*names):
    return open(os.path.join(os.path.dirname(__file__), *names)).read()

setup(
      name              = "bumblebee",
      author            = "Charlie T4ngo",
      author_email      = "charlie.t4ngo@gmail.com",
      version           = "0.0",
      description       = "",
      long_description  = read("README.txt"),
      url               = "http://bitbucket.org/t4ngo/bumblebee",
      license           = "",
      zip_safe          = True,
      packages          = find_packages(),
      test_suite        = "bumblebee.test.suites.default_suite",

      classifiers=[
                   "Environment :: Win32 (MS Windows)",
                   "Operating System :: Microsoft :: Windows",
                   "Programming Language :: Python",
                  ],
     )
