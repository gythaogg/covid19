from datetime import datetime
from json import dumps, loads

import numpy as np
import pandas as pd
import requests

# AUSTRIA
WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')


def ecdc():
    response = requests.get(
        'https://opendata.ecdc.europa.eu/covid19/casedistribution/json')
    json = response.json()
    df = pd.read_json(dumps(json['records']))
    df['dateRep'] = pd.to_datetime(df['dateRep'].astype(str),
                                   format='%d/%m/%Y')
    df['Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'] = pd.to_numeric(
        df['Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'].
        fillna(0))
    return df


def at():
    df = pd.read_csv(
        'https://info.gesundheitsministerium.at/data/Epikurve.csv',
        delimiter=';')
    weekday = []
    for i, row in df.iterrows():
        day_num = datetime.strptime(row['time'], '%d.%m.%Y').weekday()
        weekday.append(day_num)

    df['weekday'] = weekday
    df['time'] = pd.to_datetime(df['time'].astype(str), format='%d.%m.%Y')

    return df


def rolling_avg(x):
    return np.round(x.iloc[-7:].mean())


def latest(x):
    return x.iloc[-1]


def last_7_days_sum(x):
    return x.iloc[-7:].sum()


def overview(selection, compact=True):
    '''
    Returns
    - sum,
    - last_7_days_sum: sum in the last 7 days,
    - rolling_avg:  rolling average for the last 7 days,
    - latest, and
    - max
    values for cases and deaths
    '''
    if not compact:
        return selection.sort_values(
            by=['year', 'month', 'day'],
            ascending=True).groupby("countriesAndTerritories").agg({
                'cases': ['sum', last_7_days_sum, rolling_avg, latest, 'max'],
                'deaths': ['sum', last_7_days_sum, rolling_avg, latest, 'max'],
                'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000':
                [latest]
            }).sort_values(by=('cases', 'last_7_days_sum'), ascending=False)
    else:
        return selection.sort_values(
            by=['year', 'month', 'day'],
            ascending=True).groupby("countriesAndTerritories").agg({
                'cases': ['sum', last_7_days_sum, rolling_avg, latest],
                'deaths': ['sum', last_7_days_sum, rolling_avg, latest],
            }).sort_values(by=('cases', 'last_7_days_sum'), ascending=False)
