#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2020 Michael J. Hayford
"""Utilities including Singleton metaclass

.. Created on Wed Sep 16 21:42:49 2020

.. codeauthor: Michael J. Hayford
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = (super(Singleton, cls).
                                   __call__(*args, **kwargs))
        return cls._instances[cls]
