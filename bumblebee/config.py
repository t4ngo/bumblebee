
import sys
import logging
import os.path
import pyutilib.component.core
import pyutilib.component.config
from win32com.shell             import shell, shellcon


#===========================================================================

log = logging.getLogger(__name__)


#===========================================================================

class Config(object):
    """
        Main Bumblebee configuration class.

    """

    def __init__(self):
        self._found_config_path = None

    def get_config_path(self):
        """ Returns absolute path to configuration file. """
        # If a config file was already found earlier, return its path.
        if self._found_config_path:
            return self._found_config_path

        # If no config file found yet, look for one.
        # First, look for a config file in the local directory.
        local_directory = os.path.realpath(os.path.dirname(sys.argv[0]))
        local_path = os.path.join(local_directory, "Bumblebee.ini")
        if os.path.isfile(local_path):
            return local_path

        # Second, look for a config file in the system local
        #  app data directory.
        folder_id = shellcon.CSIDL_LOCAL_APPDATA
        system_directory = shell.SHGetFolderPath(0, folder_id, 0, 0)
        system_path = os.path.join(system_directory,
                                   "Bumblebee", "Bumblebee.ini")
        return system_path

    def load_default_config(self):
        """ Loads a built-in, default configuration. """
        log.debug("Loading default config.")
        env_name = "Bumblebee"
        self._environment = pyutilib.component.core.PluginEnvironment(env_name)
        pyutilib.component.core.PluginGlobals.push_env(self._environment)
        self._config = pyutilib.component.config.Configuration()

    def load_config(self):
        """
            Loads configuration from file, if the file is present.

            :returns:   True if configuration loaded;
                        False if configuration not loaded.

        """

        path = self.get_config_path()
        log.info("Loading config from {0}.".format(path))

        try:
            config_file = open(path)
        except IOError, e:
            if e.errno == 2:  # No such file or directory.
                log.warning("Config file ({0}) not found."
                            "".format(path))
                return False
            else:             # Other IOError types.
                log.exception("Failed to open config file ({0}):"
                              " {1}".format(path, e))
                raise

        env_name = "Bumblebee"
        self._environment = pyutilib.component.core.PluginEnvironment(env_name)
        pyutilib.component.core.PluginGlobals.push_env(self._environment)
        self._config = pyutilib.component.config.Configuration()
        self._config.load(path)

        return True

    def save_config(self):
        """ Saves current configuration to disk. """
        config_path = self._open_config_file_for_writing()
        self._config.save(config_path)

    def _open_config_file_for_writing(self):
        """ Saves current configuration to disk. """

        config_path = self.get_config_path()

        # Attempt to open the file directly, and handle any errors
        #  if that fails.
        try:
            open(config_path, "w").close()
            return config_path
        except IOError, e:
            if e.errno == 2:  # No such file or directory.
                log.warning("Config file ({0}) not found."
                            "".format(config_path))
            else:             # Other IOError types.
                log.exception("Failed to open config file ({0}):"
                              " {1}".format(config_path, e))
                raise

        # Create the Bumblebee local app data directory, if not found.
        config_directory = os.path.dirname(config_path)
        if not os.path.isdir(config_directory):
            log.warning("Creating local app data directory ({0})."
                        "".format(config_directory))
            try:
                os.makedirs(config_directory)
            except Exception, e:
                log.exception("Failed to create local app data"
                              " directory ({0}): {1}"
                              "".format(config_directory, e))
                raise

        # Re-attempts to open the files; failure is now nonrecoverable.
        try:
            open(config_path, "w").close()
            return config_path
        except Exception, e:
            log.exception("Failed to open config file ({0}):"
                          " {1}".format(path, e))
            raise

    def load_or_create_config(self):
        """
            Loads configuration from file, or creates it if not found.

        """

        if self.load_config():
            return
        self.load_default_config()
        self.save_config()
