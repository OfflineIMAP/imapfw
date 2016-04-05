# The MIT License (MIT).
# Copyright (C) 2015-2016, Nicolas Sebrecht and contributors.


__productname__ = 'Imapfw'
__version__     = "0.025"
__copyright__   = "Copyright 2015-2016 Nicolas Sebrecht & contributors"
__author__      = "Nicolas Sebrecht"
__author_email__= "nicolas.s-dev@laposte.net"
__description__ = "Framework for working with IMAP and emails"
__license__  = "The MIT License (MIT)"
__homepage__ = "http://github.com/OfflineIMAP/imapfw"


from imapfw.init import Imapfw # Avoid circular dependencies.
from imapfw import runtime # Import this module ASAP.
