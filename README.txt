
Bumblebee -- Dragonfly command module loader
============================================================================

Bumblebee is a command-module loader for Dragonfly.  It also supports
loading NatLink modules.


Installation
----------------------------------------------------------------------------

Bumblebee is currently under development, and does not yet come packaged
in and easily distributable form.  At the moment, it is best to install
Bumblebee in a virtual environment as follows:

 1. Make sure the virtualenv tool is available on the system:
     - C:\Python26\Scripts\easy_install.exe virtualenv

 1. Make sure wxPython is available on the system.
    This package can be installed using a Windows installer available at:
    http://www.wxpython.org/download.php

 1. Create a directory in which to install Bumblebee and its dependencies.
    In the next steps this directory will be known as "<directory>".

 1. Create a virtual environment within that directory:
     - C:\Python26\Scripts\virtualenv.exe <directory>

 1. Install Bumblebee's dependencies in the virtual environment:
     - <directory>\Scripts\easy_install.exe pep8
     - <directory>\Scripts\easy_install.exe pyutilib.component.core
     - <directory>\Scripts\easy_install.exe pyutilib.component.config
     - <directory>\Scripts\easy_install.exe pyutilib.component.loader

 1. Extract Bumblebee to a suitable location.  For example, in the
    directory "<directory>\bumblebee".

 1. Install Bumblebee in the virtual environment (note that the
    virtual environment's Python executable is used here, instead of the
    system Python):
     - <directory>\Scripts\python.exe <directory>\bumblebee\setup.py develop

 1. Run the Bumblebee test suite:
     - <directory>\Scripts\python.exe <directory>\bumblebee\setup.py test

Note that commands given above assumes that Python v2.6 is installed in
the location "C:\Python26".
