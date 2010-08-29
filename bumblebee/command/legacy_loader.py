
import logging
import os.path
from pyutilib.component.core    import (Plugin, SingletonPlugin,
                                        ExtensionPoint, implements)
from pyutilib.component.config  import declare_option

from .interface                 import (ICommandSetLoader, ICommandSet,
                                        ICommandSetObserver)


#===========================================================================

class LegacyDirectoryLoader(SingletonPlugin):

    implements(ICommandSetLoader)
    declare_option("directories", section="legacy_loader")

    _log = logging.getLogger("LegacyDirectoryLoader")

    def __init__(self):
        self._modules = {}
        self._directories = []
        self._directories_config = None

    def _parse_directories_config(self):
        # If config has not changed, return immediately.
        if self._directories_config == self.directories:
            return self._directories

        self._log.info("Config option directories has changed:"
                       " {0!r}".format(self.directories))

        directories = []
        for line in self.directories.splitlines():
            line = line.strip()

            # Skip blank lines and comments.
            if not line or line.startswith("#"):
                continue

            directory = os.path.abspath(line)
            if not os.path.isdir(directory):
                self._log.error("Not a directory: {0}".format(directory))
                continue

            directories.append(directory)

        self._directories_config = self.directories
        self._directories = directories
        self._log.debug("Loading command modules from these directories:")
        for directory in directories:
            self._log.debug(" - {0}".format(directory))
        return directories

    def update(self):
        # Parse directories configuration.
        directories = self._parse_directories_config()

        valid_paths = []
        for directory in directories:
            valid_paths.extend(self._get_valid_paths(directory))

        # Remove any deleted modules.
        for path, module in self._modules.items():
            if path not in valid_paths:
                del self._modules[path]
                module.unload()

        # Add any new modules.
        for path in valid_paths:
            if path not in self._modules:
                module = LegacyCommandSet(path)
                module.load()
                self._modules[path] = module
            # Should check module freshness here.
            #else:
            #    module = self._modules[path]

    def _get_valid_paths(self, directory):
        valid_paths = []
        for filename in os.listdir(directory):
            path = os.path.abspath(os.path.join(directory, filename))
            if not os.path.isfile(path):
                continue
            if not os.path.splitext(path)[1] == ".py":
                continue
            valid_paths.append(path)
        return valid_paths


#---------------------------------------------------------------------------
# Command set base class.

class CommandSetBase(Plugin):

    implements(ICommandSet)
    observers = ExtensionPoint(ICommandSetObserver)

    _log = logging.getLogger("CommandSet")

    def after_load(self):
        for observer in self.observers:
            observer.loaded_command_set(self)

    def after_unload(self):
        self.deactivate()
        for observer in self.observers:
            observer.unloaded_command_set(self)


#---------------------------------------------------------------------------
# Legacy command set class; wraps a single NatLink-style command-module.

class LegacyCommandSet(CommandSetBase):

    _log = logging.getLogger("LegacyCommandSet")

    def __init__(self, path):
        self._path = path
        self._short_path = os.path.basename(self._path)
        self._namespace = None
        self._loaded = False

    def __str__(self):
        return "<{0}({1})>".format(self.__class__.__name__,
                                   self._short_path)

    #-----------------------------------------------------------------------
    # ICommandSet methods.

    def get_name_description(self):
        name = "{0} (legacy)".format(self._short_path)
        return (name, "")

    def get_commands(self):
        return ()

    def load(self):
        self._log.debug("Loading module {0}".format(self._path))

        # Prepare namespace in which to execute the command module.
        namespace = {}
        namespace["__file__"] = self._path

        # Attempt to execute the module; handle any exceptions.
        try:
            execfile(self._path, namespace)
        except Exception, e:
            self._log.exception("Error loading module: {0}"
                                "".format(e))
            self._loaded = False
            return

        self._loaded = True
        self._namespace = namespace

        self.after_load()

    def unload(self):
        unload_func = self._namespace.get("unload", None)
        if callable(unload_func):
            unload_func()
            self._namespace = None
            self._loaded = False
        else:
            self._log.warning("No unload() function in legacy module"
                              " {0}".format(self._short_path))
            self._namespace = None
            self._loaded = False

        self.after_unload()
