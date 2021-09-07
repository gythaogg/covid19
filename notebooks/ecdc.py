import logging
from functools import cached_property
from json import dumps, loads

import pandas as pd
import requests
from tqdm.auto import tqdm

from helper import *

tqdm.pandas()

# Manually collected from https://www.ecdc.europa.eu/en/publications-data/data-covid-19-vaccination-eu-eea
class ECDC_LINKS:
    VAX = "https://opendata.ecdc.europa.eu/covid19/vaccine_tracker/json"
    CASES = (
        "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/json"
    )
    BEDS = "https://opendata.ecdc.europa.eu/covid19/hospitalicuadmissionrates/json"
    CASES_ALL = "https://opendata.ecdc.europa.eu/covid19/agecasesnational/json"


# loads(cases.groupby(by='countryterritoryCode').agg({'countriesAndTerritories':latest}).to_json())['countriesAndTerritories']
COUNTRIES = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "EL": "Greece",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IS": "Iceland",
    "IT": "Italy",
    "LI": "Liechtenstein",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "NO": "Norway",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
}

#
VACCINES = {
    "COM": "Comirnaty – Pfizer/BioNTech",
    "MOD": "mRNA-1273 – Moderna",
    "CN": "BBIBV-CorV – CNBG",
    "SIN": "Coronavac – Sinovac",
    "SPU": "Sputnik V - Gamaleya Research Institute",
    "AZ": "AZD1222 – AstraZeneca",
    "UNK": "UNKNOWN",
}


def to_int(x):
    try:
        return int(x)
    except (TypeError, ValueError):
        return 0


class ECDC:
    @classmethod
    def get_data(cls, url):
        res = requests.get(url)
        _df = pd.read_json(dumps(res.json()["records"]))
        return _df

    @cached_property
    def cases(self):
        _df = ECDC.get_data(ECDC_LINKS.CASES)
        _df["dateRep"] = pd.to_datetime(_df["dateRep"].astype(str), format="%d/%m/%Y")

        return _df.sort_values(by="dateRep")

    @cached_property
    def vaccines(self):
        _df = self.get_data(ECDC_LINKS.VAX)
        _df["NumberDosesReceived"] = _df.NumberDosesReceived.progress_apply(to_int)
        _df["Denominator"] = _df.Denominator.progress_apply(to_int)

        return _df.sort_values(by="YearWeekISO")

    def get_cases_by_country(self, country):
        return self.cases[
            (self.cases.geoId == country)
            | (self.cases.countryterritoryCode == country)
            | (self.cases.countriesAndTerritories == country)
        ].sort_values(by="dateRep")
