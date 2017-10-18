# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvas
import matplotlib.animation as animation
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec

from PyQt5 import QtCore, QtWidgets

import logging
import pandas as pd
from dateutil.relativedelta import relativedelta
import multiprocessing as mp
from queue import Empty

from functools import partial
from collections import defaultdict, deque

log = logging.getLogger(__name__)

class Plotter(QtWidgets.QApplication):
    """The Plotter is responsible for animating the Mosyco data.

    Attributes:
        inspector: Reference to the Inspector object
        reader: Reference to the Reader object
        plotting_queue: Queue used for communicating with Inspector
    """
    def __init__(self, args, reader, inspector, plotting_queue):
        super().__init__([__package__])
        self.args = args
        # there is only one model & system in GUI mode
        self.system_name = args.systems[0]
        self.model_name = args.models[0]
        self.reader_thread = reader
        self.inspector = inspector
        self.plotting_queue = plotting_queue

        # dic attempt
        # defaultdict w/ column names as keys and a deque of equal length
        # for each column...
        # model series
        self.model_data = inspector.df[[self.model_name]].copy()
        self.data = defaultdict(partial(deque, maxlen=400))


        # TODO: get this from somewhere or leave as default
        # this needs to be half the period b/c we need to divide it later
        # and relativedeltas can not always be divided but always multiplied
        self.half_period_length = relativedelta(months=6)
        self.deviation_count = 0
        self.artists = []
        self.paused = False
        self.update_legend = False
        self.prepare_plot()


    def run(self):
        # Todo: Daemon?!
        self.process = mp.Process(target=self._run_mosyco, daemon=True)
        self.process.start()
        # start gui
        self.main_widget.show()
        self.exec_()


    def _run_mosyco(self):
        self.reader_thread.start()
        self.inspector.start()



    def prepare_plot(self):
        """Prepare drawable objects for the animation."""

        matplotlib.style.use('seaborn')

        self.fig = Figure(tight_layout=True)
        gs = GridSpec(3, 1, height_ratios=[1, 4, 4])
        self.ax1 = self.fig.add_subplot(gs[1])
        self.ax2 = self.fig.add_subplot(gs[2], sharex=self.ax1)


        self.ax1.set_title('System View')
        self.ax2.set_title('Forecast View')

        self.ax1.set_ylabel('Units')
        self.ax2.set_ylabel('Units')

        # actual system lines
        (self.acl1, ) = self.ax1.plot([], [], c='blue', ls='solid', lw=0.7)
        (self.acl2, ) = self.ax2.plot([], [], c='blue', ls='solid', lw=0.7)

        self.fc_lines = deque(maxlen=4)

        # plot model w/ standard confidence interval
        self.plot_model()

        # add lines to artist list
        self.artists.extend([self.acl1, self.acl2])

        # TODO: set lim automatically
        self.ax1.set_ylim(800, 1300)
        self.ax2.set_ylim(800, 1300)

        self.ax1.set_autoscaley_on(True)
        self.ax2.set_autoscaley_on(True)

        # prepare initial limits for the x-axes
        start_date = self.model_data.index[0]
        self.ax1.set_xlim(start_date, start_date
                          + self.half_period_length * 2)
        # self.ax2.set_xlim(start_date, start_date
        #                   + self.half_period_length * 4)

        # add the legends
        self.leg_dict = {
            'Live System': self.acl1,
            'Model': self.m_line1,
            'Model Threshold': self.model_error,
        }
        l = (self.leg_dict.values(), self.leg_dict.keys())


        # self.ax2.legend(*legend_items, loc='center',
        #             bbox_to_anchor=(0.5, -0.6),)

        self.legend = self.fig.legend(*l, loc='upper center',
                                        ncol=3, mode='expand')

        # rotate tick labels for all subplots
        self.fig.autofmt_xdate(bottom=0.2)

        # tight_layout call should be at the end of this function
        # self.fig.set_tight_layout(True)

        # prepare the canvas
        self.prepare_canvas()

        # setup animation
        self.ani = animation.FuncAnimation(
            fig=self.fig,
            func=self.update,
            frames=self.get_data,
            interval=200,
            blit=False,
            )

    def plot_model(self):
        # add upper and lower bounds w/ standard threshold
        # TODO: make variable threshold possible
        md = self.model_data[self.model_name]
        self.model_data['upper_bound'] = md + self.args.threshold * md
        self.model_data['lower_bound'] = md - self.args.threshold * md

        # save a resampled version of the model data
        self.rs_model = self.model_data.resample('W').mean()
        rs_md = self.rs_model[self.model_name]

        # model resampled
        (self.m_line1, ) = self.ax1.plot(
            rs_md.index,
            rs_md.values,
            c='green',
            ls='solid',
            lw=0.7,
            alpha=0.7,
            )

        # plot the resampled model line
        (self.m_line2, ) = self.ax2.plot(
            rs_md.index,
            rs_md.values,
            c='green',
            ls='solid',
            lw=0.7,
            alpha=0.7,
            )

        # plot the model threshold
        self.model_error = self.ax1.fill_between(
            rs_md.index,
            rs_md.values - self.args.threshold * rs_md.values,
            rs_md.values + self.args.threshold * rs_md.values,
            alpha=0.3,
            color='green',
            linestyle=':',
            )

    def prepare_canvas(self):
        """Prepare the Backend Canvas for drawing on it."""
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                    QtWidgets.QSizePolicy.Expanding)
        self.canvas.updateGeometry()

        self.main_widget = QtWidgets.QWidget()
        self.main_widget.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.main_widget.setWindowTitle('Model-/System-Controller '
            + 'Architecture Prototype')

        layout = QtWidgets.QVBoxLayout(self.main_widget)
        layout.addWidget(self.canvas)

        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.canvas.setFocus()

        def keypress(e):
            if e.key == 'escape':
                self.closeAllWindows()
            elif e.key == ' ':
                # pause / unpause
                self.paused = not self.paused

        self.canvas.mpl_connect('key_press_event', keypress)


    def get_data(self):
        """Receive data from the inspector."""
        while True:
            while self.paused:
                yield None

            new_data = []
            fc = None

            while len(new_data) < 3:
                try:
                    obj = self.plotting_queue.get_nowait()
                except Empty:
                    break

                if isinstance(obj, dict):
                    new_data.append(obj)
                else:
                    # object is a new forecast
                    fc = obj
                    break


            if len(new_data) > 0:
                yield new_data
                if fc is not None:
                    yield fc
            else:
                yield fc


    def update(self, obj):
        """Determine what object was received and update plot accordingly."""
        if obj is None:
            return self.artists
        elif isinstance(obj, pd.DataFrame):
            return self.plot_forecast(obj)
        else:
            return self.plot_actual(obj)


    def plot_actual(self, rows):
        """This function updates various plot elements.

        It is called in regular interval during the animation loop and is
        responsible for redrawing the lines and axes."""

        # add new rows to plotting data
        for row in rows:
            for k, v in row.items():
                self.data[k].append(v)

        # last row is current date
        date = rows[-1]['Index']

        # resampled plot; iloc[:-1] cuts of the most recent week
        self.resampled_actual = pd.Series(index=self.data['Index'],
                    data=self.data[self.system_name]).resample('W').mean().iloc[:-1]

        self.acl1.set_data(self.resampled_actual.index, self.resampled_actual.values)
        self.acl2.set_data(self.resampled_actual.index, self.resampled_actual.values)



        # get current upper bound of date axis
        ax1_right_lim = matplotlib.dates.num2date(self.ax1.get_xlim()[1])

        # calculate center and remove timezone information for comparison
        ax1_center = ax1_right_lim - self.half_period_length
        ax1_center = ax1_center.replace(tzinfo=None)

        # set the new x_axis limits
        if date > ax1_center:
            self.ax1.set_xlim(date - self.half_period_length, date
                              + self.half_period_length)

        # plot model-actual errors
        self.plot_model_actual_deviation()

        # adjust y-axis
        self.ax1.relim(visible_only=True)
        self.ax2.relim(visible_only=True)
        self.ax1.autoscale_view(tight=None, scalex=False, scaley=True)
        self.ax2.autoscale_view(tight=None, scalex=False, scaley=True)

        # return all artists that need to be redrawn
        return self.artists



    def plot_forecast(self, fc):
        """Draw a new forecast. Called whenever a new one is available."""

        rs_m = self.rs_model.loc[fc.index, self.model_name]

        # draw forecast confidence interval
        self.fc_error = self.ax2.fill_between(
            fc.index,
            fc['yhat_lower'],
            fc['yhat_upper'],
            alpha=0.2,
            color='orange',
            linestyle=':',
            )

        # draw deviation between forecast and model
        # below
        self.dev_warn_below = self.ax2.fill_between(
            fc.index,
            fc['yhat_lower'],
            rs_m.values,
            where=rs_m.values < fc['yhat_lower'],
            interpolate=True,
            alpha=0.2,
            color='fuchsia',
            linestyle=':',
            )

        # above
        self.dev_warn_above = self.ax2.fill_between(
            fc.index,
            fc['yhat_upper'],
            rs_m.values,
            where=rs_m.values > fc['yhat_upper'],
            interpolate=True,
            alpha=0.2,
            color='fuchsia',
            linestyle=':',
            )


        (fc_line, ) = self.ax2.plot(
                fc.index,
                fc['yhat'],
                c='black',
                ls='dashed',
                lw=0.5,
                alpha=0.4,
                )
        self.fc_lines.append(fc_line)
        if len(self.fc_lines) is 1:
            # update legend
            d = {'Forecast \u00B1 CI': (self.fc_lines[-1], self.fc_error), 'Model-Forecast Deviation': self.dev_warn_above}
            self.leg_dict.update(d)
            l = (self.leg_dict.values(), self.leg_dict.keys())

            self.legend.remove()
            self.legend = self.fig.legend(*l, loc='upper center',
                                            ncol=3, mode='expand')

        return self.artists

    def plot_model_actual_deviation(self):
        # draw deviation between model and actual lines
        idx = self.resampled_actual.index
        ml_upper = self.rs_model.loc[idx, 'upper_bound']
        ml_lower = self.rs_model.loc[idx, 'lower_bound']
        ac = self.resampled_actual.values

        # We cannot update a PolyCollection so we need to delete the old
        # deviation patches and draw a new one.
        try:
            self.actual_dev_below.remove()
            self.actual_dev_above.remove()
        except AttributeError:
            self.update_legend = True
            pass

        self.actual_dev_below = self.ax1.fill_between(
            idx,
            ml_lower,
            ac,
            where=ac < ml_lower,
            interpolate=True,
            alpha=0.2,
            color='red',
            linestyle=':',
            )

        # above
        self.actual_dev_above = self.ax1.fill_between(
            idx,
            ml_upper,
            ac,
            where=ac > ml_upper,
            interpolate=True,
            alpha=0.2,
            color='red',
            linestyle=':',
            )
        # TODO: when to update
        if self.update_legend:
            self.update_legend = False
            d = {'Model-System Deviation': self.actual_dev_below}
            self.leg_dict.update(d)
            l = (self.leg_dict.values(), self.leg_dict.keys())

            self.legend.remove()
            self.legend = self.fig.legend(*l, loc='upper center',
                                            ncol=3, mode='expand')
