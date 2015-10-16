
from .controller import Controller

#TODO
class Duplicate(Controller):
    """Controller to duplicate writes to another driver."""

    conf = None

    def fw_init(self, driver, duplicateDriver, ui):
        super(NameTrans, self).fw_init(driver)
        self.duplicateDriver = duplicateDriver #TODO: setup driver...
        self._ui = ui

        self.mode = self.conf.get('exception').lower() # fatal, warn or pass.

    def __getattr__(self, name):
        raise AttributeError("method '%s' missing in Duplicate controller"% name)

    def _call(self, name, *args, **kwargs):
        try:
            values = getattr(self.duplicateDriver, name)(*args, **kwargs)
        except Exception as e:
            if self.mode == 'pass':
                pass
            elif self.mode == 'warn':
                self._ui.warn('TODO: warning not implemented')
            else:
                raise
        finally:
            return getattr(self.driver, name)(*args, **kwargs)

    def connect(self):
            values = self._call('connect')

    #TODO: implement DriverInterface.

