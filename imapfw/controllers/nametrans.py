
from .controller import Controller

#TODO
class NameTrans(Controller):
    """Controller to change the folder names."""

    conf = None

    def fw_init(self, driver):
        super(NameTrans, self).fw_init(driver)
        self._toDriverTrans = self.conf.get('toDriverTrans')
        self._fromDriverTrans = self.conf.get('fromDriverTrans')
        self._encoding = self.conf.get('encoding')

    def getFolders(self):
        folders = self.driver.getFolders()
        for folder in folders:
            name = folder.getName(self._encoding)
            transName = self._fromDriverTrans(name)
            if name != transName:
                folder.setName(transName, self._encoding)
        return folders

    def select(self, folder):
        folder.setName(folder.getName(self._ancoding), self._encoding)
        return self.driver.select(folder)
