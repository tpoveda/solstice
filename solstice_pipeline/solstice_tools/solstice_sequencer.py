#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_sequencer.py
# by Tomas Poveda
# Solstice Sequencer Widget used to manager short sequences
# ______________________________________________________________________
# ==================================================================="""

import os
from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *

import solstice_pipeline as sp
from solstice_gui import solstice_sequencerwidgets
from solstice_utils import solstice_artella_utils as artella

reload(solstice_sequencerwidgets)
reload(artella)


class SolsticeSequencer(QWidget, object):
    def __init__(self, parent=None):
        super(SolsticeSequencer, self).__init__(parent=parent)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        self.setLayout(main_layout)



        sequencer_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(sequencer_splitter)

        sequences = self.get_solstice_sequences()
        self._sequencer = solstice_sequencerwidgets.SequencerTreeView(sequences=sequences)
        sequencer_splitter.addWidget(self._sequencer)

        # =============================================================================================

        shots_widget = QWidget()
        shots_layout = QVBoxLayout()
        shots_layout.setContentsMargins(2, 2, 2, 2)
        shots_layout.setSpacing(2)
        shots_widget.setLayout(shots_layout)
        sequencer_splitter.addWidget(shots_widget)

    def get_solstice_sequences(self):
        production_info = artella.get_status(sp.get_solstice_production_path())
        if not production_info:
            return

        sequences = list()
        for ref_name, ref_data in production_info.references.items():
            if 'SEQ' in ref_data.name:
                sequences.append(ref_data)
        # Reorder list by sequence name
        sequences.sort(key=lambda x: x.name, reverse=False)

        sequences_dict = OrderedDict()
        for seq in sequences:
            sequences_dict[seq] = dict()
            seq_files = self.get_sequences_files(seq, status='working')
            if seq_files:
                sequences_dict[seq] = seq_files

        return sequences_dict

    def get_sequences_files(self, sequence, status='published'):

        if status == 'working':

            # Master Layout File
            master_layout_folder = os.path.join(sp.get_solstice_production_path(), sequence.name, '_master_layout', '__working__', 'seq_layout')
            layout_info = artella.get_status(master_layout_folder)
            if not layout_info:
                return None
            seq_files = dict()
            layout_files = list()
            if not hasattr(layout_info, 'references'):
                return None
            if layout_info.references:
                for ref_name, ref_data in layout_info.references.items():
                    layout_files.append(ref_data)
            if len(layout_files) > 0:
                seq_files['layout'] = layout_files[0]

            # Sequence Shoots
            # seq_shots = self.get_sequence_shoots(sequence=sequence, status=status)

            return seq_files

        elif status == 'published':
            # master_layout_folder = os.path.join(sp.get_solstice_production_path(), sequence.name, '_master_layout', 'seq_layout')
            # layout_info = artella.get_status(master_layout_folder)
            pass

        return None

    def get_sequence_shoots(self, sequence, status='published'):
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

            print('SEQUENCE SHOOTS: ')
            print(shots)

            return shots


        elif status == 'published':
            pass

        return None




