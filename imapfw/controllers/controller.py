# The MIT License (MIT)
#
# Copyright (c) 2015, Nicolas Sebrecht & contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""

A controller is defined on a repository to control its end-driver.

Controllers have the same public interface as the drivers. Each responds like a
driver, does its job and relays the requests (and results) to (or from) the
underlying driver.

Controllers can be chained to each others so that the flows pass through each.

They can either be passive or active. Passive controllers follow-up the requests
as-is and returns the unchanged results. Active controllers changes the flow to
achieve their tasks. IOW, each controller can only view what the underlying
controller accepts to show. Hence, the order in the chain is important.

The controller base "Controller" is a passive controller (see code below).

The chain of controller is defined in the rascal.


SCHEMATIC OVERVIEW EXAMPLE (right side)
---------------------------------------

                 (filter)      (tracker)      (encoder)
+----------+   +----------+   +----------+   +----------+   +----------+
|          |-->|          |-->|          |-->|          |-->|          |
|  engine  |   |controller+   |controller|   |controller|   |  driver  |
|          |<--|          |<--|          |<--|          |<--|          |
+----------+   +----------+   +----------+   +----------+   +----------+
                 [active]       [passive]      [active]
                              notifications,  UTF-7/UTF-8
                                debugging


"""

class Controller(object):

    conf = {}

    def fw_initController(self, conf):
        self.conf = conf

    def fw_drive(self, driver):
        self.driver = driver

    def __getattr__(self, name):
        return getattr(self.driver, name)


