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
for (i, (idx, _)) in enumerate(df.iterrows()):
    # random sample to simulate data new "arriving"
    df.loc[idx, 'y'] = np.random.randint(0, 100)

# add another column with reference values
df['z'] = 50

# setup the plot
fig, (ax1, ax2) = plt.subplots(2)

fig.tight_layout(rect=[0, 0.03, 1, 0.95])

fig.suptitle("Model-/System-Controller Architecture Prototype")

ax1.set_title('Live System View')
ax2.set_title('Forecast Detail View')
# ax3.set_title('Static Model View')

ax1.set_ylabel('Units')
ax2.set_ylabel('Units')

# by the way: how do I initialize the line properly?
l1, = ax1.plot(df.y)
l2, = ax2.plot(df.z)
ax1.set_ylim(0, 100)
ax2.set_ylim(30, 60)
fig.autofmt_xdate()

def update_plot(i):
    l1.set_ydata(df['y'])
    l2.set_ydata(df['z'])
    ax1.autoscale_view(scaley=False)
    return l1, l2


def run():
    # give plot time to get ready
    time.sleep(0.5)
    # this loop should be animated
    for (i, (idx, _)) in enumerate(df.iterrows()):
        # random sample to simulate data new "arriving"
        df.loc[idx, 'y'] = np.random.randint(0, 100)
        df['z'] = np.random.randint(40, 60)
        # print(abs(df.loc[idx, 'y'] - df.loc[idx, 'z']))

        if i % 10 == 0:
            # some blocking computation on the dataframe happens here
            # this may actually take up to 4 seconds
            time.sleep(0.5)
        time.sleep(0.1)

ani = animation.FuncAnimation(fig, update_plot, frames=None,
                              interval=100, blit=True, repeat=False)
t1 = threading.Thread(target=run)
t1.start()
plt.show()
# run()
