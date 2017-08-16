# -*- coding: utf-8 -*-
import pandas as pd
import logging
from threading import Thread

from mosyco.plotter import Plotter
from mosyco.inspector import Inspector
from mosyco.reader import Reader
import mosyco.parser

log = logging.getLogger(__name__)

# ==============================================================================
class Mosyco():
    """Represents an instance of the Model-System-Controller Prototype.

    The Mosyco architecture combines Reader and Inspector to simulate the live
    observation of a running system.

    Attributes:
        args: command line arguments
        reader: mosyco.Reader instance
        inspector: mosyco.Inspector instance
        plotter: mosyco.Plotter instance
    """

    def __init__(self, args):
        """Create a new Mosyco instance.

        Args:
            args: The command line arguments from mosyco.parser
        """
        self.args = args
        self.reader = Reader(args.system)
        self.inspector = Inspector(self.reader.df.index, self.reader.df[args.model])
        self.plotter = Plotter(self)
        self.deviation_count = 0

    def run(self):
        """Start and run the Mosyco system."""
        self.plotter.show_plot()

    def loop(self):
        """Generator used as the Mosyco main loop."""
        for (date, value) in self.reader.actual_value_gen():

            # simulate new system data arriving
            self.inspector.receive_actual_value((date, value), self.reader.current_system)

            # evaluate difference between actual and model data
            (exceeds_threshold, _) = self.inspector.eval_actual(date, self.args.system)
            if exceeds_threshold:
                self.deviation_count += 1

            next_year = date.year + 1

            # at the end of each period, create a forecast for the following
            # TODO: allow flexible period as argument
            if date.month == 12 and date.day == 31:

                log.debug(f'current date: {date.date()}')

                period = pd.Period(next_year)
                log.info(f'Generating forecast for {period}...')

                # generate the new forecast in separate thread
                self.current_fc_thread = Thread(target=self.inspector.predict, args=(period, self.args.system))
                self.current_fc_thread.start()

            # pass data through to plotting engine
            yield (date, value)

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
