# -*- coding: utf-8 -*-
import logging
import threading
import numpy as np
from dateutil.relativedelta import relativedelta

import dash
from dash.dependencies import Input, Output, Event
import dash_core_components as dcc
import dash_html_components as html

import plotly.plotly as py
from plotly.graph_objs import Figure, Scatter

log = logging.getLogger(__name__)



app = dash.Dash()

app.layout = html.Div([
    html.Button('Start', id='start-button'),
    dcc.Graph(id='time-series'),
    dcc.Interval(id='graph-update', interval=1000),
])

@app.callback(output=Output('time-series', 'figure'),
                events=[Event('graph-update', 'interval')])




class Plotter(dash.Dash):
    def __init__(self, mosyco, plotting_queue, **kwargs):
        super().__init__(self, **kwargs)
        super().__init__(self, csrf_protect=False, **kwargs)

        self.mosyco = mosyco
        self.plotting_queue = plotting_queue

    def update_time_series(self):
        # plot the actual system
        # TODO: copy?!
        df = self.mosyco.inspector.df.copy()
        trace = Scatter(
            y=df['PAseasonal'],
            mode='lines',
        )
        return Figure(data=[trace])

    # def run_server(self, mosyco,**kwargs):
    #     super().__run_server__(self, **kwargs)


# import matplotlib
# matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# import logging
# import numpy as np
# from dateutil.relativedelta import relativedelta

# log = logging.getLogger(__name__)


# class Plotter:
#     """The Plotter is responsible for animating the Mosyco data.

#     Attributes:
#         mosyco: Reference to the Mosyco object
#         args: The application's command line arguments
#         inspector: The inspector instance
#     """

#     def __init__(self, mosyco):
#         """Create a new Plotter instance.

#         Args:
#             mosyco: The Mosyco/Application object
#         """

#         self.mosyco = mosyco
#         self.args = mosyco.args
#         self.inspector = mosyco.inspector

#         # TODO: get this from somewhere or leave as default
#         # need to be half the period b/c we need to divide it later
#         # and relativedeltas can not always be divided but always multiplied
#         self.half_period_length = relativedelta(months=6)
#         self.deviation_count = 0
#         self.artists = []
#         self.prepare_plot()

#     def show_plot(self):
#         """Display the animation window and start the FuncAnimation."""
#         plt.show()

#     def prepare_plot(self):
#         """Prepare drawable objects for the animation."""

#         plt.style.use('seaborn')
#         self.inspector.df[self.args.system] = np.nan
#         self.inspector.forecast['yhat'] = np.nan

#         self.fig = plt.figure()
#         self.ax1 = self.fig.add_subplot(211)
#         self.ax2 = self.fig.add_subplot(212)
#         self.fig.canvas.set_window_title('Mosyco')

#         self.fig.suptitle('Model-/System-Controller Architecture Prototype'
#                           , fontsize=14, fontweight='bold')

#         self.ax1.set_title('Detailed System View')
#         self.ax2.set_title('System Overview')

#         self.ax1.set_ylabel('Units')
#         self.ax2.set_ylabel('Units')

#         # TODO: better way to initialize line plots than list comprehension ?!

#         # actual system line
#         (self.ac_line, ) = self.ax1.plot(self.inspector.df.index, [0
#                 for i in range(len(self.inspector.df))], c='blue',
#                 ls='solid', lw=0.5)

#         # actual resampled
#         (self.acr_line, ) = self.ax2.plot(self.inspector.df.index, [0
#                 for i in range(len(self.inspector.df))], c='blue',
#                 ls='solid', lw=0.7)

#         rs = self.inspector.df[self.args.model].resample('W').mean()

#         # model resampled
#         (self.m_line, ) = self.ax2.plot(
#             rs.index,
#             rs.values,
#             c='green',
#             ls='solid',
#             lw=0.7,
#             alpha=0.7,
#             )

#         # add lines to artist list
#         self.artists.extend([self.ac_line, self.acr_line])

#         # TODO: set lim automatically
#         self.ax1.set_ylim(900, 1200)
#         self.ax2.set_ylim(900, 1200)

#         self.ax1.set_autoscaley_on(True)
#         self.ax2.set_autoscaley_on(True)

#         # prepare initial limits for the x-axes
#         start_date = self.inspector.df.index[0]
#         self.ax1.set_xlim(start_date, start_date
#                           + self.half_period_length * 2)
#         self.ax2.set_xlim(start_date, start_date
#                           + self.half_period_length * 4)

#         # add the legend
#         self.ax1.legend([self.ac_line], ['Live System'])
#         self.ax2.legend([self.acr_line, self.m_line],
#                         ['System Weekly Mean', 'Model Weekly Mean'])

#         # rotate tick labels for all subplots
#         for ax in self.fig.axes:
#             matplotlib.pyplot.sca(ax)
#             plt.xticks(rotation=30)

#         # tight_layout call should be at the end of this function
#         self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])

#         # setup animation
#         self.ani = animation.FuncAnimation(
#             fig=self.fig,
#             func=self.update_plot,
#             init_func=self.init_plot,
#             frames=self.mosyco.loop,
#             interval=200,
#             blit=False,
#             )

#     def init_plot(self):
#         """This function is called once before the first frame is drawn."""
#         return self.artists

#     def update_plot(self, t):
#         """This function updates the plot elements.

#         It is called in regular intervale during the animation loop and is
#         responsible for redrawing the lines and axes."""

#         (date, value) = t

#         # resampled plot
#         resampled = self.inspector.df[self.args.system].resample('W'
#                 ).mean()
#         self.acr_line.set_data(resampled.index, resampled.values)

#         # detailed plot
#         self.ac_line.set_ydata(self.inspector.df[self.args.system])

#         # get current upper bound of date axis
#         ax1_right_lim = \
#             matplotlib.dates.num2date(self.ax1.get_xlim()[1])
#         ax2_right_lim = \
#             matplotlib.dates.num2date(self.ax2.get_xlim()[1])

#         # calculate center and remove timezone information for comparison
#         ax1_center = ax1_right_lim - self.half_period_length
#         ax2_center = ax2_right_lim - self.half_period_length * 2
#         ax1_center = ax1_center.replace(tzinfo=None)
#         ax2_center = ax2_center.replace(tzinfo=None)

#         # set the new x_axis limits
#         if date > ax1_center:
#             self.ax1.set_xlim(date - self.half_period_length, date
#                               + self.half_period_length)
#         if date > ax2_center:
#             self.ax2.set_xlim(date - self.half_period_length * 2, date
#                               + self.half_period_length * 2)

#         # check if we need to plot new forecast
#         if self.inspector.new_fc_available:

#             # reset flag & draw the forecast elements

#             self.inspector.new_fc_available = False
#             self.draw_forecast()

#         # adjust y-axis
#         self.ax1.relim()
#         self.ax2.relim()
#         self.ax1.autoscale_view(tight=None, scalex=False, scaley=True)
#         self.ax2.autoscale_view(tight=None, scalex=False, scaley=True)

#         # return all artists that need to be redrawn

#         return self.artists

#     def draw_forecast(self):
#         """Draw the plot elements related to the forecasts.

#         This function is called once from within update_plot() when a new
#         forecast is available for drawing.
#         """

#         # resample values for smoother plot
#         rs_fc = self.inspector.forecast.resample('W').mean()
#         rs_m = self.inspector.df[self.args.model].resample('W').mean()

#         # We cannot update a PolyCollection so we need to delete the old
#         # uncertainty corridor and warning patches and draw a new one.
#         try:
#             self.ci.remove()
#             self.dev_warn_below.remove()
#             self.dev_warn_above.remove()
#         except AttributeError:
#             pass

#         # draw forecast confidence interval
#         self.ci = self.ax2.fill_between(
#             rs_fc.index,
#             rs_fc['yhat_lower'],
#             rs_fc['yhat_upper'],
#             alpha=0.2,
#             color='orange',
#             linestyle=':',
#             )

#         # draw deviation between forecast and model
#         # below
#         self.dev_warn_below = self.ax2.fill_between(
#             rs_fc.index,
#             rs_fc['yhat_lower'],
#             rs_m.values,
#             where=rs_m.values < rs_fc['yhat_lower'],
#             interpolate=True,
#             alpha=0.3,
#             color='red',
#             linestyle=':',
#             )

#         # above
#         self.dev_warn_above = self.ax2.fill_between(
#             rs_fc.index,
#             rs_fc['yhat_upper'],
#             rs_m.values,
#             where=rs_m.values > rs_fc['yhat_upper'],
#             interpolate=True,
#             alpha=0.3,
#             color='red',
#             linestyle=':',
#             )

#         try:
#             self.fc_line.set_data(rs_fc.index, rs_fc['yhat'])
#         except AttributeError:
#             (self.fc_line, ) = self.ax2.plot(
#                 rs_fc.index,
#                 rs_fc['yhat'],
#                 c='black',
#                 ls='dashed',
#                 lw=0.7,
#                 alpha=0.4,
#                 )
#             self.artists.append(self.fc_line)

#            # update legend
#             self.ax2.get_legend().remove()
#             self.ax2.legend([self.ac_line, self.m_line, (self.fc_line,
#                             self.ci), (self.dev_warn_above,
#                             self.dev_warn_below)], ['Live System',
#                             'System Model', 'Forecast \u00B1 CI',
#                             'Model-Forecast Deviation'])
