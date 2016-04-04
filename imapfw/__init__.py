# The MIT License (MIT).
# Copyright (C) 2015-2016, Nicolas Sebrecht and contributors.


__productname__ = 'Imapfw'
__version__     = "0.024"
__copyright__   = "Copyright 2016 Nicolas Sebrecht & contributors"
__author__      = "Nicolas Sebrecht"
__author_email__= "nicolas.s-dev@laposte.net"
__description__ = "Easy IMAP framework for mail access and synchronization"
__license__  = "The MIT License (MIT)"
__homepage__ = "http://github.com/OfflineIMAP/imapfw"


from imapfw.init import Imapfw # Avoid circular dependencies.
from imapfw import runtime # Import this module ASAP.
