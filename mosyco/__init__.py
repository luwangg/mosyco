# -*- coding: utf-8 -*-
import multiprocessing as mp
from queue import Queue

from mosyco.reader import Reader
from mosyco.plotter import Plotter
from mosyco.inspector import Inspector


class Mosyco():
    """Represents an instance of the Model-System-Controller Prototype.

    The Mosyco architecture combines Reader and Inspector to simulate the live
    observation of a running system.

    Attributes:
        args: command line arguments
        reader_queue: Queue for communication between reader and inspector
        plotting_queue: Queue for communication between inspector and plotter
        reader: mosyco.Reader instance
        inspector: mosyco.Inspector instance
        plotter: mosyco.Plotter instance if GUI-mode is enabled
    """

    def __init__(self, args):
        """Create a new Mosyco instance.

        Args:
            args: The command line arguments from mosyco.parser
        """
        self.args = args
        self.reader_queue = Queue()
        plotting_queue = mp.Queue() if args.gui else None

        self.reader = Reader(args.systems, self.reader_queue)
        self.inspector = Inspector(self.reader.df.index.copy(),
                                    self.reader.df[args.models],
                                    self.args,
                                    self.reader_queue,
                                    plotting_queue)

        if self.args.gui:
            self.plotter = Plotter(self.args, self.reader, self.inspector, plotting_queue)

    def run(self):
        """Start and run the Mosyco system."""

        # Either start Inspector thread from GUI or manually
        if self.args.gui:
            self.plotter.run()
        else:
            self.reader.start()
            self.inspector.start()
