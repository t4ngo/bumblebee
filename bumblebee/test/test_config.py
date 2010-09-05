
import sys
import logging
import unittest
import os.path
import bumblebee.config
from win32com.shell import shell, shellcon


#===========================================================================

log = logging.getLogger(__name__)


#===========================================================================

class TestConfig(unittest.TestCase):

    def setUp(self):
        self.config = bumblebee.config.Config()

    def test_path_search_order(self):
        """ Verify that config path search order is correct. """
        # Prepare local and system directories.
        local_directory   = self._get_local_directory()
        local_path        = os.path.join(local_directory, "Bumblebee.ini")
        system_directory  = self._get_system_directory()
        system_path       = os.path.join(system_directory, "Bumblebee.ini")
        self.assertTrue(os.path.isdir(local_directory))
        self.assertTrue(os.path.isdir(system_directory))

        try:
            # Only system config -> finds system config.
            self._delete_config()
            open(system_path, "w").close()
            config_path = self.config.get_config_path()
            self.assertEquals(system_path.lower(), config_path.lower())

            # Only local config -> finds local config.
            self._delete_config()
            open(local_path, "w").close()
            config_path = self.config.get_config_path()
            self.assertEquals(local_path.lower(), config_path.lower())

            # Both system and local configs -> finds local config.
            open(system_path, "w").close()
            config_path = self.config.get_config_path()
            self.assertEquals(local_path.lower(), config_path.lower())

        finally:
            self._delete_config()

    def test_load_returns_false_if_nonexistent(self):
        """ Verify that Config.load() returns False if file not found. """
        self._delete_config()
        self.assertFalse(self.config.load_config())

        # Verify that the first load hasn't changed anything.
        self.assertFalse(self.config.load_config())

    def test_load_or_create_config(self):
        """ Verify that Config.load_or_create_config() works. """
        self._delete_config()
        self.config.load_or_create_config()

    #-----------------------------------------------------------------------
    # Utility methods.

    def _get_local_directory(self):
        return os.path.realpath(os.path.dirname(sys.argv[0]))

    def _get_system_directory(self):
        folder_id = shellcon.CSIDL_LOCAL_APPDATA
        appdata_directory = shell.SHGetFolderPath(0, folder_id, 0, 0)
        return os.path.join(appdata_directory, "Bumblebee")

    def _delete_config(self):
        config_dirs = [
                       self._get_local_directory(),
                       self._get_system_directory(),
                      ]
        for config_dir in config_dirs:
            config_path = os.path.join(config_dir, "Bumblebee.ini")
            try:
                os.remove(config_path)
            except WindowsError, e:
                # Ignore file-not-found errors, but re-raise others.
                if e.errno != 2:
                    raise
                log.debug("Remove config file: file not found {0}."
                          "".format(config_path))
            else:
                log.debug("Remove config file: deleted {0}."
                          "".format(config_path))
