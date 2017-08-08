import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import time
import threading

plt.style.use('seaborn')

# set up the dataframe
index = pd.DatetimeIndex(freq='D', start='2015-01-01', periods=100)
df = pd.DataFrame(index=index)

# add the column to be filled
df['y'] = np.nan
# add another column with reference values
df['z'] = 50

# setup the plot
fig, ax = plt.subplots()

# by the way: how do I initialize the line properly?
line, = ax.plot(df.index, [0 for i in range(len(df))])
ax.set_ylim(0, 100)
fig.autofmt_xdate()

def update_plot(i):
    line.set_ydata(df['y'])
    ax.autoscale_view(scaley=False)
    return line,


def run():
    # give plot time to get ready
    time.sleep(0.5)
    # this loop should be animated
    for (i, (idx, _)) in enumerate(df.iterrows()):
        # random sample to simulate data new "arriving"
        df.loc[idx, 'y'] = np.random.randint(0, 100)

        # print(abs(df.loc[idx, 'y'] - df.loc[idx, 'z']))

        if i % 10 == 0:
            # some blocking computation on the dataframe happens here
            # this may actually take up to 4 seconds
            time.sleep(1)
        time.sleep(0.1)

ani = animation.FuncAnimation(fig, update_plot, frames=None,
                              interval=100, blit=True, repeat=False)
t1 = threading.Thread(target=run)
t1.start()
plt.show()
# run()
