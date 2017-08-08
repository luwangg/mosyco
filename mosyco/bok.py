import numpy as np
import pandas as pd

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show, output_file
import time
import threading

from tornado import gen

# set up the dataframe
index = pd.DatetimeIndex(freq='D', start='2015-01-01', periods=100)
df = pd.DataFrame(index=index)

# important
doc = curdoc()

# add the column to be filled
df['y'] = np.nan
# add another column with reference values
df['z'] = 50

source = ColumnDataSource(df)

plot = figure(title='Model-System-Controller Architecture Prototype',
              # plot_height=400,
              # plot_width=600,
              x_axis_label='Date',
              x_axis_type='datetime',
              y_axis_label='Units')


line = plot.line(x='index', y='y', source=source)

@gen.coroutine
def update_line():
    source.data['y'] = df['y']
    # source.stream()


def run():
    for (i, (idx, _)) in enumerate(df.iterrows()):
        # random sample to simulate data new "arriving"
        df.loc[idx, 'y'] = np.random.randint(0, 100)
        print(df.loc[idx, 'y'])
        # update_line()
        doc.add_next_tick_callback(update_line)
        time.sleep(0.2)

doc.add_root(plot)

t1 = threading.Thread(target=run)
t1.start()
