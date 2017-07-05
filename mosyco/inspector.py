# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import logging

from fbprophet import Prophet

import mosyco.methods as methods

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class Inspector:
    def __init__(self, index, column):
        # The index should be the reader's index. This means that the reader and
        # inspector dataframes will share the same index object.
        # columns should be the model data that is passed in batch.
        self.df = pd.DataFrame(data=column.copy(), index=index)
        # add 'ds' column for fbprohet
        self.df['ds'] = self.df.index

        # TODO: better way to integrate forecasts without polluting df
        self.forecast = pd.DataFrame(index=index)

    def receive_actual_value(self, val, system='PAcombi'):
        """Fills inspector dataframe with actual values."""
        # val is a tuple of (index, value)
        self.df.set_value(val[0], system, val[1])

    def eval_actual(self, date):
        """Evaluate the deviation between Model and Actual for given date.
        Return the deviation if it exceeds a threshold or False if not.

        The model is evaluated based on the actual values.

        date should be a TimeStamp object.
        """
        # TODO: THRESHOLD, rm hardcoded variables
        # TODO: maybe return tuple: (False/True, deviation)
        # col is the name of the column we want
        actual_column = 'PAcombi'
        model_column = 'PAmodel'

        actual = self.df.loc[date, actual_column]
        model = self.df.loc[date, model_column]

        threshold = 0.2

        result = methods.relative_deviation(model, actual, threshold)
        (exceeds_threshold, deviation) = result

        if exceeds_threshold:
            log.debug(f'Model-actual deviation on {date} by {deviation}')

        return result

    def eval_future(self, period):
        """Evaluate the deviation between Model and Forecast data for a period.
        Output the first date of any deviation in the logs and return a
        DatetimeIndex object with all the dates where deviations occurred.
        Return None if no deviations were found.

        The forecast with fbprophet returns a 95% confidence (yhat_lower, yhat_upper)
        interval along with the forecast (yhat). This information is used to identify
        potential future errors in the model. It is important to stress that these
        are *potential* deviations, as model data may be more
        accurate than the forecast in certain cases.
        """

        # 1. Determine if forecast data is available for the required period
        # 2. Access forecast and model columns from df
        # 3. Loop over pairs and check if model data is within confidence intervals
        # 4. Output the dates / periods (if any) where this is the case

        # Heuristic when to stop?
        # Only one deviation enough? Or several consecutive ones?!
        # Find out Probability of confidence interval

        # "Based on the actual data, the forecast suggests with  XX% confidence,
        # that the model data will be wrong for periods: ..."

        # variable data has model and relevant forecasting data for period
        # this will raise an exception if  we haven't forecast the required period yet
        try:
            data = pd.concat([self.df.loc[str(period)], self.forecast.loc[str(period)]], axis=1)
        except KeyError as e:
            raise KeyError(f"Forecasting data for {period} not available.")

        model_data = data.loc[:, 'PAmodel']
        yhat_lower = data.loc[:, 'yhat_lower']
        yhat_upper = data.loc[:, 'yhat_upper']

        # TODO: rename eval...
        #
        data['eval'] = model_data.where(
            (yhat_lower <= model_data) & (model_data <= yhat_upper)
        )
        # above column now contains values where model data fell within the
        # prediction confidence interval

        # get a copy of the column to return later
        result = data.loc[:, 'eval'].copy()

        # keep only rows were the model falls outside the confidence interval
        model_errors = result[np.isnan(result)]
        # check if any deviations
        if model_errors.empty:
            log.info(f'No forecast-model deviations found during {period}')
            return None

        # get first day when the model is not within forecast bounds
        first_date = model_errors.index[0]

        # TODO: need to determine how best to output this
        log.info(f'Potential forecast-model deviation from {first_date}')

        f_fit = result.count() / result.size
        log.info(f'Model-forecast fit: {f_fit:.1%}')

        return result
        # TODO: plot this too?




    # TODO: remove hard-coded column ref. (PAcombi)
    def _fit_model(self, system='PAcombi'):
        """Fit the model. This is a very expensive operation. Creates a new
        Prophet object each time this function is called. The fitting can take
        up to 5 seconds on occasion.
        """
        # We need to set 'y' column again each time because the actual value
        # column receives new values in the meantime.
        # TODO: maybe just call actual data y in dataframe (refactor)
        # --> Problem with multiple variables
        try:
            self.df['y'] = self.df[system]
        except AttributeError as e:
            log.error("inspector does not have actual data for the forecast yet.")
            raise AttributeError("inspector does not have actual {system} data for forecast yet.")

        # No custom settings for model, b/c we are predicting what we already
        # know anyways
        self.forecasting_model = Prophet().fit(self.df)



    def forecast_year(self, period):
        """Update forecast dataframe attribute with forecast for the given period.

        A period can be any pandas period object or period-like string.
        For example, pd.Period('2011') & '2012-11' are valid periods.

        The forecasting is done with fbprophet on the bases of the previous year.
        Prophet works best with at least one year of historical data, so the default
        is to wait until enough data is available and then periodcally update the
        prediction when enough new data has arrived.

        [https://github.com/facebookincubator/prophet/tree/master/python]

        The fitting takes a bit of time so it should not be done too frequently
        or else the overall performance of the application will suffer.
        """
        # TODO: allow to set period to use for forecast.

        # 1. make a dataframe for the following period
        # 2. call predict on this dataframe
        # 3. merge the values of this dataframe into the main df

        # TODO: Will the prediciton be in the main dataframe already? or do we need to concatenate later

        # TODO: call this here or in main?
        # EXPENSIVE - CAN TAKE VERY LONG
        self._fit_model()

        # TODO: entries for period MUST be empty, else this will raise an exception?!
        # double check / assert here that period is in df
        assert 'ds' in self.df.columns
        fc_frame = self.df.loc[str(period)].filter(['ds'])

        # EXPENSIVE - CAN TAKE VERY LONG
        new_forecast = self.forecasting_model.predict(fc_frame)
        del fc_frame

        # new_forecast needs to have DateTimeIndex!!!
        new_forecast.set_index('ds', inplace=True)
        # merge it into forecast dataframe
        self.forecast = self.forecast.combine_first(new_forecast)
