# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pylab as plt
import matplotlib.animation as animation

import time
import pandas as pd
import numpy as np
import logging

import asyncio

# from mosyco.animate import AnimatedPlot
from mosyco.inspector import Inspector
from mosyco.reader import Reader
import mosyco.parser

log = logging.getLogger(__name__)

class AnimatedPlot():
    """An animated plot of mosyco."""
    def __init__(self, inspector, system, actual_value_gen):
        # plt.ion()
        # self.stream = self.data_stream()
        self.inspector = inspector
        self.system = system

        # Setup the figure and axes...
        self.init_plot()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update,
                                            # init_func=self.init_plot,
                                            frames=actual_value_gen,
                                            interval=5, blit=True)


    def init_plot(self):
        self.fig, self.ax = plt.subplots()
        self.inspector.df[self.system] = np.nan
        self.actual_line, = self.ax.plot(self.inspector.index,
                                 [0 for i in range(self.inspector.df.size)])

        return self.actual_line, self.ax

    def update(self, new_value):
        """Update the plot."""
        (date, value) = new_value
        # send value to inspector
        inspector.receive_actual_value((date, value), reader.current_system)

        # create a forecast every year and eval model based on it
        if date.month == 12 and date.day == 31:
            next_year = date.year + 1

            # ======================================================================
            # REMOVE THIS
            if next_year == 2000:
                import sys
                sys.exit()
            # ======================================================================

            log.info(f'current date: {date.date()}')

            # model data ends July 2015 so we don't need a forecast for that year
            if not next_year == 2015:
                # generate the new forecast
                log.info(f'Generating forecast for {next_year}...')
                inspector.forecast_period(pd.Period(next_year), args.system)
                # forecast number is now in inspector.forecast dataframe

                # errors is a dataframe of the year with NaN values where the
                # model data falls outside the forecast confidence interval
                # TODO: could be used for plotting
                # errors = inspector.eval_future(next_year)
                inspector.eval_future(next_year)


        (exceeds_threshold, deviation) = inspector.eval_actual(date, args.system)
        # ==============================================================================

        # need to make sure that new data has come in:
        # TODO: how better? asyncio

        # TODO: try catch block for KeyError during first call
        try:
            data = self.inspector.df[self.system]
            self.actual_line.set_data(data.index, data.values)
            # self.actual_line = self.ax.plot(actual_data)[0]
        except KeyError as e:
            log.info(f'No {self.system} data available for plotting yet')
            # dummy line
            # self.actual_line =
            self.actual_line = self.ax.plot([0, 0])

        return self.actual_line,


    def show(self):
        plt.show()

# ==============================================================================
# read command line arguments & set log level
args = mosyco.parser.parse_arguments()
log.setLevel(args.loglevel)

loop = asyncio.get_event_loop()

# initialize reader and inspector
reader = Reader(args.system)
inspector = Inspector(reader.df.index, reader.df[args.model])

# animation update cycle is now the main loop
ani_plot = AnimatedPlot(inspector, args.system, reader.actual_value_gen())
ani_plot.show()
