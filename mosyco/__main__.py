# -*- coding: utf-8 -*-

import pandas as pd
import logging

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

    def run(self):
        """Run the main loop of the Mosyco App with arguments."""
        for (date, value) in self.reader.actual_value_gen():
            self.inspector.receive_actual_value((date, value), self.reader.current_system)

            # create a forecast every year and eval model based on it
            if date.month == 12 and date.day == 31:
                next_year = date.year + 1

                log.info(f'current date: {date.date()}')
                # model data ends July 2015 so we don't need a forecast for that year
                if not next_year == 2015:
                    # generate the new forecast
                    period = pd.Period(next_year)
                    log.info(f'Generating forecast for {period}...')
                    self.inspector.predict(period, self.args.system)
                    # forecast number is now in inspector.forecast dataframe

                    # errors is a dataframe of the year with NaN values where the
                    # model data falls outside the forecast confidence interval
                    # TODO: could be used for plotting
                    # errors = inspector.eval_future(next_year)
                    self.inspector.eval_future(period)

                (exceeds_threshold, deviation) = self.inspector.eval_actual(date, self.args.system)

                if exceeds_threshold:
                    deviation_count += 1

        log.info(f'Total: {deviation_count} model-actual deviations detected.')
        log.info('...finished!')

# ==============================================================================

# read command line arguments & set log level
args = mosyco.parser.parse_arguments()
log.setLevel(args.loglevel)

log.info('Starting mosyco...')
log.debug('running in DEBUG Mode')

# Run Mosyco
app = Mosyco(args)
app.run()
