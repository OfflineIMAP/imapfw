
from ..drivers.driver import DriverInterface


class Controller(DriverInterface):
    def fw_init(self, driver):
        self.driver = driver

    def __getattr__(self, name):
        return getattr(self.driver, name)


