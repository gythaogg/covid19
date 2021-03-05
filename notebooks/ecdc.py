import logging
from functools import cached_property
from json import dumps, loads

import pandas as pd
import requests

from helper import *


class ECDC:
    @cached_property
    def df(self):
        #
        response = requests.get(
            'https://opendata.ecdc.europa.eu/covid19/testing/json/')
        _df = pd.read_json(dumps(response.json()['records']))
        _df['dateRep'] = pd.to_datetime(_df['dateRep'].astype(str),
                                        format='%d/%m/%Y')
        _df['notification_rate_per_100000_population_14-days'] = pd.to_numeric(
            _df['notification_rate_per_100000_population_14-days'].fillna(0))
        return _df
