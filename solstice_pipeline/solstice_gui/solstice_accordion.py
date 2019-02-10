#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# by Tomas Poveda
#  Collapsible accordion widget similar to Maya Attribute Editor
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *
from solstice_pipeline.externals.solstice_qt.QtGui import *


class AccordionStyle(object):
    BOXED = 1
    ROUNDED = 2
    SQUARE = 3
    MAYA = 4


class AccordionDragDrop(object):
    NO_DRAG_DROP = 0
    INTERNAL_MOVE = 1


class AccordionItem(QGroupBox, object):

    trigger = Signal(bool)

    def __init__(self, accordion, title, widget):
        super(AccordionItem, self).__init__(parent=accordion)

        self._accordion_widget = accordion
        self._widget = widget
        self._rollout_style = AccordionStyle.ROUNDED
        self._drag_drop_mode = AccordionDragDrop.NO_DRAG_DROP
        self._collapsed = False
        self._collapsible = True
        self._clicked = False
        self._custom_data = dict()

        layout = QVBoxLayout()
        layout.setContentsMargins(6, 12, 6, 6)
        layout.setSpacing(0)
        layout.addWidget(widget)

        self.setAcceptDrops(True)
        self.setLayout(layout)
        self.setTitle(title)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_show_menu)

    def get_accordion_widget(self):
        return self._accordion_widget

    def get_widget(self):
        return self._widget

    def get_rollout_style(self):
        return self._rollout_style

    def set_rollout_style(self, style):
        self._rollout_style = style

    def get_drag_drop_mode(self):
        return self._drag_drop_mode

    def set_drag_drop_mode(self, mode):
        self._drag_drop_mode = mode

    def get_collapsible(self):
        return self._collapsible

    def set_collapsible(self, collapsible):
        self._collapsible = collapsible

    accordion_widget = property(get_accordion_widget)
    widget = property(get_widget)
    rollout_style = property(get_rollout_style, set_rollout_style)
    drag_drop_mode = property(get_drag_drop_mode, set_drag_drop_mode)
    collapsible = property(get_collapsible, set_collapsible)

    def enterEvent(self, event):
        self.accordion_widget.leaveEvent(event)
        event.accept()

    def leaveEvent(self, event):
        self.accordion_widget.enterEvent(event)
        event.accept()

    def dragEnterEvent(self, event):
        if not self._drag_drop_mode:
            return
        source = event.source()
        if source != self and source.parent() == self.parent() and isinstance(source, AccordionItem):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if not self._drag_drop_mode:
            return
        source = event.source()
        if source != self and source.parent() == self.parent() and isinstance(source, AccordionItem):
            event.acceptProposedAction()

    def dropEvent(self, event):
        widget = event.source()
        layout = self.parent().layout()
        layout.insertWidget(layout.indexOf(self), widget)
        self._accordion_widget.emit_items_reordered()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.get_drag_drop_rect().contains(event.pos()):
            pixmap = QPixmap.grabWidget(self, self.rect())
            mime_data = QMimeData()
            mime_data.setText('ItemTitle::{}'.format(self.title()))
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            if not drag.exec_():
                self._accordion_widget.emit_item_drag_failed(self)
            event.accept()
        # Check if the expand/collapse should happen
        elif event.button() == Qt.LeftButton and self.expand_collapse_rect().contains(event.pos()):
            self._clicked = True
            event.accept()
        else:
            event.ignore()

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        if self._clicked and self.expand_collapse_rect().contains(event.pos()):
            self.toggle_collapsed()
            event.accept()
        else:
            event.ignore()
        self.clicked = False

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(painter.Antialiasing)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        x = self.rect().x()
        y = self.rect().y()
        w = self.rect().width() - 1
        h = self.rect().height() - 1
        r = 8

        if self.rollout_style == AccordionStyle.ROUNDED:
            painter.drawText(x + 33, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            self._draw_triangle(painter, x, y)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRoundedRect(x + 1, y + 1, w - 1, h - 1, r, r)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRoundedRect(x, y, w - 1, h - 1, r, r)
        elif self.rollout_style == AccordionStyle.SQUARE:
            painter.drawText(x + 33, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            self._draw_triangle(painter, x, y)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRect(x + 1, y + 1, w - 1, h - 1)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRect(x, y, w - 1, h - 1)
        elif self.rollout_style == AccordionStyle.MAYA:
            painter.drawText(x + 33, y + 3, w, 16, Qt.AlignLeft | Qt.AlignTop, self.title())
            painter.setRenderHint(QPainter.Antialiasing, False)
            self._draw_triangle(painter, x, y)
            header_height = 20
            header_rect = QRect(x + 1, y + 1, w - 1, header_height)
            header_rect_shadow = QRect(x - 1, y - 1, w + 1, header_height + 2)
            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.4)
            painter.setPen(pen)
            painter.drawRect(header_rect)
            painter.fillRect(header_rect, QColor(255, 255, 255, 18))
            pen.setColor(self.palette().color(QPalette.Dark))
            painter.setPen(pen)
            painter.drawRect(header_rect_shadow)
            if not self.is_collapsed():
                pen = QPen(self.palette().color(QPalette.Dark))
                pen.setWidthF(0.8)
                painter.setPen(pen)
                offset = header_height + 3
                body_rect = QRect(x, y + offset, w, h - offset)
                body_rect_shadow = QRect(x + 1, y + offset, w + 1, h - offset + 1)
                painter.drawRect(body_rect)
                pen.setColor(self.palette().color(QPalette.Light))
                pen.setWidth(0.4)
                painter.setPen(pen)
                painter.drawRect(body_rect_shadow)
        elif self.rollout_style == AccordionStyle.BOXED:
            if self.is_collapsed():
                a_rect = QRect(x + 1, y + 9, w - 1, 4)
                b_rect = QRect(x, y + 8, w - 1, 4)
                text = '+'
            else:
                a_rect = QRect(x + 1, y + 9, w - 1, h - 9)
                b_rect = QRect(x, y + 8, w - 1, h - 9)
                text = '-'

            pen = QPen(self.palette().color(QPalette.Light))
            pen.setWidthF(0.6)
            painter.setPen(pen)
            painter.drawRect(a_rect)
            pen.setColor(self.palette().color(QPalette.Shadow))
            painter.setPen(pen)
            painter.drawRect(b_rect)
            painter.setRenderHint(painter.Antialiasing, False)
            painter.setBrush(self.palette().color(QPalette.Window).darker(120))
            painter.drawRect(x + 10, y + 1, w - 20, 16)
            painter.drawText(x + 16, y + 1, w - 32, 16, Qt.AlignLeft | Qt.AlignVCenter, text)
            painter.drawText(x + 10, y + 1, w - 20, 16, Qt.AlignCenter, self.title())

        if self.drag_drop_mode:
            rect = self.get_drag_drop_rect()
            l = rect.left()
            r = rect.right()
            cy = rect.center().y()
            for y in (cy - 3, cy, cy + 3):
                painter.drawLine(l, y, r, y)

        painter.end()


    def get_custom_data(self, key, default=None):
        """
        Returns a custom pionter to information stored with this item
        :param key: str
        :param default: variant, default value to return if the key was not found
        :return: variant, data
        """
        return self._custom_data.get(str(key), default)

    def set_custom_data(self, key, value):
        """
        Sets a custom pointer to information stored on this item
        :param key: str
        :param value: variant
        """

        self._custom_data[str(key)] = value

    def get_drag_drop_rect(self):
        return QRect(25, 7, 10, 6)

    def expand_collapse_rect(self):
        return QRect(0, 0, self.width(), 20)

    def is_collapsed(self):
        return self._collapsed

    def set_collapsed(self, state=True):
        if self.collapsible:
            accord = self.accordion_widget
            accord.setUpdatesEnabled(True)
            self._collapsed = state
            if state:
                self.setMinimumHeight(22)
                self.setMaximumHeight(22)
                self.widget.setVisible(False)
            else:
                self.setMinimumHeight(0)
                self.setMaximumHeight(1000000)
                self.widget.setVisible(True)

            self._accordion_widget.emit_item_collapsed(self)
            accord.setUpdatesEnabled(True)

    def toggle_collapsed(self):
        collapsed_state = not self.is_collapsed()
        self.set_collapsed(collapsed_state)
        return collapsed_state

    def _on_show_menu(self):
        if QRect(0, 0, self.width(), 20).contains(self.mapFromGlobal(QCursor.pos())):
            self._accordion_widget.emit_item_menu_requested(self)

    def _draw_triangle(self, painter, x, y):
        brush = QBrush(QColor(255, 255, 255, 160), Qt.SolidPattern)
        if not self.is_collapsed():
            tl, tr, tp = QPoint(x + 9, y + 8), QPoint(x + 19, y + 8), QPoint(x + 14, y + 13.0)
            points = [tl, tr, tp]
            triangle = QPolygon(points)
        else:
            tl, tr, tp = QPoint(x + 11, y + 6), QPoint(x + 16, y + 11), QPoint(x + 11, y + 16.0)
            points = [tl, tr, tp]
            triangle = QPolygon(points)

        current_brush = painter.brush()
        painter.setBrush(brush)
        painter.drawPolygon(triangle)
        painter.setBrush(current_brush)


class AccordionWidget(QScrollArea, object):

    itemCollapsed = Signal(AccordionItem)
    itemMenuRequested = Signal(AccordionItem)
    itemDragFailed = Signal(AccordionItem)
    itemsReordered = Signal()

    def __init__(self, parent=None):
        super(AccordionWidget, self).__init__(parent=parent)

        self._rollout_style = AccordionStyle.ROUNDED
        self._drag_drop_mode = AccordionDragDrop.NO_DRAG_DROP
        self._scrolling = False
        self._scroll_init_y = 0
        self._scroll_init_val = 0
        self._item_class = AccordionItem

        self.setFrameShape(QScrollArea.NoFrame)
        self.setAutoFillBackground(False)
        self.setWidgetResizable(True)
        self.setMouseTracking(True)
        self.verticalScrollBar().setMaximumWidth(10)

        widget = QWidget(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 6)
        layout.setSpacing(2)
        layout.addStretch(1)
        widget.setLayout(layout)
        self.setWidget(widget)

    def get_drag_drop_mode(self):
        return self._drag_drop_mode

    def set_drag_drop_mode(self, mode):
        self._drag_drop_mode = mode
        for item in self.findChildren(AccordionItem):
            item.drag_drop_mode = self._drag_drop_mode

    def get_rollout_style(self):
        return self._rollout_style

    def set_rollout_style(self, style):
        self._rollout_style = style
        for item in self.findChildren(AccordionItem):
            item.rollout_style = self._rollout_style

    def get_item_class(self):
        return self._item_class

    def set_item_class(self, item_class):
        self._item_class = item_class

    drag_drop_mode = property(get_drag_drop_mode, set_drag_drop_mode)
    rollout_style = property(get_rollout_style, set_rollout_style)
    item_class = property(get_item_class, set_item_class)

    def eventFilter(self, object, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
            return True
        elif event.type() == QEvent.MouseMove:
            self.mouseMoveEvent(event)
            return True
        elif event.type() == QEvent.MouseButtonRelease:
            self.mouseReleaseEvent(event)
            return True
        return False

    def enterEvent(self, event):
        if self.can_scroll():
            QApplication.setOverrideCursor(Qt.OpenHandCursor)

    def leaveEvent(self, event):
        if self.can_scroll():
            QApplication.restoreOverrideCursor()

    def mouseMoveEvent(self, event):
        if self._scrolling:
            sbar = self.verticalScrollBar()
            smax = sbar.maximum()
            # Calculate the distance moved for the mouse point
            dy = event.globalY() - self._scroll_init_y
            # Calculate the percentage that is on the scroll bar
            dval = smax * (dy / float(sbar.height()))
            # Calculate the new value
            sbar.setValue(self._scroll_init_val - dval)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.can_scroll():
            self._scrolling = True
            self._scroll_init_y = event.globalY()
            self._scroll_init_val = self.verticalScrollBar().value()
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
        event.accept()

    def mouseReleaseEvent(self, event):
        if self._scrolling:
            QApplication.restoreOverrideCursor()
        self._scrolling = False
        self._scroll_init_y = 0
        self._scroll_init_val = 0
        event.accept()

    def can_scroll(self):
        return self.verticalScrollBar().maximum() > 0

    def count(self):
        return self.widget().layout().count() - -1

    def set_spacing(self, space_int):
        self.widget().layout().setSpacing(space_int)

    def add_item(self, title, widget, collapsed=False):
        self.setUpdatesEnabled(False)
        try:
            item = self._item_class(self, title, widget)
            item.rollout_style = self.rollout_style
            item.drag_drop_mode = self.drag_drop_mode
            layout = self.widget().layout()
            layout.insertWidget(layout.count() - 1, item)
            layout.setStretchFactor(item, 0)
            if collapsed:
                item.set_collapsed(state=collapsed)
            self.setUpdatesEnabled(True)
            return item
        except Exception:
            self.setUpdatesEnabled(True)
            return None

    def clear(self):
        self.setUpdatesEnabled(False)
        try:
            layout = self.widget().layout()
            while layout.count() > 1:
                item = layout.itemAt(0)

                # First we remove the item from the layout
                w = item.widget
                layout.removeItem(item)

                # Second, close the widget and delete it
                w.close()
                w.deleteLater()
            self.setUpdatesEnabled(True)
        except Exception:
            self.setUpdatesEnabled(True)

    def index_of(self, widget):
        """
        Searches for widget (without including child layouts) and returns the index of widget
        or -1 if the widget is not found
        :param widget: QWidget
        :return: int
        """

        layout = self.widget().layout()
        for index in range(layout.count()):
            if layout.itemAt(index).widget().widget() == widget:
                return index

        return -1

    def is_box_mode(self):
        return self._rollout_style == AccordionStyle.MAYA

    def set_box_mode(self, state):
        if state:
            self._rollout_style = AccordionStyle.BOXED
        else:
            self._rollout_style = AccordionStyle.ROUNDED

    def item_at(self, index):
        layout = self.widget().layout()
        if 0 <= index < layout.count() - 1:
            return layout.itemAt(index).widget()
        return None

    def move_item_down(self, index):
        layout = self.widget().layout()
        if (layout.count() - 1) > (index + 1):
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index + 1, widget)

    def move_item_up(self, index):
        if index > 0:
            layout = self.widget().layout()
            widget = layout.takeAt(index).widget()
            layout.insertWidget(index - 1, widget)

    def take_at(self, index):
        self.setUpdatesEnabled(False)
        try:
            layout = self.widget().layout()
            widget = None
            if 0 < index < layout.count() - 1:
                item = layout.itemAt(index)
                widget = item.widget
                layout.removeItem(item)
                widget.close()
            self.setUpdatesEnabled(True)
            return widget
        except Exception:
            self.setUpdatesEnabled(True)
        return None

    def widget_at(self, index):
        item = self.item_at(index)
        if item:
            return item.widget
        return None

    def emit_item_collapsed(self, item):
        if not self.signalsBlocked():
            self.itemCollapsed.emit(item)

    def emit_item_menu_requested(self, item):
        if not self.signalsBlocked():
            self.itemMenuRequested.emit(item)

    def emit_item_drag_failed(self, item):
        if not self.signalsBlocked():
            self.itemDragFailed.emit(item)

    def emit_items_reordered(self):
        if not self.signalsBlocked():
            self.itemsReordered.emit()
