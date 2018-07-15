#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_label.py
# by Tomas Poveda
# Module that contains classes to create different kind of labels
# ______________________________________________________________________
# ==================================================================="""

from solstice_qt.QtCore import *
from solstice_qt.QtWidgets import *
from solstice_qt.QtGui import *

from solstice_utils import solstice_qt_utils as utils


class ElidedLabel(QLabel, object):
    """
    This label elides text and adds ellipses if the text does not fit
    properly withing the widget frame
    """

    def __init__(self, parent=None):
        super(ElidedLabel, self).__init__(parent=parent)

        self._elide_mode = Qt.ElideRight
        self._actual_text = ""
        self._line_width = 0
        self._ideal_width = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def sizeHint(self):

        base_size_hint = super(ElidedLabel, self).sizeHint()
        return QSize(self._get_width_hint(), base_size_hint.height())

    def _get_width_hint(self):

        if not self._ideal_width:

            doc = QTextDocument()
            try:
                # add the extra space to buffer the width a bit
                doc.setHtml(self._actual_text + "&nbsp;")
                doc.setDefaultFont(self.font())
                width = doc.idealWidth()
            except Exception:
                width = self.width()
            finally:
                utils.safe_delete_later(doc)

            self._ideal_width = width

        return self._ideal_width

    def _get_elide_mode(self):
        """
        Returns current elide mode
        """

        return self._elide_mode

    def _set_elide_mode(self, value):
        """
        Set the current elide mode.
        """

        if (value != Qt.ElideLeft
                and value != Qt.ElideRight):
            raise ValueError("elide_mode must be set to either QtCore.Qt.ElideLeft or QtCore.Qt.ElideRight")
        self._elide_mode = value
        self._update_elided_text()

    elide_mode = property(_get_elide_mode, _set_elide_mode)

    def text(self):
        """
        Overridden base method to return the original unmodified text
        """
        return self._actual_text

    def setText(self, text):
        """
        Overridden base method to set the text on the label
        """
        # clear out the ideal width so that the widget can recalculate based on
        # the new text
        self._ideal_width = None
        self._actual_text = text
        self._update_elided_text()

        # if we're elided, make the tooltip show the full text
        if super(ElidedLabel, self).text() != self._actual_text:
            # wrap the actual text in a paragraph so that it wraps nicely
            self.setToolTip("<p>%s</p>" % (self._actual_text,))
        else:
            self.setToolTip("")

    def resizeEvent(self, event):
        """
        Overridden base method called when the widget is resized.
        """

        self._update_elided_text()

    def _update_elided_text(self):
        """
        Update the elided text on the label
        """

        text = self._elide_text(self._actual_text, self._elide_mode)
        QLabel.setText(self, text)

    def _elide_text(self, text, elide_mode):
        """
        Elide the specified text using the specified mode
        :param text:        The text to elide
        :param elide_mode:  The elide mode to use
        :returns:           The elided text.
        """

        # target width is the label width:
        target_width = self.width()

        # Use a QTextDocument to measure html/richtext width
        doc = QTextDocument()
        try:
            doc.setHtml(text)
            doc.setDefaultFont(self.font())

            # if line width is already less than the target width then great!
            line_width = doc.idealWidth()
            if line_width <= target_width:
                self._line_width = line_width
                return text

            # depending on the elide mode, insert ellipses in the correct place
            cursor = QTextCursor(doc)
            ellipses = ""
            if elide_mode != Qt.ElideNone:
                # add the ellipses in the correct place:
                ellipses = "..."
                if elide_mode == Qt.ElideLeft:
                    cursor.setPosition(0)
                elif elide_mode == Qt.ElideRight:
                    char_count = doc.characterCount()
                    cursor.setPosition(char_count - 1)
                cursor.insertText(ellipses)
            ellipses_len = len(ellipses)

            # remove characters until the text fits within the target width:
            while line_width > target_width:

                start_line_width = line_width

                # if string is less than the ellipses length then just return
                # an empty string
                char_count = doc.characterCount()
                if char_count <= ellipses_len:
                    self._line_width = 0
                    return ""

                # calculate the number of characters to remove - should always remove at least 1
                # to be sure the text gets shorter!
                line_width = doc.idealWidth()
                p = target_width / line_width
                # play it safe and remove a couple less than the calculated amount
                chars_to_delete = max(1, char_count - int(float(char_count) * p) - 2)

                # remove the characters:
                if elide_mode == Qt.ElideLeft:
                    start = ellipses_len
                    end = chars_to_delete + ellipses_len
                else:
                    # default is to elide right
                    start = max(0, char_count - chars_to_delete - ellipses_len - 1)
                    end = max(0, char_count - ellipses_len - 1)

                cursor.setPosition(start)
                cursor.setPosition(end, QTextCursor.KeepAnchor)
                cursor.removeSelectedText()

                # update line width:
                line_width = doc.idealWidth()

                if line_width == start_line_width:
                    break

            self._line_width = line_width
            return doc.toHtml()
        finally:
            utils.safe_delete_later(doc)

    @property
    def line_width(self):
        """
        :returns: int, width of the line of text in pixels
        """
        return self._line_width

