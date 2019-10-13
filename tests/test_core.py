#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains tests for solstice-core
"""

from solstice import __version__


def test_version():
    assert __version__.__version__
