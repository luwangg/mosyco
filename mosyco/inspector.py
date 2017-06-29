# -*- coding: utf-8 -*-
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

    def receive_actual_value(self, val, system='PAcombi'):
        """Fills inspector dataframe with actual values."""
        # val is a tuple of (index, value)
        self.df.set_value(val[0], system, val[1])

    def evaluate(self, date):
        """Evaluate the deviation between Model and Actual for given date.
        Return the deviation if it exceeds a threshold or False if not."""
        # TODO: THRESHOLD, rm hardcoded variables
        # col is the name of the column we want
        actual_column = 'PAcombi'
        model_column = 'PAmodel'

        actual = self.df.loc[date, actual_column]
        model = self.df.loc[date, model_column]

        threshold = 0.2

        return methods.relative_deviation(model, actual, threshold)

    def _fit_model(self):
        """Fit the model. This is a very expensive operation. Creates a new
        Prophet object each time this function is called. The fitting can take
        up to 5 seconds on occasion.
        """
        # We need to set 'y' column again each time because the actual value
        # column receives new values in the meantime.
        # TODO: maybe just call actual data y in dataframe (refactor)
        # --> Problem with multiple variables
        # TODO: remove hard-coded column reference
        try:
            self.df['y'] = self.df['PAcombi']
        except AttributeError:
            log.error("inspector does not have actual data for the forecast yet.")
            raise

        # No custom settings for model, b/c we are predicting what we already
        # know anyways
        self.forecasting_model = Prophet().fit(self.df)



    def forecast_year(self, year):
        """Return a future dataframe object with forecast for the given year.

        The forecasting is done with fbprophet on the bases of the previous year.
        Prophet works best with at least one year of historical data, so the default
        is to wait until enough data is available and then periodcally update the
        prediction when enough new data has arrived.

        [https://github.com/facebookincubator/prophet/tree/master/python]

        The fitting takes a bit of time so it should not be done too frequently
        or else the overall performance of the application will suffer.
        """
        # TODO: allow to set period to use for forecast.

        # 1. make a dataframe for the following year
        # 2. call predict on this dataframe
        # 3. merge the values of this dataframe into the main df
        #
        # TODO: Will the prediciton be in the main dataframe already? or do we need to concatenate later

        # TODO: call this here or in main?
        # EXPENSIVE - CAN TAKE VERY LONG
        self._fit_model()

        # TODO: entries for year MUST be empty, else this will raise an exception?!
        # double check / assert here that year is in df
        fc_frame = self.df.loc[str(year)].copy()
        # returns new dataframe

        # EXPENSIVE - CAN TAKE VERY LONG
        new_forecast = self.forecasting_model.predict(fc_frame)
        # needs to be merged into existing one




        # future = self.forecasting_model.predict()



if __name__ == '__main__':
    pass
