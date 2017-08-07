from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure

import numpy as np

source = ColumnDataSource(data={
    'x': [],
    'y': [],
    'avg': [],
    })

plot = figure(title="Model-System-Controller Architecture Prototype",
              x_axis_label="Date",
              x_axis_type='datetime',)

plot.line(source=source, x='x', y='y')
plot.line(source=source, x='x', y='avg')

ct = 0
sine_sum = 0

def update_data():
    global ct, sine_sum
    ct += 1
    sine = np.sin(ct)
    sine_sum += sine
    new_data = dict(x=[ct], y=[sine], avg=[sine_sum/ct])
    source.stream(new_data, 100)

curdoc().add_root(plot)
curdoc().add_periodic_callback(update_data, 100)
