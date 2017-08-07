import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
import time

# set up the dataframe
index = pd.DatetimeIndex(freq='D', start='2015-01-01', periods=100)
df = pd.DataFrame(index=index)

# add the column to be filled
df['y'] = np.nan
# add another column with reference values
df['z'] = 50

# setup the plot
fig, ax = plt.subplots()
line, = ax.plot(df.index, [50 for i in range(len(df))])
ax.set_ylim(0, 100)

def update_plot(i):
    line.set_ydata(df['y'])
    return line,

def run():
    # this loop should be animated
    for (i, (idx, _)) in enumerate(df.iterrows()):

        # random sample to simulate data new "arriving"
        df.loc[idx, 'y'] = np.random.randint(0, 100)

        # log some error here
        # error = abs(df.loc[idx, 'y'] - df.loc[idx, 'z'])
        # print(error)

        if i % 10 == 0:
            # some blocking computation on the dataframe happens here
            # this may actually take up to 4 seconds
            time.sleep(0.1)
        yield i

# run the animation
ani = animation.FuncAnimation(fig, update_plot, frames=run,
                              interval=100, blit=True, repeat=False)
plt.show()
