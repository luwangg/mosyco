# -*- coding: utf-8 -*-

import argparse
import logging

# DEFAULT COLUMN NAMES
model_list = ['PAmodel']
system_list = ['PAseasonal', 'PAtrend']
# DEFAULT THRESHOLD
default_threshold = 0.2


def valid_threshold(f):
    """Determine if f is a float between 0 and 1."""
    f = float(f)
    if f < 0.0 or f > 1.0:
        msg = f"Invalid threshold value: {f} is not in range [0.0, 1.0]"
        raise argparse.ArgumentTypeError(msg)

def parse_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(prog="mosyco",
        description="Prototype for a Model-/System-Controller architecture.")

    # Log verbosity
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", help="output more verbose logs",
            action="store_true")
    group.add_argument("-q", "--quiet", help="silence output", action="store_true")

    # Data columns
    parser.add_argument("-m", "--models", help="list of the model data columns",
            default=model_list)

    parser.add_argument("-s", "--systems",
            help="list of the actual system data columns",
            default=system_list)

    # Threshold value
    parser.add_argument("-t", "--threshold",
            help="initial threshold used for gap analysis",
            default=default_threshold,
            type=valid_threshold)

    # Animation
    parser.add_argument("--gui",
            help="show animated plots if available",
            action="store_true")

    args = parser.parse_args()

    if args.quiet:
        args.loglevel = 0
    elif args.verbose:
        args.loglevel = logging.DEBUG
    else:
        args.loglevel = logging.INFO

    return args
