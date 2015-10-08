

__VERSION__ = 0.1


##########
# GLOBAL #
##########

#
# The main configuration options are set in this dict.
#
MainConf = {

    # Concurrency backend to use for the workers:
    # - multiprocessing;
    # - threading;
    #
    # Because most of the wait time is due to I/O (disk and network, there
    # should be no visible performance differences.
    #
    # Be aware that this rascal module gets COPIED into each worker. This means
    # that any changed ressource (including global variable) after the call to
    # configure() won't be updated for all the running code.
    'concurrency_backend': 'multiprocessing',

    # The number of concurrent workers for the accounts. Default is the number
    # of accounts to sync.
    'max_sync_accounts': 2,
}

# UI allows to send messages to the UI library of the framework. Interface is
# quite the same as the logging library:
# - critical(*args)
# - debug(*args)
# - error(*args)
# - exception(*args)
# - info(*args)
# - warn(*args)
UI = None

# The configure method is called once the environment is ready, way after the
# rascal is loaded.
def configure(ui):
    global UI
    UI = ui # Let the framework update the UI so it can be turned thread-safe.


#########
# Hooks #
#########


# The hook started at the beginning of the process once initialization is done.
def preHook(actionName, params):
    UI.info("Running preHook: starting action %s with params %s"%
        (actionName, params))
    return actionName, params


# The hook started at the end of the process when no exception is raised.
def postHook():
    UI.info('Runing postHook')


# This hook is started on unexpected exception.
# Arguments:
# - error: the exception error.
# Don't call sys.exit() here or you will loose the correct exit code.
def exceptionHook(error):
    UI.critical("Running exceptionHook: an exception was catched!")
    #import traceback, sys
    #UI.exception(error)
    #traceback.print_exc(file=sys.stdout)


from imapfw.api import actions, engines, types, drivers
# Support for contributor's backends. ,-)
#from imapfw.api import contrib



###########
# DRIVERS #
###########

# The Maildir driver provides low-level "read/write" abilities to a local
# Maildir. This is about HOW to handle the maildir.
#
# Optional. drivers.Maildir is the standard Maildir driver.
class MaildirDriverExample(drivers.Maildir):
    def write(self, mail):
        UI.info("will write new mail [%s]"% mail.getUID())
        return mail # Let's write it!

    def read(self, mail):
        return mail

    def connect(self):
        pass # noop

    def getFolders(self):
        return ['sample', 'of', 'static', 'local', 'folder', 'list']


# The IMAP driver connects to a remote server and provides low-level
# "read/write" abilities.  It seats just in front of the remote server.
# This is about HOW to interact with the remote IMAP.
#
# Optional. drivers.Imap is the standard IMAP driver.

class ImapDriverExample(drivers.Imap):
    def connect(self, username, password):
        return True

    def download(self, uid_list):
        new_list = []
        ignore_list = []
        header_dict = self.getHeaders(uid_list)
        for uid, header in header_dict:
            if header.has('X-ignore'):
                ignore_list.append(uid)
            else:
                new_list.append(uid)
        UI.info('ignoring: %s'% ', '.join(ignore_list))
        return new_list



################
# REPOSITORIES #
################

ImapExampleConf = {
    'dns':      'imap.gmail.com',
    'port':     '143',
    'username': 'myname',
    'max_connections': 2,
}

MaildirExampleConf = {
    'path': '~/Maildir',
    'max_connections': 2,
}

class MaildirRepositoryExample(types.Maildir):

    conf = MaildirExampleConf
    driver = drivers.Maildir # Default: drivers.Maildir.


class ImapRepositoryExample(types.Imap):

    conf = ImapExampleConf
    driver = ImapDriverExample # Default: drivers.Imap.

    def _getPassword(self):
        return self.conf.password

    def credentials(self):
        return self.conf.username, self._getPassword()

    def search(self, server, uid_list, conditions):
        title = mail.getTitle()

        if title.startswith('spam'):
            mail.deleteRemote('deleting spam')

        if title.startswith('offlineimap'):
            mail.setTitle("filtered: %s"% title)
            mail.moveTo('INBOX.offlineimap') # IMAP MOVE.

        return # Continue proceeding to the folder.


# Defines a IMAP controller: this is the WHAT to do.
class ImapExampleController(controllers.Imap):
    def getFolders(self):
        return ['sample', 'of', 'static', 'remote', 'folder', 'list']



############
# ACCOUNTS #
############

class AccountExample(types.Account):
    left = MaildirRepositoryExample
    right = ImapRepositoryExample

    # Optional. The folders considered for a sync.
    # Arguments:
    # - folder_list: list of folder names to sync.
    # Returned values: the new list of folders to sync.
    def syncFolders(self, foldersList):
        return ['folderA', 'folderB', 'folderC']


# vim: syntax=python ts=4 expandtab :
