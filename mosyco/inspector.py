# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import logging

from fbprophet import Prophet

import mosyco.methods as methods
import mosyco.helpers as helpers

log = logging.getLogger(__name__)


class Inspector:
    """The Inspector analyses the data pushed by the reader.

    The Inspector evaluates deviations between:
        * Model data and actually observed values
        * Model data and forecast values

    The Inspector's job is to detect significant deviations or potential deviations
    in this data that might warrant an adjusment to the model parameters or
    hyperparameters. In other words, the intended purpose of this program is to
    warn users of a model as early as possible if the model might require tweaking.

    The Inspector does not suggest how such a model might be altered in response
    to the deviations, but merely that it may be necessary.

    Attributes:
        df (DataFrame): holds model data and is filled with actual values.
        model_name (str): name of the model.
        forecast (DataFrame): is filled with forecasts in regular intervals.
        threshold (float): percentage threshold for actual-model deviations.
    """
    def __init__(self, index, model_column):
        """Create a new Inspector.

        The index should be the reader's index. This means that the reader and
        inspector dataframes will share the same index object.

        Args:
            index (Index or DateTimeIndex): of the corresponding reader's dataframe.
            model_column (Series): model data column, passed from reader in batch.
        """
        self.model_name = model_column.name
        self.df = pd.DataFrame(data=model_column.copy(), index=index)

        # add 'ds' (Date) column for fbprohet
        self.df['ds'] = self.df.index

        # add a forecast dataframe with same index as main dataframe
        self.forecast = pd.DataFrame(index=index)

        # TODO: figure out where to get THRESHOLD from
        self.threshold = 0.2
        # \u00B1 is unicode for hte plus-minus character
        log.info(f"Using threshold: \u00B1{self.threshold:.2%}")

    def receive_actual_value(self, val, system):
        """Fills inspector dataframe with actual values from a running system.
        Args:
            val (tuple): of (index, value) where index is a DateTime object
            system (str): name of the active system (e.g. 'PAcombi')
        """
        self.df.set_value(val[0], system, val[1])

    def eval_actual(self, date, system):
        """Evaluate the deviation between model- and actual data for given date.
        Return the deviation if it exceeds a threshold or False if not.

        Args:
            date (TimeStamp): Date for which to evaluate.
            system (str): Name of the actual system.
        """
        # assertion will fail if the values are not available yet
        assert system in self.df.columns

        # get the values
        actual = self.df.loc[date, system]
        model = self.df.loc[date, self.model_name]

        # sanity check
        assert not pd.isnull(actual)
        assert not pd.isnull(model)

        # calculate the deviation
        result = methods.relative_deviation(model, actual, self.threshold)
        (exceeds_threshold, deviation) = result

        if exceeds_threshold:
            log.debug(f'Model-actual deviation on {date} by {deviation}')

        return result

    def eval_future(self, period):
        """Evaluate the deviation between Model and Forecast data for a period.

        Outputs the first date of any deviation in the logs and returns a
        DatetimeIndex object with all the dates where deviations occurred.
        Return None if no deviations were found.

        The forecast with fbprophet returns a 95% confidence (yhat_lower, yhat_upper)
        interval along with the forecast (yhat). This information is used to identify
        potential future errors in the model. It is important to stress that these
        are *potential* deviations, as model data may be more
        accurate than the forecast in certain cases.

        This function takes the following steps:
            1. Determine if forecast data is available for the required period
            2. Access forecast and model columns from the dataframes
            3. Create a mask column where the model data falls within the confidence interval
            4. Output the dates / periods (if any) where this is the case

        Args:
            period (Period): Period for which to evaluate forecast vs model.
        """

        # ======================================================================
        # TODO:
        # Output format? First date of deviation, period of consecutive deviations?
        # Probability of confidence interval is 95%. How to interpret this?
        # Make sure all available data is used for new forecasts
        # ======================================================================

        # variable data has model and relevant forecasting data for period
        # this will raise an exception if  we haven't forecast the required period yet
        try:
            data = pd.concat(
                [self.df.loc[str(period)], self.forecast.loc[str(period)]],
                axis=1)
        except KeyError as e:
            raise KeyError(f"Forecasting data for {period} not available.")

        model_data = data.loc[:, self.model_name]
        yhat_lower = data.loc[:, 'yhat_lower']
        yhat_upper = data.loc[:, 'yhat_upper']

        # TODO: rename eval...
        data['eval'] = model_data.where(
            (yhat_lower <= model_data) & (model_data <= yhat_upper)
        )

        # the above column now contains values where model data fell within the
        # prediction confidence interval and NaNs otherwise

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
        log.info(f'Potential forecast-model deviation from {first_date.date()}')

        f_fit = result.count() / result.size
        log.info(f'Model-forecast fit: {f_fit:.1%}')

        return result
        # TODO: plot this too?




    # TODO: remove hard-coded column ref. (PAcombi)
    def _fit_model(self, system):
        """Fit the model.

        This is a very expensive operation. It creates a new Prophet object each
        time this function is called. The fitting can take up to 5 seconds on
        occasion but should generally be quite fast, thanks to
        `PyStan <https://pystan.readthedocs.io/en/latest/>`_.

        This is the bottleneck that restricts the real-time capability of this
        program. This implementation is therefore not suitable for use cases
        that require new forecasts every few seconds or so. However, it works very
        well for frequencies of once per minute or lower.
        """
        # We need to set 'y' column again each time because the actual value
        # column receives new values in the meantime.
        # TODO: maybe just call actual data y in dataframe (refactor)
        # But then --> Problem with multiple variables
        try:
            self.df['y'] = self.df[system]
        except AttributeError as e:
            raise AttributeError("inspector does not have actual {system} data \
                                    for forecast yet.")

        # No custom settings for model, b/c we are predicting what we already
        # know anyways
        with helpers.silence():
            self.forecasting_model = Prophet().fit(self.df)



    def forecast_year(self, period, actual_system):
        """Update forecast dataframe attribute with forecast for the given period.

        A period can be any pandas period object or period-like string.
        For example, pd.Period('2011') & '2012-11' are valid periods.

        The forecasting is done with
        `fbprophet <https://github.com/facebookincubator/prophet/tree/master/python>`_
        on the bases already received actual data.

        Prophet works best with at least one year of historical data, so the default
        is to wait until enough data is available and then periodcally update the
        prediction when enough new data has arrived.

        A good introduction to how fbprophet works can be found in their blog post
        `here <https://research.fb.com/prophet-forecasting-at-scale/>`_. Further
        reading can be found in the \
        `paper <https://facebookincubator.github.io/prophet/static/prophet_paper_20170113.pdf>

        The fitting takes a bit of time so it should not be done too frequently
        or else the overall performance of the application will suffer.

        Procedure:
            1. Create an empty dataframe for the required period
            2. Call the prophet model's predict() function on this dataframe
            3. Merge the prediction output into the forecast dataframe

        """
        # TODO: allow to set period to use for forecast.

        # EXPENSIVE - CAN TAKE VERY LONG
        self._fit_model(actual_system)

        # TODO: entries for period MUST be empty, else this will raise an exception?!
        # double check / assert here that period is in df
        assert 'ds' in self.df.columns
        fc_frame = self.df.loc[str(period)].filter(['ds'])

        # EXPENSIVE - CAN TAKE VERY LONG
        with helpers.silence():
            new_forecast = self.forecasting_model.predict(fc_frame)
        del fc_frame

        # new_forecast needs to have DateTimeIndex
        new_forecast.set_index('ds', inplace=True)

        # merge it into forecast dataframe
        self.forecast = self.forecast.combine_first(new_forecast)
