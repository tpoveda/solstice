#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_worker.py
# by Tomas Poveda
# Module that contains class to execute tasks in background
# ______________________________________________________________________
# ==================================================================="""

import uuid
from threading import Lock, Condition

from Qt.QtCore import *


class Worker(QThread):
    work_completed = Signal(str, object)
    work_failure = Signal(str, str)

    def __init__(self, app, parent=None):
        super(Worker, self).__init__(parent=parent)

        self._execute_tasks = True
        self._app = app

        self._queue_mutex = Lock()

        self._queue = list()
        self._receivers = dict()

        self._wait_condition = Condition(self._queue_mutex)

    def stop(self, wait_for_completion=True):
        """
        Stops the work, run this before shutdown
        :param wait_for_completion:  bool
        """

        with self._queue_mutex:
            self._execute_tasks = False
            self._wait_condition.notifyAll()

        if wait_for_completion:
            self.wait()

    def clear(self):
        """
        Empties the queue
        """
        with self._queue_mutex:
            self._queue = list()

    def queue_work(self, worker_fn, params, asap=False):
        """
        Queues up some work
        :param worker_fn:
        :param params:
        :param asap: bool, If True the worker fn will be inserted the first one in the queue list
        :return: int, unique ID to identify this item
        """

        uid = uuid.uuid4().hex

        work = {'id': uid, 'fn': worker_fn, 'params': params}
        with self._queue_mutex:
            if asap:
                self._queue_mutex.insert(0, work)
            else:
                self._queue.append(work)

            self._wait_condition.notifyAll()

        return uid

    def run(self):
        while self._execute_tasks:
            item_to_process = None
            with self._queue_mutex:
                if len(self._queue) == 0:
                    # Wait for some work, this unlocks the mutex until the wait condition
                    # is signaled where it will the attemp to obtain a lock before
                    # returning
                    self._wait_condition.wait()

                    if len(self._queue) == 0:
                        continue
                item_to_process = self._queue.pop(0)
            if not self._execute_tasks:
                break

            # we have something to do
            data = None
            try:
                data = item_to_process['fn'](item_to_process['params'])
            except Exception as e:
                if self._execute_tasks:
                    self.work_failure.emit(item_to_process['id'], 'An error ocurred: {0}'.format(str(e)))
            else:
                if self._execute_tasks:
                    self.work_completed.emit(item_to_process['id'], data)
