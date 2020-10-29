import logging
from functools import cached_property
from json import dumps, loads

import pandas as pd
import requests

from helper import *


class ECDC:
    @cached_property
    def df(self):
        response = requests.get(
            'https://opendata.ecdc.europa.eu/covid19/casedistribution/json')
        _df = pd.read_json(dumps(response.json()['records']))
        _df['dateRep'] = pd.to_datetime(_df['dateRep'].astype(str),
                                        format='%d/%m/%Y')
        _df['Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'] = pd.to_numeric(
            _df['Cumulative_number_for_14_days_of_COVID-19_cases_per_100000'].
            fillna(0))

        return _df

    def overview(self, selection=None):
        '''
        Returns
        - sum,
        - last_7_days_sum: sum in the last 7 days,
        - rolling_avg:  rolling average for the last 7 days,
        - latest, and
        - max
        values for cases and deaths
        '''
        if selection is None: selection = self.df
        return selection.sort_values(
            by=['year', 'month', 'day'],
            ascending=True).groupby("countriesAndTerritories").agg({
                'cases': [rolling_avg, last_5_days, 'max'],
                'deaths':
                ['sum', last_7_days_sum, rolling_avg, last_5_days, 'max'],
                'Cumulative_number_for_14_days_of_COVID-19_cases_per_100000':
                [latest, 'max']
            }).sort_values(by=('cases', 'rolling_avg'), ascending=False)

    def compact_overview(self, selection):
        if selection is None: selection = self.df
        return selection.sort_values(
            by=['year', 'month', 'day'],
            ascending=True).groupby("countriesAndTerritories").agg({
                'cases': [rolling_avg, latest, 'max'],
                'deaths': ['sum', last_7_days_sum, rolling_avg, latest, 'max'],
            }).sort_values(by=('cases', 'rolling_avg'), ascending=False)

    def country_name(self, geoId):
        return self.df[self.df.geoId ==
                       geoId].iloc[0].countriesAndTerritories.replace(
                           '_', ' ')

    def select_country(self, geoId, ndays=0):
        if not ndays:
            selection = self.df[self.df.geoId == geoId].sort_values(
                by=['year', 'month', 'day'], ascending=True)
        else:
            selection = self.df[self.df.geoId == geoId].sort_values(
                by=['year', 'month', 'day'], ascending=True).tail(ndays)

        return selection

    def plot_country(self, geoId, ndays=0, **kwargs):
        selection = self.select_country(geoId, ndays)
        return self.plot_selection(selection, ndays, **kwargs)

    def plot_selection(self, selection, ndays=0, **kwargs):
        f, ax = plt.subplots()
        x = selection.dateRep
        column = kwargs.get('column', 'cases')
        y = selection[column]
        dates = pd.date_range(start=min(x),
                              end=max(x),
                              freq='W',
                              closed='left')

        xticks = (dates, dates.strftime('%Y W #%U'))
        ax = bar(ax, x=x, y=y, label=column, xticks=xticks, **kwargs)
        ax = plot_rolling_avg(ax, x=x, y=y, **kwargs)

        if kwargs.get('log'):
            plt.yscale('log')

        plt.legend(loc='best')
        plt.title('')
        plt.xlim(x.iloc[-ndays], x.iloc[-1])
        plt.tight_layout()
        return ax

    def plot_comparison(
            self,
            geoIds,
            roll_days=1,
            field='Cumulative_number_for_14_days_of_COVID-19_cases_per_100000',
            log=False,
            ndays=30):
        f, ax = plt.subplots(figsize=(9, 6))
        for geoId in geoIds:
            selection = self.select_country(geoId, ndays)
            ax.plot(selection.dateRep,
                    selection[field],
                    label=self.country_name(geoId))

        ax.xaxis.set_major_locator(plt.MaxNLocator(25))
        ax.yaxis.set_major_locator(plt.MaxNLocator(10))

        plt.xticks(rotation=45)
        if log:
            plt.yscale('log')

        plt.legend(loc='best')
        plt.title(field)
        plt.tight_layout()
        return ax
