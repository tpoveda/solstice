#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Solstice Sequencer Widget used to manager short sequences
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpoveda@cgart3d.com"

import os
import sys
import time
from collections import OrderedDict

from solstice.pipeline.externals.solstice_qt.QtCore import *
from solstice.pipeline.externals.solstice_qt.QtWidgets import *

import solstice.pipeline as sp
from solstice.pipeline.gui import stack, spinner, label
from solstice.pipeline.utils import artellautils as artella
from solstice.pipeline.resources import resource

from solstice.pipeline.tools.pipelinizer.widgets import sequencerwidget

if sp.is_maya():
    import maya.cmds as cmds


class SequencerBackground(QFrame, object):
    def __init__(self, parent=None):
        super(SequencerBackground, self).__init__(parent)

        self.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        lbl_layout = QHBoxLayout()
        lbl_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.thumbnail_label = label.ThumbnailLabel()
        self.thumbnail_label.setMinimumSize(QSize(80, 55))
        self.thumbnail_label.setMaximumSize(QSize(80, 55))
        self.thumbnail_label.setStyleSheet('')
        self.thumbnail_label.setPixmap(resource.pixmap('solstice_logo', category='images'))
        self.thumbnail_label.setScaledContents(False)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        lbl_layout.addWidget(self.thumbnail_label)
        lbl_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Fixed))

        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
        main_layout.addLayout(lbl_layout)
        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))


class SequencerWaiting(QFrame, object):
    def __init__(self, parent=None):
        super(SequencerWaiting, self).__init__(parent)

        self.setStyleSheet("#background {border-radius: 3px;border-style: solid;border-width: 1px;border-color: rgb(32,32,32);}")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self.wait_spinner = spinner.WaitSpinner(spinner_type=spinner.SpinnerType.Loading)
        self.wait_spinner.bg.setFrameShape(QFrame.NoFrame)
        self.wait_spinner.bg.setFrameShadow(QFrame.Plain)

        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))
        main_layout.addWidget(self.wait_spinner)
        main_layout.addItem(QSpacerItem(0, 20, QSizePolicy.Fixed, QSizePolicy.Expanding))


class SolsticeSequencer(QWidget, object):

    sequencerInitialized = Signal()

    def __init__(self, parent=None):
        super(SolsticeSequencer, self).__init__(parent=parent)

        self._current_sequence = None

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        self._sequencer_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self._sequencer_splitter)

        self._sequences_list = QListWidget()

        self._shots_stack = stack.SlidingStackedWidget(parent=self)

        bg_widget = SequencerBackground()
        wait_widget = SequencerWaiting()
        self._shots_list = QListWidget()
        self._shots_stack.addWidget(bg_widget)
        self._shots_stack.addWidget(wait_widget)
        self._shots_stack.addWidget(self._shots_list)

        self._sequencer_splitter.addWidget(self._sequences_list)
        self._sequencer_splitter.addWidget(self._shots_stack)

        # self._sequences_list.currentItemChanged.connect(self.update_shots)

        # =============================================================================================

        shots_widget = QWidget()
        shots_layout = QVBoxLayout()
        shots_layout.setContentsMargins(2, 2, 2, 2)
        shots_layout.setSpacing(2)
        shots_widget.setLayout(shots_layout)
        self._sequencer_splitter.addWidget(shots_widget)

    def init_sequencer(self):
        self._shots_list.clear()
        self._sequences_list.clear()

        start_time = time.time()
        sequences = list()

        try:
            thread, event = sys.solstice.info_dialog.do(
                'Getting Sequences Info ... Please wait!',
                'SolsticeArtellaSequencesThread',
                self.get_solstice_sequences, [sequences], show=False
            )

            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.05)
        except Exception as e:
            sys.solstice.logger.debug(str(e))

        elapsed_time = time.time() - start_time
        sys.solstice.logger.debug('Sequences synchronized in {} seconds'.format(elapsed_time))

        self.sequencerInitialized.emit()

        if sequences:
            sequences = sequences[0]
        else:
            return

        for seq_data, seq_files in sequences.items():
            sequence_widget = sequencerwidget.SequenceWidget(sequence_data=seq_data, sequence_files=seq_files)
            sequence_widget.syncShots.connect(self.update_shots)
            sequence_item = QListWidgetItem()
            sequence_item.setSizeHint(sequence_widget.sizeHint())
            sequence_item.setFlags(Qt.NoItemFlags)
            self._sequences_list.addItem(sequence_item)
            self._sequences_list.setItemWidget(sequence_item, sequence_widget)

    def sync_sequences(self, full_sync=False, ask=False):
        """
        Synchronizes all the sequences of Solstice Short Film
        :param full_sync: bool, If True, all the assets will be sync with the content on Artella Server,
               if False, only will synchronize the assets that are missing (no warranty that you have latest versions
               on other assets)
       :param ask: bool, True if you want to show a message box to the user to decide if the want or not download
               missing files in his local machine
        :return:
        """

        sys.solstice.logger.debug('Syncing sequences ...')

        start_time = time.time()
        try:
            cmds.waitCursor(state=True)
            sequences = list()
            thread, event = sys.solstice.info_dialog.do(
                'Getting Sequences Info ... Please wait!',
                'SolsticeArtellaSequencesThread',
                self.get_solstice_sequences_data, [sequences]
            )

            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.05)

            if sequences:
                sequences = sequences[0]
                for seq_data in sequences:
                    seq_obj = sequencerwidget.SequenceWidget(
                        sequence_data=seq_data
                    )
                    seq_obj.sync()
        except Exception as e:
            sys.solstice.logger.debug(str(e))
            cmds.waitCursor(state=False)

        elapsed_time = time.time() - start_time
        sys.solstice.logger.debug('Sequences synchronized in {} seconds'.format(elapsed_time))
        cmds.waitCursor(state=False)

    def update_shots(self, selected_widget=None):
        if selected_widget is None:
            return

        valid_sync = True
        sys.solstice.logger.debug('Syncing sequences ...')

        self._shots_list.clear()

        start_time = time.time()
        try:
            self._shots_stack.setCurrentIndex(1)
            cmds.waitCursor(state=True)
            sequence_shots = list()
            thread, event = sys.solstice.info_dialog.do(
                'Getting Sequence Shots ... Please wait!',
                'SolsticeArtellaSequencesShotsThread',
                self.get_sequence_shots, [sequence_shots, selected_widget, 'working'], show=False
            )

            while not event.is_set():
                QCoreApplication.processEvents()
                event.wait(0.05)

            if sequence_shots:
                sequence_shots = sequence_shots[0]
                for shot_data, shot_files in sequence_shots.items():
                    shot_widget = sequencerwidget.ShotWidget(shot_data=shot_data, shot_files=shot_files)
                    shot_item = QListWidgetItem()
                    shot_item.setSizeHint(shot_widget.sizeHint())
                    self._shots_list.addItem(shot_item)
                    self._shots_list.setItemWidget(shot_item, shot_widget)
        except Exception as e:
            sys.solstice.logger.debug(str(e))
            cmds.waitCursor(state=False)
            self._shots_stack.setCurrentIndex(0)
            valid_sync = False

        elapsed_time = time.time() - start_time
        sys.solstice.logger.debug('Shots updated in {} seconds'.format(elapsed_time))
        cmds.waitCursor(state=False)

        if valid_sync:
            self._shots_stack.slide_in_next()

    def get_solstice_sequences_data(self, thread_result=None, thread_event=None):
        """
        Returns a list of paths to sequences
        :return: list<str>
        """

        production_path = sp.get_solstice_production_path()
        if not production_path:
            return

        production_info = artella.get_status(production_path)
        if not production_info:
            return

        sequences = list()
        for ref_name, ref_data in production_info.references.items():
            if 'SEQ' in ref_data.name:
                sequences.append(ref_data)

        # Reorder list by sequence name
        sequences.sort(key=lambda x: x.name, reverse=False)

        if thread_event:
            thread_event.set()
            thread_result.append(sequences)

        return sequences

    def get_solstice_sequences(self, thread_result=None, thread_event=None):
        """
        Returns a list of sequences as dict with its files
        :param thread_result:
        :param thread_event:
        :return:
        """

        sequences = self.get_solstice_sequences_data()
        if not sequences:
            return

        sequences_dict = OrderedDict()
        for seq in sequences:
            sequences_dict[seq] = OrderedDict()
            seq_files = self.get_sequences_files(seq, status='working')
            if seq_files:
                sequences_dict[seq] = seq_files

        if thread_event:
            thread_event.set()
            thread_result.append(sequences_dict)

        return sequences_dict

    def get_sequence_shots(self, thread_result=None, sequence=None, status='published',  thread_event=None):
        if status == 'working':
            sequence_info = artella.get_status(os.path.join(sp.get_solstice_production_path(), sequence.name))
            if not sequence_info:
                return None

            shots = list()
            for ref_name, ref_data in sequence_info.references.items():
                if ref_name.startswith('S_'):
                    shots.append(ref_data)

            # Reorder shots by shot name
            shots.sort(key=lambda x:x.name, reverse=False)

            print('SHOT: {}'.format(shots))

            shots_dict = OrderedDict()
            for shot in shots:
                shots_dict[shot] = OrderedDict()
                shot_files = self.get_shots_files(sequence=sequence, shot=shot, status=status)
                if shot_files:
                    shots_dict[shot] = shot_files

            if thread_event:
                thread_event.set()
                thread_result.append(shots_dict)

            return shots_dict
        elif status == 'published':
            raise NotImplementedError('Not implemented yet!')
        return None

    @staticmethod
    def get_sequences_files(sequence, status='published'):

        seq_files = dict()
        master_layout_folder = os.path.join(sp.get_solstice_production_path(), sequence.name, '_master_layout')
        seq_files['master_layout'] = dict()
        seq_files['master_layout']['path'] = master_layout_folder

        if status == 'working':
            # Master Layout File
            master_layout_working_folder = os.path.join(master_layout_folder, '__working__', 'seq_layout')
            layout_info = artella.get_status(master_layout_working_folder)
            if not layout_info:
                return None
            layout_files = list()
            if not hasattr(layout_info, 'references'):
                return None
            if layout_info.references:
                for ref_name, ref_data in layout_info.references.items():
                    layout_files.append(os.path.join(master_layout_working_folder, ref_name.split('/')[-1]))
            if len(layout_files) > 0:
                seq_files['master_layout']['working'] = dict()
                seq_files['master_layout']['working']['path'] = master_layout_working_folder
                seq_files['master_layout']['working']['file'] = layout_files[0]
            return seq_files
        elif status == 'published':
            raise NotImplementedError('Not implemented yet!')
            # master_layout_folder = os.path.join(sp.get_solstice_production_path(), sequence.name, '_master_layout', 'seq_layout')
            # layout_info = artella.get_status(master_layout_folder)
            pass
        return None

    @staticmethod
    def get_shots_files(sequence, shot, status='published'):
        if status == 'working':
            shot_files = dict()
            for file_type in ['previs', 'anim', 'effects', 'light']:
                shot_files[file_type] = None
                previs_folder = os.path.join(sp.get_solstice_production_path(), sequence.name, shot.name, '__working__', file_type)
                previs_info = artella.get_status(previs_folder)
                if not previs_info:
                    continue
                if hasattr(previs_info, status) and previs_info.status == 'ERROR':
                    continue
                files_list = list()
                if not hasattr(previs_info, 'references'):
                    continue
                if previs_info.references:
                    for ref_name, ref_data in previs_info.references.items():
                        files_list.append(os.path.join(previs_folder, ref_name.split('/')[-1]))
                    if len(files_list) > 0:
                        for f in files_list:
                            if f.endswith('.ma'):
                                shot_files[file_type] = f
                                break
            return shot_files
        elif status == 'published':
            pass
        return None
