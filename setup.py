
import os
from setuptools import setup, find_packages


#---------------------------------------------------------------------------
# Retrieve information about this package from nearby files.

package_root = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(package_root, "README.txt")
readme_text = open(readme_path).read()


#---------------------------------------------------------------------------
# Set up package.

setup(
      name          = "bumblebee",
      version       = "0.0",
      description   = "",
      author        = "Charlie T4ngo",
      author_email  = "charlie.t4ngo@gmail.com",
      license       = "GPL",
      url           = "http://code.google.com/p/dragonfly/",
      zip_safe      = True,
      long_description = readme_text,

      classifiers=[
                   "Environment :: Win32 (MS Windows)",
                   "Operating System :: Microsoft :: Windows",
                   "Programming Language :: Python",
                  ],

      install_requires="setuptools >= 0.6c7",

      packages=find_packages(),
      test_suite = "bumblebee.test.suite_all.test_suite",
     )
