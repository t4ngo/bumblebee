
from __future__ import absolute_import

import logging
from pyutilib.component.core        import (Plugin, SingletonPlugin,
                                            ExtensionPoint, implements)
from pyutilib.component.config      import declare_option
from bumblebee.system.interfaces    import ISystemParticipant


#===========================================================================

log = logging.getLogger(__name__)


#===========================================================================

class DragonflySystemParticipant(SingletonPlugin):

    implements(ISystemParticipant)
    declare_option("engine", section="Dragonfly", default="auto")

    def __init__(self):
        self._engine = None
        self._loaded_engine_name = None

    #-----------------------------------------------------------------------
    # ISystemParticipant methods.

    def startup(self):
        self.shutdown()
        self._connect_engine()

    def shutdown(self):
        if self._engine:
            self._engine.disconnect()
        self._engine = None
        self._loaded_engine_name = None

    def config_changed(self):
        if self.engine == self._loaded_engine_name:
            # No change, return immediately.
            log.info("No change.")
            return

        self.shutdown()
        self.startup()

    #-----------------------------------------------------------------------
    # Internal methods.

    def _resolve_engine_name(self, engine_name):
        if not engine_name or engine_name == "auto":
            return None
        return engine_name

    def _connect_engine(self):
        engine_name = self._resolve_engine_name(self.engine)

        try:
            log.info("Importing Dragonfly library.")
            import dragonfly

            log.info("Locating SR engine {0}."
                     "".format(engine_name or "(automatic selection)"))
            self._engine = dragonfly.get_engine(engine_name)

            log.info("Connecting to SR engine {0}.".format(self._engine))
            self._engine.connect()
        except Exception, e:
            log.exception("Error during Dragonfly setup: {0}".format(e))
            raise

        self._loaded_engine_name = self.engine
