# -*- coding: utf-8 -*-
import argparse
import logging
import sys

log = logging.getLogger(__name__)

# DEFAULT COLUMN NAMES
model_list = ['PAmodel']
system_list = ['PAseasonal']
# DEFAULT THRESHOLD
default_threshold = 0.0025

desc = ("Prototype for a Model-/System-Controller architecture. "
        "\n\n"
        "Sample data for this prototype is contained in 'data/productA-data.csv',\n"
        "which is automatically loaded by the reader. The command-line options\n"
        "'--models' and '--systems' allow the user to select which columns from\n"
        "the sample data they want to use as model- and system-values respectively."
        "\n\n"
        "Avilable data columns are:\n"
        "'PAmodel' -> The standard model data from the Bossel Vensim Simulation\n"
        "'PAseasonal' -> This data includes a yearly seasonal component\n"
        "'PAtrend' -> This data includes an underlying trend\n"
        "'PAshift' -> This data includes a sudden shift\n"
        "'PAcombi' -> This data includes all three of the three above components"
        "\n\n"
        "To read more about the sample data, visit:\n"
        "https://vab9.github.io/observer/data-prep.html\n\n"
        "The actual system data is pushed from the reader to the inspector\n"
        "through a thread-safe queue, in order to mimic the behaviour of\n"
        "a real live system. "
        )


def valid_threshold(f):
    """Determine if f is a float between 0 and 1."""
    f = float(f)
    if f < 0.0 or f > 1.0:
        msg = f"Invalid threshold value: {f} is not in range [0.0, 1.0]"
        raise argparse.ArgumentTypeError(msg)

def parse_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(prog="mosyco",
        description=desc,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Log verbosity
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose",
            help="Debug mode: generate more verbose log output",
            action="store_true")

    group.add_argument("-q", "--quiet",
            help="Silence output: suppress any console or log output",
            action="store_true")

    # Data columns
    parser.add_argument("-m", "--models",
            help="A list of the model data columns. e.g. --models 'PAmodel1' 'PAmodel2'",
            nargs='+', default=model_list)

    parser.add_argument("-s", "--systems",
            help="A list of the actual system data columns. e.g. --systems 'PAseasonal' 'PAtrend'",
            nargs='+', default=system_list)

    # Threshold value
    parser.add_argument("-t", "--threshold",
            help="The initial threshold used for the gap analysis",
            default=default_threshold,
            type=valid_threshold)

    # Animation
    parser.add_argument("--gui",
            help="GUI-mode: show live updating plots. This will only work " +
            "if for single model and system values.",
            action="store_true")

    # Log to file
    parser.add_argument("--logfile",
            help="Log to a file called 'mosyco.log'",
            action="store_true")

    args = parser.parse_args()

    if args.gui and (len(args.systems) > 1):
        print(" GUI-mode is only available for a single system and model.")
        sys.exit()

    if args.quiet:
        args.loglevel = logging.CRITICAL
    elif args.verbose:
        args.loglevel = logging.DEBUG
    else:
        args.loglevel = logging.INFO

    return args
