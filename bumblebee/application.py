
import logging
import os.path
import wx
import dragonfly
from pyutilib.component.core        import PluginEnvironment, ExtensionPoint
from bumblebee.config               import Config
from bumblebee.gui.main_frame       import MainFrame
from bumblebee.command.interfaces   import ICommandSetLoader
from bumblebee.system.interfaces    import ISystemParticipant
from bumblebee.system               import *


#===========================================================================

log = logging.getLogger(__name__)


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

    def __init__(self):
        wx.App.__init__(self)
        self._config = Config()

    #-----------------------------------------------------------------------
    # Overridden wx.App methods.

    def OnInit(self):
        log.debug("OnInit()")

        self._setup_logging()

        # Create main GUI frame.
        self._main_frame = MainFrame(None, -1, "Bumblebee")

        # Schedule further initialization.
        wx.CallLater(1, self._initialize_pca)

        # Return true to indicate that initialization was successful.
        return True

    def OnExit(self):
        self._shutdown_system_participants()

    #-----------------------------------------------------------------------
    # Internal methods.

    def _setup_logging(self):
        log.debug("_setup_logging()")

        log_levels = {
                      "compound.parse":       logging.INFO,
                      "engine":               logging.INFO,
                      "grammar.begin":        logging.INFO,
                      "grammar.decode":       logging.INFO,
                      "dictation.formatter":  logging.INFO,
                      "context.match":        logging.INFO,
                      "grammar.load":         logging.INFO,
                      "action.exec":          logging.INFO,
                     }

        for name, level in log_levels.items():
            this_log = logging.getLogger(name)
            this_log.setLevel(level)

    def _initialize_pca(self):
        log.debug("_initialize_pca()")

        self._initialize_loaders()

        self._config = Config()
        self._config.load_or_create()

        # Schedule further initialization.
        wx.CallLater(1, self._startup_system_participants)

    def _startup_system_participants(self):
        for participant in ExtensionPoint(ISystemParticipant):
            participant.startup()

    def _shutdown_system_participants(self):
        for participant in ExtensionPoint(ISystemParticipant):
            participant.shutdown()

    def _initialize_loaders(self):
        log.debug("_initialize_loaders()")

        # Import loaders so that they are registered in the PCA.
        import bumblebee.command.legacy_loader

        # Setup infrastructure for periodic updating of loaders.
        loaders = ExtensionPoint(ICommandSetLoader)

        def on_timer(event):
            reloaded = self._config.reload_if_modified()
            if reloaded:
                for participant in ExtensionPoint(ISystemParticipant):
                    participant.config_changed()
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

    setup_logging()
    try:
        application = BumblebeeApp()
        application.MainLoop()
    except Exception, e:
        log.exception("Exception: %s", e)
        raise
