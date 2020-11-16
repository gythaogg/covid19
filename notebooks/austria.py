import logging
from datetime import datetime
from functools import cached_property
from json import dumps, loads

import numpy as np
import pandas as pd
import requests
from matplotlib import pyplot as plt

from helper import bar, latest, plot_rolling_avg, pretty_plot


class Austria:
    @cached_property
    def epicurve(self):
        df = pd.read_csv(
            'https://info.gesundheitsministerium.at/data/Epikurve.csv',
            delimiter=';')
        weekday = []
        for i, row in df.iterrows():
            day_num = datetime.strptime(row['time'], '%d.%m.%Y').weekday()
            weekday.append(day_num)

        df['weekday'] = weekday
        df['time'] = pd.to_datetime(df['time'].astype(str), format='%d.%m.%Y')

        return df.sort_values(by='time', ascending=True)

    @cached_property
    def fall_zählen(self):
        df = pd.read_csv(
            'https://covid19-dashboard.ages.at/data/CovidFallzahlen.csv',
            delimiter=';')
        df['MeldeDatum'] = pd.to_datetime(df['MeldeDatum'].astype(str),
                                          format='%d.%m.%Y %H:%M:%S')

        return df

    @cached_property
    def fälle_timeline_gkz(self):
        df = pd.read_csv(
            'https://covid19-dashboard.ages.at/data/CovidFaelle_Timeline_GKZ.csv',
            delimiter=';')
        df['Time'] = pd.to_datetime(df['Time'].astype(str),
                                    format='%d.%m.%Y %H:%M:%S')

        return df

    @cached_property
    def ampel(self):
        '''
        Stand Warnungstufe
        '''
        df = pd.read_json(
            'https://corona-ampel.gv.at/sites/corona-ampel.gv.at/files/assets/Warnstufen_Corona_Ampel_aktuell.json'
        )
        df['Stand'] = pd.to_datetime(df['Stand'].astype(str),
                                     format='%Y-%m-%dT%H:%M:%SZ')

        return df

    @cached_property
    def ampel_aktuell(self):
        '''
        Region	GKZ	Name	Warnstufe
        '''
        df = self.ampel
        latest = df.sort_values('Stand', ascending=False).iloc[0].Warnstufen
        df = pd.DataFrame(latest)
        df['Warnstufe'] = df.Warnstufe.astype(int)
        return df

    @cached_property
    def altersgruppe(self):
        '''
        AltersgruppeID Altersgruppe
        Bundesland BundeslandID AnzEinwohner
        Geschlecht Anzahl AnzahlGeheilt	AnzahlTot
        '''
        df = pd.read_csv(
            'https://covid19-dashboard.ages.at/data/CovidFaelle_Altersgruppe.csv',
            delimiter=';')
        return df

    def plot_tägliche_erkrankungen(self, roll_days, ndays=30, **kwargs):
        f, ax = plt.subplots()
        x = self.epicurve['time']
        y = self.epicurve['tägliche Erkrankungen']
        dates = pd.date_range(start=min(x),
                              end=max(x),
                              freq='W',
                              closed='left')

        xticks = (dates, dates.strftime('%Y W #%U'))

        ax = bar(ax,
                 x=x,
                 y=y,
                 label='tägliche Erkrankungen',
                 xticks=xticks,
                 **kwargs)

        if roll_days:
            ax = plot_rolling_avg(ax, x=x, y=y, roll_days=roll_days, **kwargs)
        if kwargs.get('log'):
            plt.yscale('log')

        print([x.iloc[-ndays], x.iloc[-1]])
        plt.xlim(x.iloc[-ndays], x.iloc[-1])
        plt.legend(loc='best')
        plt.title('Positive COVID tests')
        plt.tight_layout()
        return ax

    def plot_cases_by_day_of_the_week(self, num_weeks_history=5):
        f, ax = plt.subplots(figsize=(9, 5))
        grouped = self.epicurve.groupby(self.epicurve.time.dt.day_name(),
                                        as_index=False).agg(
                                            ('sum', 'max', 'min', 'median',
                                             'mean', latest)).sort_values(
                                                 ('weekday', 'latest'))

        ax.scatter(grouped.index,
                   grouped[('tägliche Erkrankungen', 'max')],
                   label='max',
                   marker='D',
                   s=50,
                   c='k')
        ax.scatter(grouped.index,
                   grouped[('tägliche Erkrankungen', 'median')],
                   label='median',
                   marker='D')
        ax.scatter(grouped.index,
                   grouped[('tägliche Erkrankungen', 'min')],
                   label='min',
                   marker='D')

        last_n_weeks = self.epicurve.sort_values(
            'time').time.dt.isocalendar().week.unique()[-num_weeks_history:]
        print(last_n_weeks)
        for w in last_n_weeks:
            df = self.epicurve[self.epicurve.time.dt.isocalendar().week == w]
            ax.plot(df.time.dt.day_name(),
                    df['tägliche Erkrankungen'],
                    label=f'week #{w}',
                    marker='o',
                    linestyle='--',
                    alpha=0.7)

        pretty_plot(ax, log=False, num_x_locators=7)

        return ax

    def plot_positivity_rate(self, bundesland='Alle'):
        cases = self.fall_zählen[self.fall_zählen.Bundesland == bundesland]
        timeline = self.fälle_timeline_gkz[self.fälle_timeline_gkz.Bezirk ==
                                           bundesland]
        print(cases.MeldeDatum.max())
        f, ax = plt.subplots()
        ax.plot(cases.MeldeDatum,
                cases.TestGesamt.diff().rolling(7).mean(),
                label='Tests')
        ax.plot(timeline.Time,
                timeline.AnzahlFaelle.rolling(7).mean(),
                label='Cases')

        pretty_plot(ax, log=True, title=f'Positiviy rate - {bundesland}')
        return ax
