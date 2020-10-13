import logging
from datetime import datetime
from functools import cached_property
from json import dumps, loads

import numpy as np
import pandas as pd
import requests

WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')


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

        return df

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
