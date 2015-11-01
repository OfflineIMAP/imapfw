# Copyright (C) 2015, Nicolas Sebrecht and contributors.
#
#   The MIT License (MIT)
#
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to deal
#   in the Software without restriction, including without limitation the rights
#   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#   copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#   THE SOFTWARE.


__productname__ = 'Imapfw'
__version__     = "0.014"
__copyright__   = "Copyright 2015 Nicolas Sebrecht & contributors"
__author__      = "Nicolas Sebrecht"
__author_email__= "nicolas.s-dev@laposte.net"
__description__ = "Easy IMAP framework for mail access and synchronization"
__license__  = "The MIT License (MIT)"
__homepage__ = "http://github.com/OfflineIMAP/imapfw"


from imapfw.init import Imapfw # Avoid circular dependencies.
from imapfw import runtime # Import this module ASAP.
