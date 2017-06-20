# -*- coding: utf-8 -*-
import pandas as pd
from fbprophet import Prophet


df = pd.read_csv('../data/produktA-data.csv')
df = df.drop(['Unnamed: 0'], axis=1)
print(df.head())
model = Prophet()
df['ds'] = df['Date']
df['y'] = df['PAcombi']

model.fit(df)

future = model.make_future_dataframe(periods=365)
print(future.tail())

forecast = model.predict(future)
print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())

model.plot(forecast)
model.plot_components(forecast)
