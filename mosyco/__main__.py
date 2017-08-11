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
    """Represents an instance of the Model-System-Controller Prototype."""
    def __init__(self, args):
        """Create a new Mosyco app."""
        self.args = args
        self.reader = Reader(args.system)
        self.inspector = Inspector(self.reader.df.index, self.reader.df[args.model])
        self.plotter = Plotter(self)
        self.deviation_count = 0

    def run(self):
        self.plotter.show_plot()

    def loop(self):
        for (date, value) in self.reader.actual_value_gen():

            self.inspector.receive_actual_value((date, value), self.reader.current_system)

            # create a forecast every year and evaluate the model based on it
            if date.month == 12 and date.day == 31:
                next_year = date.year + 1

                log.info(f'current date: {date.date()}')

                # model data ends July 2015 so we don't need a forecast for that year
                if not next_year == 2015:

                    period = pd.Period(next_year)
                    log.info(f'Generating forecast for {period}...')

                    # generate the new forecast
                    self.current_fc_thread = Thread(target=self.inspector.predict, args=(period, self.args.system))
                    self.current_fc_thread.start()
                    # self.inspector.predict(period, self.args.system)
                    # this returns a dataframe of the period with NaN values
                    # where the model data falls outside the forecast
                    # confidence interval. TODO: could be used for plotting

                # TODO: take out early exit
                if next_year == 1998:
                    # TODO: how to exit program cleanly
                    log.info('The program has terminated, \
                             please close the plot to exit cleanly.')
                    break

                (exceeds_threshold, _) = self.inspector.eval_actual(date, self.args.system)
                if exceeds_threshold:
                    self.deviation_count += 1

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

log.info(f'Total: {app.deviation_count} model-actual deviations detected.')
log.info('...finished!')
