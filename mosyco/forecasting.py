# -*- coding: utf-8 -*-
import pandas as pd
from fbprophet import Prophet

from mosyco.helpers import load_dataframe

df = load_dataframe()
print(df.head())
model = Prophet()
df['ds'] = df.index
df['y'] = df['PAcombi']

model.fit(df)

future = model.make_future_dataframe(periods=365)
print(future.tail())

forecast = model.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

model.plot(forecast)
model.plot_components(forecast)
