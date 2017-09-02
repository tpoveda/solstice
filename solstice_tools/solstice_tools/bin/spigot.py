#!/usr/bin/env python

import sys
import struct, json
import socket

import imp

DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 14002

class SpigotClient():
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._keep_open = False
        self._host = host
        self._port = port

    def __enter__(self):
        self._keep_open = True
        self._connect()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._keep_open = False
        self._disconnect()

    def _connect(self):
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((self._host, self._port))

    def _disconnect(self):
        self._s.close()
        self._s = None

    def execute(self, command_action='do', command_name='help', payload='{"topic":"all"}'):

        ## Data is sent as a JSON
        #
        json_command = json.dumps({
            'CommandAction': command_action,
            'CommandName': command_name,
            'ArgsJson': payload,
        })

        if not self._keep_open: self._connect()
        
        if self._s is None:
            # Throw?
            return

        ## First 32 bits provide the number of bytes in the subsequent message
        #
        self._s.send(struct.pack('!I', len(json_command)))
        self._s.send(json_command)

        ## Expect an acknowledgment - TODO: Have the response's first 4 bytes be the 
        ## length of the response so we correctly handle responses with no length.
        #
        response = self._s.recv(1024)

        if not self._keep_open: self._disconnect()

        return response

class SpigotImporter(object):
    modules = set()
    modules_fetched = False

    def find_module(self, fullname, path=None):
        ## Check cache
        #
        if fullname in SpigotImporter.modules or '%s.__init__' % fullname in SpigotImporter.modules:
            return self
        elif SpigotImporter.modules_fetched:
            return None

        ## Fetch all available modules and their packages
        #
        json_modules = SpigotClient().execute(
            command_name = "listPythonModules",
            payload = "{}",
        ).replace('\r', '')

        ## Create cache
        #
        SpigotImporter.modules = set(json.loads(json_modules)['modules'])
        SpigotImporter.modules_fetched = True

        ## Check cache
        #
        if fullname in SpigotImporter.modules or '%s.__init__' % fullname in SpigotImporter.modules:
            return self
        else:
            return None

    def load_module(self, fullname):
        faucet_client = SpigotClient()

        ## Check cache
        #
        if fullname in sys.modules:
            return sys.modules[fullname]

        ## Create module/package
        #
        mod = imp.new_module(fullname)
        mod.__file__ = "<%s>" % self.__class__.__name__
        mod.__loader__ = self

        ## Fetch module/package init code from Spigot
        #
        code = faucet_client.execute(
            command_name = "getPythonPackage" if '%s.__init__' % fullname in SpigotImporter.modules else "getPythonModule",
            payload = json.dumps({ "fullname": fullname }),
        ).replace('\r', '')

        ## Code represents a package
        #
        if code[:2] == 'P:':
            mod.__path__ = []
            mod.__package__ = fullname

        ## Code represents a module
        #
        else:
            mod.__package__ = fullname.rpartition('.')[0]

        ## Give the module its meat
        #
        exec code[2:] in mod.__dict__

        ## Make it available
        #
        sys.modules[fullname] = mod

        return mod

sys.meta_path = [SpigotImporter()]

if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)
