# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import logging
import time

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
        args (Namespace): command line arguments
        df (DataFrame): holds model data and is filled with actual values.
        model_map (dict): mapping of systems to models.
        forecast (DataFrame): is filled with forecasts in regular intervals.
        plotting_queue (Queue): Queue for plotter-inspector communication.
        reader_queue (Queue): Queue for reader-inspector communication.
        threshold (float): percentage threshold for actual-model deviations.
    """
    def __init__(self, index, model_columns, args, reader_queue, plotting_queue):
        """Create a new Inspector.

        The index should be the reader's index. This means that the reader and
        inspector dataframes will share the same index object.

        Args:
            index (Index or DateTimeIndex): of the corresponding reader's dataframe.
            model_columns (Series): list of model data columns, passed from reader in batch.
        """
        self.args = args
        self.model_map = dict(zip(self.args.systems, self.args.models))

        self.df = pd.DataFrame(data=model_columns.copy(), index=index)
        for s in self.args.systems:
            self.df[s] = np.nan

        self.reader_queue = reader_queue
        self.plotting_queue = plotting_queue

        # add 'ds' (Date) column for fbprohet
        self.df['ds'] = self.df.index

        # add a forecast dataframe with same index as main dataframe
        self.forecast = pd.DataFrame(index=index)

        self.threshold = self.args.threshold
        # \u00B1 is unicode for hte plus-minus character
        log.debug(f"Using threshold: \u00B1{self.threshold:.1%}")

    def start(self):
        """Start the Inspector."""
        # silence suppresses stdout (to deal with pystan bug)
        log.info("Starting Inspector...")
        # with helpers.silence():
        for row in self.receive():
            # sanity check
            assert len(self.args.systems) == len(row) - 1

            # get date
            date = row['Index']

            # evaluate system vs model for each system
            for system_name, val in row.items():
                if system_name is not 'Index':
                    self.eval_actual(date, system_name)

            # at the end of each period, create a forecast for the following
            if date.month == 12 and date.day == 31:
                # create a period for the following year
                period = pd.Period(date.year + 1)

                # stop at this date
                if date.year == 2005:
                    break

                # generate a forecasts for each system and evaluate it
                # against the model data
                for system in self.args.systems:
                    log.debug(f'Generating {system} forecast for {period}...')
                    self.forecast_period(period, system)
                    log.debug(f'{system} forecast was generated for {period}.')
                    log.debug(f'Evaluating {system} forecast for {period}...')
                    self.eval_future(period, system)

            # if in GUI-Mode, push forecast to plotter
            if self.args.gui:
                self.plotting_queue.put(row)

        log.info("The Inspector has finished!")


    def receive(self):
        """Receive data from the Reader.

        While the Reader pushes new data rows to the reader_queue in a loop,
        the Inspector receives this data and yields it row by row to the
        Inspector's start method for evaluation.
        """
        while True:
            try:
                new_row = self.reader_queue.get(block=True)

                # Signal that reader has finished pushing data
                if new_row is None:
                    log.debug('The queue is empty. Shutting down Inspector...')
                    return

                # prevent pandas error "setting an array element with a sequence"
                if len(new_row) == 2:
                    self.df.loc[new_row.Index, self.args.systems] = new_row[1:][0]
                else:
                    self.df.loc[new_row.Index, self.args.systems] = new_row[1:]

                yield new_row._asdict()

            except Exception as e:
                log.debug('Exception in mosyco.inspector.receive: {}'.format(e))
                time.sleep(0.05)
                continue



    def eval_actual(self, date, system):
        """Evaluate the deviation between model- and actual data for a given date.

        A log output will be sent for every deviation that this method detects.

        Args:
            date (TimeStamp): Date for which to evaluate.
            system (str): Name of the actual system.
        """

        # assertion will fail if the values are not available yet
        assert system in self.df.columns

        # get the values
        actual = self.df.loc[date, system]
        model = self.df.loc[date, self.model_map[system]]

        # sanity check
        assert not pd.isnull(actual)
        assert not pd.isnull(model)

        # calculate the deviation
        # rs = methods.relative_deviation(model, actual, self.threshold)
        (exceeds_threshold, rel_dev) = methods.relative_deviation(model, actual, self.threshold)
        abs_dev = methods.absolute_deviation(model, actual, self.threshold)




        # if exceeds_threshold:
        #     log.debug(f'Model-Actual deviation for '
        #             f'system: {system} '
        #             f'on {date.date()} '
        #             f'by {deviation}.')

        log.debug(f'on {date.date()} - '
                f'{system}: '
                f'{exceeds_threshold} '
                f'IST: {round(actual, 2)} '
                f'SOLL: {round(model, 2)} '
                f'ABS DEV: {round(abs_dev, 2)} '
                f'REL DEV: {rel_dev:.2%}.')

    def eval_future(self, period, system):
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
        # this will raise an exception if we haven't forecast the required period yet
        try:
            data = pd.concat(
                [
                self.df.loc[period.start_time:period.end_time],
                self.forecast.loc[period.start_time:period.end_time]
                ],
                axis=1)
        except KeyError as e:
            raise KeyError(f"Forecasting data for {period} not available.")

        model_data = data.loc[:, self.model_map[system]]
        yhat_lower = data.loc[:, 'yhat_lower']
        yhat_upper = data.loc[:, 'yhat_upper']

        forecast_data = data.loc[:, 'yhat']
        deviations = (model_data - forecast_data) / forecast_data

        # find out where model data falls outside forecast CI
        outside = model_data.where(
            (model_data < yhat_lower) | (model_data > yhat_upper))


        outside_deviations = deviations.loc[outside.index]

        if self.args.loglevel == logging.DEBUG:
            for date, deviation in outside_deviations.iteritems():
                # log.debug(f'Model-Forecast deviation for '
                #         f'model: {self.model_map[system]} '
                #         f'on {date.date()} '
                #         f'by {deviation:.2%}.')
                pass


        f_fit = 1.0 - (outside.count() / outside.size)
        log.debug(f'Finished evaluating {system} forecast: '
            f'Model-Forecast fit: {f_fit:.2%}')

        # plot the forecast if in GUI-Mode
        if self.args.gui:
            fc = data[['yhat', 'yhat_upper', 'yhat_lower']].resample('W').mean()
            self.plotting_queue.put(fc)


    def forecast_period(self, period, actual_system):
        """Update forecast dataframe attribute with forecast for the given period.

        A period can be any pandas period object or period-like string.
        For example, pd.Period('2011') & '2012-11' are valid periods.

        The forecasting is done with
        `fbprophet <https://github.com/facebookincubator/prophet/tree/master/python>`_
        on the bases already received actual data.

        Prophet works best with at least one year of historical data, so the default
        is to wait until enough data is available and then periodcally update the
        prediction when enough new data has arrived. This also means that in
        certain circumstances, the first forecast may not be very accurate.

        A good introduction to how fbprophet works can be found in their blog post
        `here <https://research.fb.com/prophet-forecasting-at-scale/>`_. Further
        reading can be found in the \
        `paper <https://facebookincubator.github.io/prophet/static/prophet_paper_20170113.pdf>`_

        The fitting is computationally intensive and should therefore not be done
        too frequently or else the overall performance of the application will suffer.

        Procedure:
            1. Create an empty dataframe for the required period
            2. Call the prophet model's predict() function on this dataframe
            3. Merge the prediction output into the forecast dataframe

        """
        # EXPENSIVE - CAN TAKE VERY LONG
        fc_model = self._fit_model(actual_system)

        # double check / assert here that period is in df
        assert 'ds' in self.df.columns
        fc_frame = self.df.loc[period.start_time:period.end_time, ['ds']]

        # EXPENSIVE - CAN TAKE VERY LONG
        new_forecast = fc_model.predict(fc_frame)

        # new_forecast needs to have DateTimeIndex
        new_forecast.set_index('ds', inplace=True)

        # merge it into forecast dataframe
        self.forecast = self.forecast.combine_first(new_forecast)

    def _fit_model(self, system):
        """Fit and return a new forecasting model.

        This is also an expensive operation. It creates a new Prophet object each
        time this function is called. The fitting can take up to 5 seconds on
        occasion but should generally be quite fast, thanks to
        `PyStan <https://pystan.readthedocs.io/en/latest/>`_.

        This is the bottleneck that restricts the real-time capability of this
        prototype. This implementation is not suitable for use cases
        that require new forecasts every few seconds or so. However, it does work
        very well for frequencies of once per minute or less.
        """
        # We need to set 'y' column again each time because the actual value
        # column receives new values in the meantime.
        try:
            self.df['y'] = self.df[system]
        except AttributeError as e:
            raise AttributeError("inspector does not have actual {system} data \
                                    for forecast yet.")

        # No custom settings for model --> forecast is just for illustration
        return Prophet().fit(self.df[['ds', 'y']])
