import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.ion()

df = pd.read_pickle('df')
fc = pd.read_pickle('fc')


# TODO:
# 1. second axes yes or no?
# 2. how to make edges red (segment lines?!)
# 3. Legend, Title, Labels
# 4. Save IMG

# sharex / sharey?
fig, (ax1, ax2) = plt.subplots(2)

fig.suptitle("Model-/System-Controller Architecture")

ax1.set_title('Live System View')
ax2.set_title('Forecast Detail View')

ax1.set_ylabel('Units')
ax2.set_ylabel('Units')

actual_data = df.loc['2008', 'PAseasonal']
overview = df.loc['2006':'2009', 'PAseasonal'].resample('W')
ax1.plot(overview, label='Live System Overview')
ax1.set_xlim('2006-01', '2009-12')

plt.xticks(rotation=30)
# resampled = actual_data.resample('W')

forecast_data = fc.loc['2008', 'yhat']

# plt.setp(plt.xticks()[1], rotation=30, ha='right')
# fig.autofmt_xdate()

actual_line = ax2.plot(actual_data, c='blue', label='Live System Detail')
fc_line_resampled = ax2.plot(forecast_data.resample('W'), 'k--', alpha=0.4, label='Forecast Resampled Weekly')

p = forecast_data.index
lower_error_bound = fc.loc[p, 'yhat_lower']
upper_error_bound = fc.loc[p, 'yhat_upper']
uncertainty = ax2.fill_between(p.values,
                              lower_error_bound,
                              upper_error_bound,
                              alpha=0.4,
                              color='orange',
                              linestyle=':',
                              label='Forecast Confidence Interval',)

# ax2.plot(forecast_data)
ax2.set_xlim('2008-01', '2008-12')

fig.tight_layout(rect=[0, 0.03, 1, 0.95])

# figure out bounds
# try:
#     data = pd.concat(
#         [df.loc[p], fc.loc[p]],
#         axis=1)
# except KeyError as e:
#     raise KeyError(f"Forecasting data for {period} not available.")

# model_data = data.loc[:, 'PAseasonal']
# yhat_lower = data.loc[:, 'yhat_lower']
# yhat_upper = data.loc[:, 'yhat_upper']

# data['inside'] = model_data.where(
#     (yhat_lower <= model_data) & (model_data <= yhat_upper)
# )

# data['above'] = model_data.where(model_data > yhat_upper)
# data['below'] = model_data.where(model_data < yhat_lower)

# plot bounds
# inside = ax2.plot(data['inside'], c='green')
# above = ax2.plot(data['above'], c='red')
# below = ax2.plot(data['below'], c='red')
