#!/usr/bin/env python

import sys
import struct, json
import socket
import logging
import threading
import time


DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 14002

PROTOCOL_BYTES = 0x53504754 # "SPGT"


class SpigotClient():
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self._host = host
        self._port = port 
        self._connected = False
        self._listenServ = None

    def listen(self, appId, handler):
        logging.info("Starting listen thread...")

        threading.Thread(
                target=self._pullMessages, 
                args=(appId, handler)
            ).start()

    def _connectAndRegister(self, appId):
        logging.info("Connecting...")

        if self._listenServ is not None:
            self._listenServ.close()

        ## We will listen on an arbitrary port, and tell the other end what that
        ## port is.
        #
        self._listenServ = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listenServ.bind(("127.0.0.1", 0)) # let the system pick a port...  
        local_addr, port = self._listenServ.getsockname() #... and tell us what it is
        self._listenServ.listen(1)
        logging.info("listening on %s:%d" % (local_addr, port))

        ## Register our new socket with Spigot so we may receive Spigot messages.
        #
        # TODO: retry if connection fails (say, because spigot is restarting)
        self._connected = False
        numRetries = 0
        maxRetries = 30
        retryDelay = 3 # seconds
        while not self._connected and numRetries <= maxRetries:
            try:
                logging.info(self.execute(command_action='do', command_name='registerApp', payload=json.dumps({
                    "appId": appId,
                    "talkBackAddress": "%s:%d" % (local_addr, port),
                })))
                self._connected = True
            except socket.error as e:
                logging.info("Failed to connect, retrying: %r" % e)
                time.sleep(retryDelay)
                numRetries = numRetries + 1

        if not self._connected:
            logging.info("Giving up")
            self._listenServ.close()
            return None
        logging.info("Pulling messages")

        ## Accept the connection we assume is Spigot.
        #
        listeningSocket, remote_addr = self._listenServ.accept()
        listeningSocket.setblocking(True)
        logging.info("Accepted connection from: %s" % str(remote_addr))
        return listeningSocket

    def _pullMessages(self, appId, handlerFunc):

        listeningSocket = self._connectAndRegister(appId)
        if listeningSocket is None:
            return

        ## Wait for messages.
        #
        while True:
            try:
                response_length_raw = listeningSocket.recv(4)
                if response_length_raw is None or len(response_length_raw) == 0:
                    raise socket.error
                response_length, = struct.unpack('>I', response_length_raw)
                logging.info("Preparing to receive byte count: %d" % response_length)
     
                response_raw = listeningSocket.recv(int(response_length))
                if response_raw is None or len(response_raw) == 0:
                    raise socket.error
                logging.info("Received: %r" % response_raw)

                handlerFunc(response_raw)
            except socket.error:
                try:
                    listeningSocket.close()
                except:
                    pass
                listeningSocket = self._connectAndRegister(appId)
                if listeningSocket is None:
                    return

    def execute(self, command_action='do', command_name='sayHi', payload='{"lang":"french"}'):

        ## Data is sent as a JSON
        #
        json_command = json.dumps({
            'CommandAction': command_action,
            'CommandName': command_name,
            'ArgsJson': payload,
        })

        #logging.info("Opening execution socket at %s:%s" % (self._host, self._port))
        sendingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sendingSocket.connect((self._host, self._port))
        #logging.info("Execution socket opened")

        ## First 32 bits provide the protocol, the next 32 bits
        ## provide the number of bytes in the subsequent message.
        #
        sendingSocket.send(struct.pack('!I', PROTOCOL_BYTES))
        sendingSocket.send(struct.pack('!I', len(json_command)))
        sendingSocket.send(json_command)

        ##
        ## Block until we receive a response.
        ##

        ## TODO: the first thing we should ask for is a status, so we can shift our
        #        attention to pulling error data
        
        ## Expect an acknowledgment.
        #
        response_length_raw = sendingSocket.recv(4)
        response_length, = struct.unpack('!I', response_length_raw)
        response = sendingSocket.recv(response_length)  

        sendingSocket.close()

        return response


if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)
