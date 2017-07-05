# -*- coding: utf-8 -*-
"""
This module contains various methods for calculating erros and evaluate
deviations between actual and simulated values.

These deviations are later used in analysis to determine if the simulation
should be adjusted.
"""


# TODO: Docstrings


def absolute_deviation(simulated, observed, threshold):
    return abs(simulated - observed) > threshold

def relative_deviation(simulated, observed, threshold):
    # TODO: try except ZeroDivisionError handle properly
    try:
        1 / observed
    except ZeroDivisionError:
        observed = 0.00001

    dev = abs(simulated - observed) / observed
    if dev > threshold:
        return (True, dev)
    else:
        return (False, dev)
