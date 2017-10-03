# -*- coding: utf-8 -*-
import pandas as pd
import logging
import queue
import time
from threading import Thread

from mosyco.plotter import Plotter
from mosyco.inspector import Inspector
from mosyco.reader import Reader
import mosyco.parser
import mosyco.helpers as helpers

logging.getLogger('fbprophet').setLevel(logging.WARNING)
log = logging.getLogger(__package__)

# ==============================================================================
class Mosyco():
    """Represents an instance of the Model-System-Controller Prototype.

    The Mosyco architecture combines Reader and Inspector to simulate the live
    observation of a running system.

    Attributes:
        args: command line arguments
        queue: Queue for communication between reader and inspector
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
        self.queue = queue.Queue()
        self.reader = Reader(args.systems, self.queue)
        self.inspector = Inspector(self.reader.df.index,
                                    self.reader.df[args.models], args,
                                    self.queue)
        if self.args.gui:
            self.plotter = Plotter(self)
        self.fc_threads = []
        self.deviation_count = 0

    def run(self):
        """Start and run the Mosyco system."""
        if self.args.gui:
            self.plotter.show_plot()
        else:
            self.reader.start()
            for res in self.loop():
                log.debug(f'Ran through iteration. res: {res}')


    def loop(self):
        # silence suppresses stdout (to deal with pystan bug)
        with helpers.silence():
            for t in self.inspector.receive():
                assert len(self.args.systems) == len(t[1:])
                values = t._asdict()
                date = values.pop('Index')

                for system_name, val in values.items():
                    (exceeds_threshold, _) = self.inspector.eval_actual(date, system_name)
                    # TODO: how to output threshold deviations
                    log.debug(f'Date: {date.date()} ' + \
                        f'- Model-Actual deviation for system: {system_name}')

                next_year = date.year + 1

                # at the end of each period, create a forecast for the following
                # TODO: allow flexible period as argument
                if date.month == 12 and date.day == 31:

                    log.debug(f'Current date: {date.date()}')

                    period = pd.Period(next_year)

                    # generate forecasts for each system
                    if date.year == 2015:
                        break
                    for sys in self.args.systems:
                        log.info(f'Generating {sys} forecast for {period}...')

                        # generate the new forecasts separate threads
                        t = Thread(target=self.inspector.predict,
                                    name='-'.join(['Thread', sys, str(period)]),
                                    args=(period, sys),
                                    daemon=True)
                        t.start()

                # pass data through to plotting engine
                yield (date, values)


# ==============================================================================

# read command line arguments & set log level
args = mosyco.parser.parse_arguments()
log.setLevel(args.loglevel)

log.info('Starting mosyco...')
log.debug('running in DEBUG Mode')

# Run Mosyco
app = Mosyco(args)
app.run()

log.debug(f'Total: {app.deviation_count} model-actual deviations detected.')
