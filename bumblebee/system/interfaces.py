
from pyutilib.component.core    import Interface


#===========================================================================

class ISystemParticipant(Interface):

    def startup(self):
        """
            Starts up the system participant.

            This method is called on system startup.

        """

    def shutdown(self):
        """
            Shuts down the system participant.

            This method is called on system shutdown.

        """

    def config_changed(self):
        """
            Handles configuration changes.

            This method is called when the configuration has been
            modified.

        """
