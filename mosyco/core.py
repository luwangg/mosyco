# -*- coding: utf-8 -*-
import logging

import pandas as pd
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pylab as plt
import matplotlib.animation as animation
import numpy as np

from collections import deque

def get_data():
    a = np.arange(1000)
    for i in len(a) - window_length:
        yield a[i:i + window_length]

def update(n, *args):
    '''Callback function called each frame for the animation. '''
    # extract artist objects
    ax, line, prediction_line, xdata = args

    xdata.append(n + 1)

    line.set_xdata(xdata)
    line.set_ydata(np.sin(xdata))
    ax.relim()
    ax.autoscale_view(scaley=False)
    if n + fc_frame >= window_length:
        ax.set_xlim(n - window_length + fc_frame + 1, n + fc_frame + 1)
    else:
        # makes it look ok when the animation loops
        ax.set_xlim(0, window_length)

    # create forecast period
    forecast_period = np.arange(xdata[-1], xdata[-1] + fc_frame)
    # need to actually predict here perhaps using fbprophet?!
    prediction = np.sin(forecast_period)

    # need better way to determine error
    sigma = prediction.std(axis=0)

    # adds more uncertainty for predictions farther in the future
    future_factor = np.arange(
        1, len(forecast_period) + 1) / (len(forecast_period) + 1)

    upper_error_bound = prediction + sigma * future_factor
    lower_error_bound = prediction - sigma * future_factor

    # delete previous prediction drawings
    for coll in ax.collections:
        ax.collections.remove(coll)

    prediction_line.set_xdata(forecast_period)
    prediction_line.set_ydata(prediction)

    uncertainty = ax.fill_between(forecast_period,
                                  lower_error_bound,
                                  upper_error_bound,
                                  alpha=0.1,
                                  color='orange',)

    # should return one line for historic data and another for projection
    # only really necessary for blitting
    return [line, prediction_line, uncertainty]


if __name__ == '__main__':
    # setup figure
    fig, ax = plt.subplots()
    # set up viewing window (in this case the 25 most recent values)
    # should be length of deque + forecast frame
    window_length = 10
    fc_frame = 3
    ax.set_xlim([0, window_length])
    ax.set_ylim([-1.2, 1.2])

    line, = ax.plot([], [], color=(0, 0, 1))
    prediction_line, = ax.plot([], [], '--b')

    # maxlen = window_length - fc_period ?!
    xdata = deque([0], maxlen=7)

    # must keep reference to ani, else it will be garbage collected
    ani = animation.FuncAnimation(fig, update, frames=None, fargs=[
                                  ax, line, prediction_line, xdata], interval=1000, blit=True)

    plt.show()

    # plt.ion()
