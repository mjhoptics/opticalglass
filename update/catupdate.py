#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2019 Michael J. Hayford
""" Update support for commercial glass catalogs

.. codeauthor: Michael J. Hayford
"""


def find_differences(catalog_prev, catalog):
    """ find differences in the glass list between 2 catalog versions """
    gnames_prev = catalog_prev.get_glass_names()
    gnames = catalog.get_glass_names()

    num_glasses_prev = len(gnames_prev)
    num_glasses = len(gnames)

    gnames_prev_set = set(gnames_prev)
    gnames_set = set(gnames)

    gnames_intersection = gnames_prev_set.intersection(gnames_set)
    gnames_unchanged = len(gnames_intersection)

    gnames_removed = gnames_prev_set.difference(gnames_intersection)
    gnames_added = gnames_set.difference(gnames_intersection)

    print('previous number of glasses:', num_glasses_prev)
    print('current number of glasses:', num_glasses)
    print('number of unchanged glasses:', gnames_unchanged)

    num_gnames_removed = len(gnames_removed)
    print('number of glasses removed:', num_gnames_removed)
    if num_gnames_removed > 0:
        print(gnames_removed)

    num_gnames_added = len(gnames_added)
    print('number of glasses added:', num_gnames_added)
    if num_gnames_added > 0:
        print(gnames_added)
