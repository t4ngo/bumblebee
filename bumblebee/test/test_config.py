
import sys
import logging
import unittest
import os
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

            # Only local config, after having found system config
            #  -> remembers system config.
            self._delete_config()
            open(local_path, "w").close()
            config_path = self.config.get_config_path()
            self.assertEquals(system_path.lower(), config_path.lower())

            # Only local config -> finds local config.
            self.config = bumblebee.config.Config()
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
        self.assertFalse(self.config.load())

        # Verify that the first load hasn't changed anything.
        self.assertFalse(self.config.load())

        # Cleanup.
        self._delete_config()

    def test_load_or_create(self):
        """ Verify that Config.load_or_create() works. """

        # Remove any old config files.
        self._delete_config()
        self.assertFalse(os.path.exists(self._get_local_path()))
        self.assertFalse(os.path.exists(self._get_system_path()))

        # Verify that load_or_create() creates the system config.
        self.config.load_or_create()
        self.assertFalse(os.path.exists(self._get_local_path()))
        self.assertTrue(os.path.exists(self._get_system_path()))

        # Cleanup.
        self._delete_config()

    def test_reload_if_modified(self):
        """ Verify that Config.reload_if_modified() works. """

        # Remove any old config files.
        self._delete_config()
        self.assertFalse(os.path.exists(self._get_local_path()))
        self.assertFalse(os.path.exists(self._get_system_path()))

        # Verify that reload_if_modified() creates a new file.
        reloaded = self.config.reload_if_modified()
        self.assertTrue(reloaded)
        self.assertFalse(os.path.exists(self._get_local_path()))
        self.assertTrue(os.path.exists(self._get_system_path()))
        config_path = self.config.get_config_path()
        self.assertEquals(self._get_system_path(), config_path)

        # Verify that reload_if_modified() doesn't reload if not modified.
        reloaded = self.config.reload_if_modified()
        self.assertFalse(reloaded)

        # Verify that reload_if_modified() reloads if modified.
        os.utime(config_path, None)
        reloaded = self.config.reload_if_modified()
        self.assertTrue(reloaded)

        # Verify that reload_if_modified() deals with a deleted file.
        self._delete_config()
        reloaded = self.config.reload_if_modified()
        self.assertTrue(reloaded)
        self.assertFalse(os.path.exists(self._get_local_path()))
        self.assertTrue(os.path.exists(self._get_system_path()))

        # Cleanup.
        self._delete_config()

    #-----------------------------------------------------------------------
    # Utility methods.

    def _get_local_directory(self):
        return os.path.realpath(os.path.dirname(sys.argv[0]))

    def _get_local_path(self):
        return os.path.join(self._get_local_directory(), "Bumblebee.ini")

    def _get_system_directory(self):
        folder_id = shellcon.CSIDL_LOCAL_APPDATA
        appdata_directory = shell.SHGetFolderPath(0, folder_id, 0, 0)
        return os.path.join(appdata_directory, "Bumblebee")

    def _get_system_path(self):
        return os.path.join(self._get_system_directory(), "Bumblebee.ini")

    def _delete_config(self):
        config_paths = [
                        self._get_local_path(),
                        self._get_system_path(),
                       ]
        for config_path in config_paths:
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
