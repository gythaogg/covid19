#!/home/gythaogg/anaconda3/bin/python
import logging

logging.basicConfig(level=logging.ERROR)


import calendar
from datetime import datetime, timedelta

from matplotlib import pyplot as plt
from matplotlib.ticker import (AutoMinorLocator, FormatStrFormatter,
                               MultipleLocator)

plt.style.use("seaborn-whitegrid")
import numpy as np
import pandas as pd
# plt.style.use('seaborn')
from matplotlib import cm

pd.set_option("display.max_colwidth", None)

from austria import Austria
from ecdc import ECDC
from helper import *


def predict_future(
    past_days, past_y, ndays=14, predict_days=30, degree_fit=2, window_size=14
):
    """
    @ndays: number of days to consider from the end for predicting future
    """
    past_y = past_y.rolling(window_size).mean().tolist()
    future = np.arange(0, ndays + predict_days)
    past_days = past_days.dt.to_pydatetime()
    future_days = pd.date_range(
        start=past_days[-ndays], end=past_days[-1] + timedelta(days=predict_days)
    ).to_list()

    x = np.arange(ndays)
    z = np.polyfit(x, past_y[-ndays:], degree_fit)
    p = np.poly1d(z)
    return future_days, p(future)


def str2float(x):
    return float(str(x).replace(",", "."))


def plot_yearly(
    df, date_column, value_column, ax=None, title="", log=True, roll=14, **plot_params
):
    if not ax:
        f, ax = plt.subplots()
    for y in df.sort_values(by=date_column, ascending=False)[
        date_column
    ].dt.year.unique():
        df_year = df[df[date_column].dt.year == y][[date_column, value_column]].rename(
            columns={value_column: f"{y}"}
        )
        df_year[date_column] = df_year[date_column].dt.strftime("%m-%d")
        ax.plot(
            df_year[date_column],
            df_year[f"{y}"].rolling(roll).mean(),
            label=f"{y}",
            marker="o",
            markersize=2,
            **plot_params,
        )

    title = f"{title} ({roll} day average)" if roll > 1 else title
    ax.set_title(title)
    ax.set_xlabel("")
    pretty_plot(ax, major_locator=28)
    #     plt.xticks( range(1,13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    if log:
        ax.set_yscale("log")
    plt.tight_layout()


def plot_yearly_avg(bezirk="Alle", log=False, roll=14, ax=None):
    if not ax:
        f, ax = plt.subplots()
    if bezirk != "Alle":
        cases = AT.fälle_timeline_gkz[AT.fälle_timeline_gkz.Bezirk == bezirk]
    else:
        cases = AT.fälle_timeline_gkz.groupby(by="Time", as_index=False).agg("sum")
    for y in cases.sort_values(by="Time", ascending=False).Time.dt.year.unique():
        cases_year = cases[cases.Time.dt.year == y][["Time", "AnzahlFaelle"]].rename(
            columns={"AnzahlFaelle": f"{y}"}
        )
        cases_year["Time"] = cases_year["Time"].dt.strftime("%m-%d")
        ax.plot(
            cases_year["Time"],
            cases_year[f"{y}"].rolling(roll).mean(),
            label=f"{y}",
            marker="o",
            markersize=2,
            alpha=0.7,
        )

    title = bezirk if bezirk != "Alle" else "Österreich"
    title = f"{title} - Cases ({roll} day average)" if roll > 1 else title
    ax.set_title(title)
    ax.set_xlabel("")
    pretty_plot(ax, major_locator=28)
    #     plt.xticks( range(1,13), ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    if log:
        ax.set_yscale("log")
    plt.tight_layout()


def refresh_data():
    today = f"{datetime.now().year}_{datetime.now().month:02d}_{datetime.now().day:02d}"
    ecdc = ECDC()
    AT = Austria()
    print("TODAY: ", datetime.now())

    return AT, ecdc


def main():
    STORAGE_LOC = "/home/gythaogg/Documents/Dropbox/covid"
    timenow = datetime.now()
    today = f"{timenow.year}_{timenow.month:02d}_{timenow.day:02d}"

    AT, ecdc = refresh_data()
    # Days of the week comparison
    HISTORY = 15

    ax = AT.plot_cases_by_day_of_the_week(num_weeks_history=HISTORY, bezirk="Wien")
    ax.get_figure().savefig(f"{STORAGE_LOC}/vienna_weekly_{today}.png")
    ax = AT.plot_cases_by_day_of_the_week(num_weeks_history=HISTORY, bezirk="")
    ax.get_figure().savefig(f"{STORAGE_LOC}/austria_weekly_{today}.png")

    # Annual comparison
    ROLL = 7
    LOG_PLOT = True
    ALPHA = 0.8
    f, ax = plt.subplots(nrows=3, figsize=(7, 10), sharex=True)
    # plot_yearly_avg(bezirk='Wien', log=True, roll=ROLL,ax=ax[0])
    plot_yearly(
        AT.fälle_timeline_gkz[AT.fälle_timeline_gkz.Bezirk == "Wien"],
        ax=ax[0],
        title="Cases",
        date_column="Time",
        value_column="AnzahlFaelle",
        roll=ROLL,
        log=LOG_PLOT,
        alpha=ALPHA,
    )
    plot_yearly(
        AT.fall_zählen[AT.fall_zählen.Bundesland == "Wien"],
        ax=ax[1],
        title="Hospital beds",
        date_column="MeldeDatum",
        value_column="FZHosp",
        roll=ROLL,
        log=LOG_PLOT,
        alpha=ALPHA,
    )
    plot_yearly(
        AT.fall_zählen[AT.fall_zählen.Bundesland == "Wien"],
        ax=ax[2],
        title="ICU",
        date_column="MeldeDatum",
        value_column="FZICU",
        roll=ROLL,
        log=LOG_PLOT,
        alpha=ALPHA,
    )
    f.suptitle("Wien", fontsize=16)
    plt.tight_layout()
    # plot_yearly_avg(bezirk='Wien', log=True, roll=ROLL)
    f.savefig(f"{STORAGE_LOC}/vienna_annual_{today}.png")

    f, ax = plt.subplots(nrows=3, figsize=(7, 10), sharex=True)
    plot_yearly(
        AT.fälle_timeline_gkz.groupby(by="Time", as_index=False).agg("sum"),
        title="Cases",
        date_column="Time",
        value_column="AnzahlFaelle",
        ax=ax[0],
        log=LOG_PLOT,
        roll=ROLL,
        alpha=ALPHA,
    )

    plot_yearly(
        AT.fall_zählen[AT.fall_zählen.Bundesland == "Alle"],
        ax=ax[1],
        title="Hospital beds",
        date_column="MeldeDatum",
        value_column="FZHosp",
        log=LOG_PLOT,
        roll=ROLL,
        alpha=ALPHA,
    )
    plot_yearly(
        AT.fall_zählen[AT.fall_zählen.Bundesland == "Alle"],
        ax=ax[2],
        title="ICU",
        date_column="MeldeDatum",
        value_column="FZICU",
        log=LOG_PLOT,
        roll=ROLL,
        alpha=ALPHA,
    )
    f.suptitle("Austria", fontsize=16)
    plt.tight_layout()
    f.savefig(f"{STORAGE_LOC}/austria_annual_{today}.png")


if __name__ == "__main__":

    main()
