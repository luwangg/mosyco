# -*- coding: utf-8 -*-
"""This module contains various helper functions."""

import os
import sys
import contextlib
import logging
import pandas as pd


def load_dataframe():
    """Load the dataset into memory."""
    df = pd.read_csv(os.path.join('data/sample_data.csv'),
                                    index_col=1, parse_dates=True,
                                    infer_datetime_format=True)
    # sanitize dataframe
    df = df.drop(['Unnamed: 0'], axis=1)
    return df

def setup_logging(args):
    """Setup logging for the application"""

    log = logging.getLogger(__package__)
    log.setLevel(args.loglevel)

    # disable root logger handlers
    root_logger = logging.getLogger()
    root_logger.handlers = []

    # set log output destination
    if args.logfile:
        handler = logging.FileHandler('mosyco.log', mode='w')
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('{name}: {message}', style='{'))
    root_logger.addHandler(handler)

    # set prophet loglevel
    logging.getLogger('fbprophet').setLevel(logging.WARNING)

    return log

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
