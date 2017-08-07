from mosyco.inspector import Inspector
from mosyco.reader import Reader

from random import random

from bokeh.layouts import column
from bokeh.models import Button, ColumnDataSource
from bokeh.palettes import RdYlBu3
from bokeh.plotting import figure, curdoc


class Nub():
    def __init__(self):
        self.reader = Reader('PAseasonal')
        self.inspector = Inspector(self.reader.df.index, self.reader.df['PAmodel'])

    def run(self):
        for (date, value) in self.reader.actual_value_gen():
            self.inspector.receive_actual_value((date, value), self.reader.current_system)
            update_plot()


def update_plot():
    pass

nub = Nub()

source = ColumnDataSource(nub.inspector.df[['PAseasonal', 'PAmodel']])

# create a plot and style its properties
plot = figure(title="Model-System-Controller Architecture Prototype",
              x_axis_label="Date",
              x_axis_type='datetime',)

i = 0

# call callback every iteration of main for loop (run method)
# in callback set the updated dataframe as the new_data (maybe as a dict)


# create a callback that will add a number in a random location
def callback():
    global i

    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    new_data['x'] = ds.data['x'] + [random()*70 + 15]
    new_data['y'] = ds.data['y'] + [random()*70 + 15]
    new_data['text_color'] = ds.data['text_color'] + [RdYlBu3[i%3]]
    new_data['text'] = ds.data['text'] + [str(i)]
    ds.data = new_data

    i = i + 1

# add a button widget and configure with the call back
button = Button(label="Press Me")
button.on_click(callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(button, p))
