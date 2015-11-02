

# Available debug categories.
DEBUG_CATEGORIES = {
    'architects': False,
    'callbacks': False,
    'controllers': False,
    'drivers': False,
    'emitters': False,
    'imap': False,
    'managers': False,
    'workers': False,
    'all': False,
    }

# Default categories for the 'all' keyword.
DEFAULT_DEBUG_CATEGORIES = {
    'architects': True,
    'callbacks': True,
    'controllers': True,
    'drivers': True,
    'emitters': True,
    'imap': True,
    'managers': True,
    'workers': True,
    }

ARC = 'architects'
CLB = 'callbacks'
CTL = 'controllers'
DRV = 'drivers'
EMT = 'emitters'
MGR = 'managers'
WRK = 'workers'

IMAP = 'imap'


# Time to sleep for a response of another worker. This value is used by the edmp
# module where appropriate. This allows not eating too much CPU.
#TODO: expose to the rascal.
SLEEP = 0.02
