"""
This module contains various methods for calculating erros and evaluate
deviations between actual and simulated values.

These deviations are later used in analysis to determine if the simulation
should be adjusted.
"""


def absolute_deviation(simulated, observed, threshold):
    return abs(simulated - observed) > threshold

def relative_deviation(simulated, observed, threshold):
    return abs(simulated - observed) / simulated > threshold

def deviation_percent(simulated, observed):
    return abs(simulated - observed) / observed * 100


def exceeds_threshold(deviation, threshold):
    return deviation > threshold


def evaluation():
    """Assess deviation & provide ongoing feedback on model performance."""
    return None
