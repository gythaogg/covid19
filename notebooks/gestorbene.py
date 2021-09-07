from functools import cached_property

import pandas as pd
from tqdm.auto import tqdm

tqdm.pandas()


class Gestorbene:
    @property
    def under_65(self):
        return self.df[self.df['C-ALTERGR65-0'] == 'ALTERSGR65-1']

    @property
    def over_65(self):
        return self.df[self.df['C-ALTERGR65-0'] == 'ALTERSGR65-2']

    @cached_property
    def df(self):
        _df = pd.read_csv(
            'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100.csv',
            delimiter=';')

        # replace codes with labels
        # C-KALWOCHE-0	C-B00-0	C-ALTERGR65-0	C-C11-0	F-ANZ-1

        def update_rows(row):
            kal_data = self.kal_woche[
                self.kal_woche.code ==
                row['C-KALWOCHE-0']].iloc[0]['name'].replace('(', '').replace(
                    ')', '').split()
            sex_label = self.geschlecht[self.geschlecht.code ==
                                        row['C-C11-0']].iloc[0].en_name
            bundesland = self.bundesland[self.bundesland.code ==
                                         row['C-B00-0']].iloc[0]['name'].split(
                                             '<')[0]

            return (kal_data[-3], kal_data[-1], sex_label, bundesland)

        _df['week_begin'], _df['week_end'], _df['sex'], _df[
            'bundesland'] = zip(*_df.progress_apply(update_rows, axis=1))
        _df['week_begin'] = pd.to_datetime(_df['week_begin'].astype(str),
                                           format='%d.%m.%Y')
        _df['week_end'] = pd.to_datetime(_df['week_end'].astype(str),
                                         format='%d.%m.%Y')

        return _df

    @cached_property
    def headers(self):
        '''
        code	name	en_name
        0	C-KALWOCHE-0	Kalenderwoche des Sterbedatums	Calendar week
        1	C-B00-0	Bundesland des Wohnorts des Verstorbenen	Province (NUTS 2 unit) of deceased
        2	C-ALTERGR65-0	Altersgruppe des Verstorbenen	Age group of deceased
        3	C-C11-0	Geschlecht des Verstorbenen	Gender of deceased
        4	F-ANZ-1	Anzahl der Sterbefälle	Number of deaths
        '''
        url = 'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100_HEADER.csv'
        return pd.read_csv(url, delimiter=';')

    @cached_property
    def geschlecht(self):
        '''
        code	name	en_name
        0	C11-1	männlich	male
        1	C11-2	weiblich	female
        2	C11-0	Nicht klassifizierbar <0>	Not classifiable <0>
        '''
        url = 'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100_C-C11-0.csv'
        return pd.read_csv(url, delimiter=';')

    @cached_property
    def altes_gruppe(self):
        '''
        code	name	Unnamed: 2	en_name	de_desc	de_link	en_desc	en_link	de_syn	en_syn
        0	ALTERSGR65-1	0 bis 64 Jahre	NaN	0 to 64 years	NaN	NaN	NaN	NaN	NaN	NaN
        1	ALTERSGR65-2	65 Jahre und älter	NaN	65 years and more	NaN	NaN	NaN	NaN	NaN	NaN
        '''
        url = 'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100_C-ALTERGR65-0.csv'
        return pd.read_csv(url, delimiter=';')

    @cached_property
    def bundesland(self):
        '''
        code	name	Unnamed: 2	en_name	de_desc	de_link	en_desc	en_link	de_syn	en_syn
        0	B00-1	Burgenland <AT11>	NaN	Burgenland <AT11>	NaN	NaN	NaN	NaN	NaN	NaN
        1	B00-2	Kärnten <AT21>	NaN	Carinthia <AT21>	NaN	NaN	NaN	NaN	NaN	NaN
        2	B00-3	Niederösterreich <AT12>	NaN	Lower Austria <AT12>	NaN	NaN	NaN	NaN	NaN	NaN
        3	B00-4	Oberösterreich <AT31>	NaN	Upper Austria <AT31>	NaN	NaN	NaN	NaN	NaN	NaN
        4	B00-5	Salzburg <AT32>	NaN	Salzburg <AT32>	NaN	NaN	NaN	NaN	NaN	NaN
        '''
        url = 'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100_C-B00-0.csv'
        return pd.read_csv(url, delimiter=';')

    @cached_property
    def kal_woche(self):
        url = 'http://data.statistik.gv.at/data/OGD_gest_kalwo_GEST_KALWOCHE_100_C-KALWOCHE-0.csv'
        return pd.read_csv(url, delimiter=';')
