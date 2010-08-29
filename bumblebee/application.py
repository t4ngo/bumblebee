
import logging
import os.path
import wx
import dragonfly
import pyutilib.component.core
import pyutilib.component.config

from .gui.main_frame            import MainFrame
from .command.interface         import ICommandSetLoader


#===========================================================================

class BumblebeeApp(wx.App):
    """
        Main Bumblebee application class.

        This is a `wx.App` derived class which drives the rest of the
        Bumblebee application.

        This class also manages the connection between Bumblebee and the
        speech recognition engine.  See `_connect_to_sr_engine` for
        implementation details.

    """

    _log = logging.getLogger("BumblebeeApp")

    #-----------------------------------------------------------------------
    # Overridden wx.App methods.

    def OnInit(self):
        # Setup application logging.
        self._log.debug("OnInit()")

        # Create main GUI frame.
        self._main_frame = MainFrame(None, -1, "Bumblebee")

        # Schedule further initialization.
        wx.CallLater(1, self._initialize_pca)
        wx.CallLater(2, self._connect_to_sr_engine)

        # Return true to indicate that initialization was successful.
        return True

    def OnExit(self):
        self._engine.disconnect()
        import natlink
        natlink.natDisconnect()

    #-----------------------------------------------------------------------
    # Internal methods.

    def _initialize_pca(self):
        self._log.debug("_initialize_pca()")

        env_name = "Bumblebee"
        self._env = pyutilib.component.core.PluginEnvironment(env_name)
        pyutilib.component.core.PluginGlobals.push_env(self._env)

        directory = os.path.split(__file__)[0]
        self._config_path = os.path.join(directory, "bumblebee.ini")
        self._log.info("Loading Bumblebee config from {0}"
                        "".format(self._config_path))

        self._initialize_loaders()

        self._config = pyutilib.component.config.Configuration()
        self._config.load(self._config_path)

    def _connect_to_sr_engine(self):
        self._log.debug("_connect_to_sr_engine()")

        self._setup_dragonfly_logging()

        self._engine = dragonfly.get_engine()
        import natlink
        natlink.natConnect(1)
        self._engine.connect()

    def _setup_dragonfly_logging(self):
        self._log.debug("_setup_dragonfly_logging()")

        log_levels = {
                      "compound.parse":       logging.INFO,
                      "engine":               logging.INFO,
                      "grammar.begin":        logging.INFO,
                      "grammar.decode":       logging.INFO,
                      "dictation.formatter":  logging.INFO,
                     }

        for name, level in log_levels.items():
            log = logging.getLogger(name)
            log.setLevel(level)

    def _initialize_loaders(self):
        self._log.debug("_initialize_loaders()")

        # Import loaders so that they are registered in the PCA.
        import bumblebee.command.legacy_loader

        # Setup infrastructure for periodic updating of loaders.
        loaders = pyutilib.component.core.ExtensionPoint(ICommandSetLoader)

        def on_timer(event):
            self._config.load(self._config_path)
            for loader in loaders:
                loader.update()
        self.Bind(wx.EVT_TIMER, on_timer)

        # Timer object must be bound to self, because otherwise it would
        #  be garbage collected and therefore destroyed without ever
        #  firing.
        self._timer = wx.Timer(self)
        self._timer.Start(500, oneShot=False)


#===========================================================================

def setup_logging():
    """ Set up the Python logging infrastructure to log to a file. """

    # Set root log level.
    log = logging.getLogger("")
    log.setLevel(logging.DEBUG)

    # Register a log file handler.
    log_path = __file__ + "-log.txt"
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)


def run_application():
    """
        Helper function for running the Bumblebee application with
        file-based logging and in a try-except block to report any
        bootstrapping errors.

    """

    log = logging.getLogger("run_application")
    setup_logging()
    try:
        application = BumblebeeApp()
        application.MainLoop()
    except Exception, e:
        log.exception("Exception: %s", e)
        raise
