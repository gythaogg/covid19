import logging
from datetime import datetime
from functools import cached_property
from json import dumps, loads

import numpy as np
import pandas as pd
import requests
from matplotlib import cm
from matplotlib import pyplot as plt

from helper import bar, latest, plot_rolling_avg, pretty_plot


class Austria:
    # @cached_property
    # def epicurve(self):
    #     df = pd.read_csv(
    #         'https://info.gesundheitsministerium.at/data/Epikurve.csv',
    #         delimiter=';')
    #     weekday = []
    #     for i, row in df.iterrows():
    #         day_num = datetime.strptime(row['time'], '%d.%m.%Y').weekday()
    #         weekday.append(day_num)

    #     df['weekday'] = weekday
    #     df['time'] = pd.to_datetime(df['time'].astype(str), format='%d.%m.%Y')

    #     return df.sort_values(by='time', ascending=True)

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

    def plot_tägliche_erkrankungen(self,
                                   roll_days,
                                   ndays=30,
                                   column_name='AnzahlFaelle',
                                   bezirk='Wien',
                                   **kwargs):
        if bezirk:
            df = self.fälle_timeline_gkz[self.fälle_timeline_gkz.Bezirk ==
                                         bezirk]
        else:
            df = self.fälle_timeline_gkz.groupby(
                by='Time', as_index=False).agg(
                    'sum')  #[self.fälle_timeline_gkz.Bezirk == bezirk]
        f, ax = plt.subplots()
        x = df['Time']
        y = df[column_name]
        dates = pd.date_range(start=min(x),
                              end=max(x),
                              freq='W',
                              closed='left')

        xticks = (dates, dates.strftime('%Y W #%U'))

        ax = bar(ax, x=x, y=y, label=column_name, xticks=xticks, **kwargs)

        if roll_days:
            ax = plot_rolling_avg(ax, x=x, y=y, roll_days=roll_days, **kwargs)
        if kwargs.get('log'):
            plt.yscale('log')

        print([x.iloc[-ndays], x.iloc[-1]])
        plt.xlim(x.iloc[-ndays], x.iloc[-1])
        plt.legend(loc='best')
        plt.title(
            f'Positive COVID tests - {bezirk if bezirk else "Österreich"}')
        plt.xticks(rotation=90)
        plt.tight_layout()
        return ax

    def plot_cases_by_day_of_the_week(self,
                                      num_weeks_history=5,
                                      column_name='AnzahlFaelle',
                                      bezirk='Wien'):
        f, ax = plt.subplots(figsize=(9, 5))
        viridis = cm.get_cmap('viridis', num_weeks_history)
        if bezirk:
            df = self.fälle_timeline_gkz[self.fälle_timeline_gkz.Bezirk ==
                                         bezirk]
        else:
            df = self.fälle_timeline_gkz.groupby(
                by='Time', as_index=False).agg(
                    'sum')  #[self.fälle_timeline_gkz.Bezirk == bezirk]

        grouped = df.groupby(by=df.Time.dt.day, as_index=False).agg(
            ('sum', 'max', 'min', 'median', 'mean',
             latest))  #.sort_values(df.Time.dt.day)

        # ax.scatter(grouped.index,
        #            grouped[(column_name, 'max')],
        #            label='max',
        #            marker='D',
        #            s=50,
        #            c='k')
        # ax.scatter(grouped.index,
        #            grouped[(column_name, 'median')],
        #            label='median',
        #            marker='D')
        # ax.scatter(grouped.index,
        #            grouped[(column_name, 'min')],
        #            label='min',
        #            marker='D')

        last_n_weeks = []
        for i, row in df.sort_values('Time', ascending=False).iterrows():
            y, w = row.Time.year, row.Time.week
            if (y, w) not in last_n_weeks:
                last_n_weeks.append((y, w))

            if len(last_n_weeks) == num_weeks_history:
                break

        for i, (y, w) in enumerate(last_n_weeks):
            dfi = df[(df.Time.dt.isocalendar().week == w)
                     & (df.Time.dt.isocalendar().year == y)]

            ax.plot(dfi.Time.dt.day_name(),
                    dfi[column_name],
                    label=f'year {y} w #{w}',
                    marker='d' if i == 0 else 'o',
                    linestyle='--',
                    color=viridis.colors[i] if i else 'k',
                    alpha=0.7 if i else 1)

        ax.set_title(bezirk if bezirk else "Österreich")

        if num_weeks_history >= 6:
            plt.legend(bbox_to_anchor=(1, 1), ncol=1, loc='upper left')

        pretty_plot(ax,
                    log=False,
                    num_x_locators=7,
                    show_legend=num_weeks_history < 6)
        return ax

    def plot_positivity_rate(self, bundesland='Alle'):
        cases = self.fall_zählen[self.fall_zählen.Bundesland == bundesland]

        if bundesland == 'Alle':
            timeline = self.fälle_timeline_gkz.groupby(
                by='Time', as_index=False).agg(
                    'sum')  #[self.fälle_timeline_gkz.Bezirk == bezirk]
        else:
            timeline = self.fälle_timeline_gkz[self.fälle_timeline_gkz.Bezirk
                                               == bundesland]

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
