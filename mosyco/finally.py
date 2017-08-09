# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

import pandas as pd
import numpy as np
import logging
from threading import Thread
from dateutil.relativedelta import relativedelta

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
        # TODO: get this from somewhere or leave as default
        # need to be half the period b/c we need to divide it later
        # and relativedeltas can not always be divided but always multiplied
        self.half_period_length = relativedelta(months=6)
        self.deviation_count = 0
        self.artists = []
        self.prepare_plot()

    def prepare_plot(self):
        plt.style.use('seaborn')
        self.inspector.df[self.args.system] = np.nan
        self.inspector.forecast['yhat'] = np.nan
        # ax1 contains the actual data plot, ax2 the forecast
        # self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3)
        self.fig, (self.ax1, self.ax2) = plt.subplots(2)
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        self.fig.suptitle("Model-/System-Controller Architecture Prototype",
                          fontsize=14,
                          fontweight='bold',)

        self.ax1.set_title('Live System View')
        self.ax2.set_title('Forecast Detail View')
        # self.ax3.set_title('Static Model View')

        self.ax1.set_ylabel('Units')
        self.ax2.set_ylabel('Units')
        # self.ax3.set_ylabel('Units')


        # TODO: better way to initialize line plots?!

        # actual system line
        self.ac_line, = self.ax2.plot(self.inspector.df.index,
                                      [0 for i in range(len(self.inspector.df))],
                                      c='blue',
                                      ls='solid',
                                      label='Live System',)

        # resampled
        self.acr_line, = self.ax1.plot(self.inspector.df.index,
                                      [0 for i in range(len(self.inspector.df))],
                                      c='blue',
                                      ls='solid',
                                      label='Live System Resampled Weekly',)

        # add lines to artist list
        self.artists.extend([self.ac_line, self.acr_line])

        # uncertainty corridor / confidence interval for forecast
        # self.ci = self.draw_uncertainty()

        # TODO: set lim automatically
        self.ax1.set_ylim(900, 1200)
        self.ax2.set_ylim(900, 1200)
        # self.ax3.set_ylim(800, 1300)

        self.ax1.set_autoscaley_on(True)
        self.ax2.set_autoscaley_on(True)

        # prepare initial limits for the x-axes
        start_date = self.inspector.df.index[0]
        self.ax1.set_xlim(start_date, start_date + self.half_period_length * 4)
        self.ax2.set_xlim(start_date, start_date + self.half_period_length * 2)

        # add the legend
        self.ax1.legend()
        self.ax2.legend()

        # rotate tick labels for all subplots
        for ax in self.fig.axes:
            matplotlib.pyplot.sca(ax)
            plt.xticks(rotation=30)

        # tight_layout call should be at the end of this function
        self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        # setup animation
        self.ani = animation.FuncAnimation(fig=self.fig,
                                           func=self.update_plot,
                                           init_func=self.init_plot,
                                           frames=self.loop,
                                           interval=20, blit=False)

    def init_plot(self):
        return self.artists

    def update_plot(self, t):
        (date, value) = t

        # resampled plot
        resampled = self.inspector.df[self.args.system].resample('W').mean()
        self.acr_line.set_data(resampled.index, resampled.values)

        # detailed plot
        self.ac_line.set_ydata(self.inspector.df[self.args.system])

        # get current upper bound of date axis
        right_lim = matplotlib.dates.num2date(self.ax1.get_xlim()[1])
        # remove timezone information for comparison
        center = right_lim - self.half_period_length
        center = center.replace(tzinfo=None)

        # set the new limits
        if date > center:
            self.ax1.set_xlim(date - self.half_period_length * 2,
                              date + self.half_period_length * 2)
            self.ax2.set_xlim(date - self.half_period_length,
                              date + self.half_period_length)


        # check if we need to plot new forecast
        if self.inspector.new_fc_available:

            # reset flag
            self.inspector.new_fc_available = False

            # update forecast line
            fc_resampled = self.inspector.forecast['yhat'].resample('W').mean()

            # We cannot update a PolyCollection so we need to delete the old
            # uncertainty corridor and draw a new one.
            try:
                self.ci.remove()
            except AttributeError:
                pass
            self.ci = self.draw_uncertainty()

            # create update or create the forecast line plot
            try:
                self.fc_line.set_data(fc_resampled.index, fc_resampled.values)
            except AttributeError:
                self.fc_line, = self.ax2.plot(fc_resampled.index,
                                              fc_resampled.values,
                                              c='black',
                                              ls='dashed',
                                              alpha=0.4,
                                              label='Forecast',)
                self.artists.append(self.fc_line)
                # add fc and uncertainty to legend
                self.ax2.get_legend().remove()
                self.ax2.legend()


        # set the date axis so current date is in middle
        start = date - self.half_period_length
        stop = date + self.half_period_length
        self.ax2.set_xlim(start, stop)

        # adjust y-axis
        self.ax1.relim()
        self.ax2.relim()
        # TODO: tight setting?!
        self.ax1.autoscale_view(tight=None, scalex=False, scaley=True)
        self.ax2.autoscale_view(tight=None, scalex=False, scaley=True)

        # return all artists that need to be redrawn
        return self.artists

    def run(self):
        plt.show()


    def draw_uncertainty(self):
        # TODO: resampled or not?
        rs = self.inspector.forecast.resample('W').mean()
        self.ci = self.ax2.fill_between(rs.index,
                                        rs['yhat_lower'],
                                        rs['yhat_upper'],
        # self.ci = self.ax2.fill_between(self.inspector.forecast.index,
        #                                 self.inspector.forecast['yhat_lower'],
        #                                 self.inspector.forecast['yhat_upper'],
                                        alpha=0.4,
                                        color='orange',
                                        linestyle=':',
                                        label='Forecast CI',)

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
