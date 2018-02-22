#!/usr/bin/env python

import sys
import struct, json
import socket
import logging
import threading

import maya.cmds

def getDependencies(cli, cms_uri):
    # Spin the actual request off in a thread, so we can maintain the progress window
    # in the main thread
    event = threading.Event()
    threading.Thread(
        target=_requestGetDeps,
        args=(cli, cms_uri, event)
        ).start()

    root_file_name = cms_uri.split('__/')[-1]
    msg = "For %s" % root_file_name
    maya.cmds.progressWindow( title="Get Dependencies",
                              progress=0,
                              status=msg,
                              isInterruptable=True)

    try:
        while not event.is_set():
            if maya.cmds.progressWindow(query=True, isCancelled=True):
                rsp = cli.execute(command_action='do', command_name='cancelGetDeps',
                                  payload = '{ "cms_uri" : "%s" }' % cms_uri)
                break
            rsp = cli.execute(command_action='do', command_name='getDepsProgress',
                              payload = '{ "cms_uri" : "%s" }' % cms_uri)
            # Ugh. Really need to nail down our return value protocol for the external
            # interface.
            if type(rsp) == str:
                rsp = json.loads(rsp)
            if type(rsp) == dict and 'inProgress' in rsp:
                for uri in rsp['inProgress']:
                    active = uri.split('__/')[-1]
                    amount = int(rsp['inProgress'][uri])
                    msg = "For %s -> %s" % (root_file_name, active)
                    maya.cmds.progressWindow( edit=True,
                                              progress=amount,
                                              status=msg)
            # This gives us a refresh rate of 4fps. We could do more, except the api
            # is restful, so each progress query is a full on call through the the
            # external interface and spams the log like crazy. So let's dial it back
            # for now until/unless we have a less spammy alternative. If the cancel
            # delay is untenable, we could consider checking for cancel more often.
            event.wait(0.25)
    finally:
        maya.cmds.progressWindow(endProgress=1)

def _requestGetDeps(cli, cms_uri, event):
    rsp = cli.execute(command_action='do', command_name='getDependencies',
                      payload = '{ "cms_uri" : "%s" }' % cms_uri)
    print rsp
    event.set()


if __name__ == "__main__":
    exit_status = main()
    sys.exit(exit_status)
