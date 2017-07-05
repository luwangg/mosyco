# -*- coding: utf-8 -*-
"""This module contains various helper functions."""

import os
import sys
import contextlib

import pandas as pd


def load_dataframe():
    """Load the dataset into memory."""
    # TODO: proper naming conventions for columns
    df = pd.read_csv(os.path.join('data/productA-data.csv'),
                                    index_col=1, parse_dates=True,
                                    infer_datetime_format=True)
    # sanitize dataframe
    df = df.drop(['Unnamed: 0'], axis=1)
    return df


@contextlib.contextmanager
def silence():
    """Silence all output in block used with this context manager.
    This is done by redirecting stdout to /dev/null while block is executing.
    """
    devnull = open(os.devnull, 'w')
    oldstdout_fno = os.dup(sys.stdout.fileno())
    os.dup2(devnull.fileno(), 1)

    yield

    os.dup2(oldstdout_fno, 1)
    devnull.close()
