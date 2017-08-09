# -*- coding: utf-8 -*-
import pdb
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import numpy as np
import logging
from threading import Thread

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
        self.deviation_count = 0


        # if self.args.animate:
        self.prepare_plot()

    def prepare_plot(self):
        self.inspector.df[self.args.system] = np.nan
        self.fig, self.ax = plt.subplots()

        # TODO: better way to initialize line plot?!
        self.actual_line, = self.ax.plot(self.inspector.df.index,
                                        [0 for i in range(len(self.inspector.df))])

        self.ax.set_ylim(800, 1300)
        self.ani = animation.FuncAnimation(self.fig, self.update_plot,
                                                init_func=self.init_plot,
                                                frames=self.loop,
                                                interval=16, blit=True)

    def init_plot(self):
        return self.actual_line,

    def update_plot(self, i):
        self.actual_line.set_ydata(self.inspector.df[self.args.system])
        return self.actual_line,

    def run(self):
        plt.show()


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
                    t = Thread(target=self.inspector.predict, args=(period, self.args.system))
                    t.start()
                    # self.inspector.predict(period, self.args.system)
                    # this returns a dataframe of the period with NaN values
                    # where the model data falls outside the forecast
                    # confidence interval. TODO: could be used for plotting


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
