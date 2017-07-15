# -*- coding: utf-8 -*-
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pylab as plt
import matplotlib.animation as animation
import time
import logging
log = logging.getLogger(__name__)

class AnimatedPlot():
    """An animated plot of mosyco.

    Only init after system data is available in inspector or else
    """
    def __init__(self, inspector, system, actual_value_gen):
        self.inspector = inspector
        self.system = system

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()
        # Then setup FuncAnimation.
        self.ani = animation.FuncAnimation(self.fig, self.update,
                                            frames=actual_value_gen,
                                            init_func=self.setup_plot,
                                            interval=200, blit=False)

    def setup_plot(self):
        """Set up the initial state of the plot."""
        # x, y, s, c = next(self.stream)
        # actual_data = self.inspector.df[self.system]
        # self.actual_line = self.ax.plot(actual_data)[0]
        # self.ax.axis('tight')

        # For FuncAnimation's sake, we need to return the artist we'll be using
        # Note that it expects a sequence of artists, thus the trailing comma.
        # return self.actual_line,
        datemin = self.inspector.df.index.min()
        datemax = self.inspector.df.index.max()
        self.ax.set_xlim(datemin, datemax)
        self.fig.autofmt_xdate()
        return [self.ax]


    def update(self, i):
        """Update the plot."""
        # need to make sure that new data has come in:
        # TODO: how better? asyncio
        # TODO: try catch block for KeyError during first call
        try:
            actual_data = self.inspector.df[self.system]
            if not hasattr(self, 'actual_line'):
                self.actual_line = self.ax.plot(actual_data)[0]
            else:
                self.actual_line.set_xdata(actual_data[0])
                self.actual_line.set_ydata(actual_data[1])
                # self.actual_line.set_data(actual_data.values)
        except KeyError as e:
            log.info(f"No {self.system} data available for plotting yet")
            # dummy line
            # return self.ax.plot([0, 0])
            raise

        plt.pause(0.0001)
        return self.actual_line,

        # is this enough? or set axis and move window?

        # # Set x and y data...
        # self.scat.set_offsets(data[:2, :])
        # # Set sizes...
        # self.scat._sizes = 300 * abs(data[2])**1.5 + 100
        # # Set colors..
        # self.scat.set_array(data[3])

    def show(self):
        plt.show()
