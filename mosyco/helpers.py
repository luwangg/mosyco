# -*- coding: utf-8 -*-
"""This module contains various helper functions"""

import pandas as pd
from os import path

def load_dataframe():
    # TODO: proper naming conventions for columns
    df = pd.read_csv(path.join(path.dirname(__file__), '../data/produktA-data.csv'),
                                    index_col=1, parse_dates=True,
                                    infer_datetime_format=True)
    df = df.drop(['Unnamed: 0'], axis=1)
    return df


if __name__ == '__main__':
    df = load_dataframe()
