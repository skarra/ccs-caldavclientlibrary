##
# Copyright (c) 2007-2016 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##

from caldavclientlibrary.browser.command import Command, CommandError
from caldavclientlibrary.protocol.url import URL


class Cmd(Command):

    def __init__(self):
        super(Command, self).__init__()
        self.cmds = ("emptytrash",)

    def execute(self, cmdname, options):

        principal = self.shell.account.getPrincipal()
        homeset = principal.homeset
        if not homeset:
            print "No calendar home set found for %s" % (principal.principalPath,)
            raise CommandError

        homepath = homeset[0].path

        resource = URL(url="{}?action=emptytrash".format(homepath))
        self.shell.account.session.writeData(resource, None, None, method="POST")

        return True

    def usage(self, name):
        return """Usage: %s
""" % (name,)

    def helpDescription(self):
        return "Empties the trash of the current user."
