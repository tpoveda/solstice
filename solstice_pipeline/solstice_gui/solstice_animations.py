#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_animations.py
# by Tomas Poveda
# Class with classes and function to work with GUI animations
# ______________________________________________________________________
# ==================================================================="""

from solstice_pipeline.externals.solstice_qt.QtCore import *
from solstice_pipeline.externals.solstice_qt.QtWidgets import *


def property_animation(start=[0, 0], end=[30, 0], duration=300, object=None, property='iconSize', on_finished=None):
    """
    Functions that returns a ready to use QPropertyAnimation
    :param start: int, animation start value
    :param end: int, animation end value
    :param duration: int, duration of the effect
    :param object: variant, QDialog || QMainWindow
    :param property: str, object property to animate
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    animation = QPropertyAnimation(object, property, object)
    anim_curve = QEasingCurve()
    anim_curve.setType(QEasingCurve.InOutQuint)
    animation.setEasingCurve(anim_curve)
    animation.setDuration(duration)
    animation.setStartValue(start)
    animation.setEndValue(end)
    animation.start()

    return animation


def fade_in_widget(widget, duration=200, on_finished=None):
    """
    Fade in animation effect for widgets
    :param widget: QWidget, widget to apply effect
    :param duration: int, duration of the effect
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, 'opacity')
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.InOutCubic)
    animation.start()

    if on_finished:
        animation.finished.connect(on_finished)

    widget._fade_in_ = animation

    return animation


def fade_out_widget(widget, duration=200, on_finished=None):
    """
    Fade out animation effect for widgets
    :param widget: QWidget, widget to apply effect
    :param duration: int, duration of the effect
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    animation = QPropertyAnimation(effect, 'opacity')
    animation.setDuration(duration)
    animation.setStartValue(1.0)
    animation.setEndValue(0.0)
    animation.setEasingCurve(QEasingCurve.InOutCubic)
    animation.start()

    if on_finished:
        animation.finished.connect(on_finished)

    widget._fade_out_ = animation

    return animation


def fade_animation(start=0, end=1, duration=300, object=None, on_finished=None):
    """
    Fade animation for widgets
     :param start: int, animation start value
    :param end: int, animation end value
    :param duration: int, duration of the effect
    :param object: variant, QDialog || QMainWindow
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    anim_curve = QEasingCurve()
    anim_curve.setType(QEasingCurve.OutQuint)

    if start is 'current':
        start = object.opacity()
    if end is 'current':
        end = object.opacity()

    animation = QPropertyAnimation(object, 'opacity', object)
    animation.setEasingCurve(anim_curve)
    animation.setDuration(duration)
    animation.setStartValue(start)
    animation.setEndValue(end)
    animation.start()

    if on_finished:
        animation.finished.connect(on_finished)


def fade_window(start=0, end=1, duration=300, object=None, on_finished=None):
    """
    Fade animation for windows
    :param start: int, animation start value
    :param end: int, animation end value
    :param duration: int, duration of the effect
    :param object: variant, QDialog || QMainWindow
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    anim_curve = QEasingCurve()
    anim_curve.setType(QEasingCurve.OutQuint)
    animation = QPropertyAnimation(object, 'windowOpacity', object)
    animation.setEasingCurve(anim_curve)
    animation.setDuration(duration)
    animation.setStartValue(start)
    animation.setEndValue(end)
    animation.start()

    if on_finished:
        animation.finished.connect(on_finished)

    return animation


def slide_window(start=-100, end=0, duration=300, object=None, on_finished=None):
    """
    Slide animation for windows
    :param start: int, animation start value
    :param end: int, animation end value
    :param duration: int, duration of the effect
    :param object: variant, QDialog || QMainWindow
    :param on_finished: variant, function to call when the animation is finished
    :return: QPropertyAnimation
    """

    pos = object.pos()
    animation = QPropertyAnimation(object, 'pos', object)
    animation.setDuration(duration)
    anim_curve = QEasingCurve()
    if start >= end:
        anim_curve.setType(QEasingCurve.OutExpo)
    else:
        anim_curve.setType(QEasingCurve.InOutExpo)
    animation.setEasingCurve(anim_curve)
    animation.setStartValue(QPoint(pos.x(), pos.y() + start))
    animation.setEndValue(QPoint(pos.x(), pos.y() + end))
    animation.start()

    if on_finished:
        animation.finished.connect(on_finished)

    return animation