# -*- coding: utf-8 -*-

import argparse
import logging

# DEFAULT COLUMN NAMES
model_name = 'PAmodel'
actual_name = 'PAseasonal'
# DEFAULT THRESHOLD
default_threshold = 0.3


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
    parser.add_argument("-m", "--model", help="name of the model data column",
            default=model_name)

    parser.add_argument("-s", "--system",
            help="name of the actual system data column",
            default=actual_name)

    # Threshold value
    parser.add_argument("-t", "--threshold",
            help="threshold used for gap analysis",
            default=default_threshold,
            type=valid_threshold)

    # Animation
    parser.add_argument("--animate",
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
