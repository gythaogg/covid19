import numpy as np
from matplotlib import pyplot as plt

WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')


def aggregation_rules(fields, datefield):
    agg_rules = {}
    agg_rules[datefield] = latest
    for f in fields:
        agg_rules[f] = ('max', 'min', 'sum', 'median', latest)

    return agg_rules


def group_by_month(df, datefield, fields, include_last=False):
    agg_rules = aggregation_rules(fields, datefield)
    grouped = df.groupby(df[datefield].dt.month,
                         as_index=False).agg(agg_rules).sort_values(
                             (datefield, 'latest'))
    if not include_last:
        return grouped.iloc[:-1]

    return grouped


def group_by_week(df, datefield, fields, include_last=False):
    agg_rules = aggregation_rules(fields, datefield)
    grouped = df.groupby(df[datefield].dt.isocalendar().week,
                         as_index=False).agg(agg_rules).sort_values(
                             (datefield, 'latest'))
    if not include_last:
        return grouped.iloc[:-1]

    return grouped


def rolling_avg_round(x):
    return np.round(x.iloc[-7:].mean())


def rolling_avg(x):
    return x.iloc[-7:].mean()


def latest(x):
    return x.iloc[-1]


def last_7_days_sum(x):
    return x.iloc[-7:].sum()


def last_5_days(x):
    return ', '.join(x.iloc[-5:].astype(str))


def concat(x):
    return ', '.join(x.astype(str))


def bar(ax, x, y, **kwargs):
    plt.xticks(rotation=45)
    if kwargs.get('xticks'):
        plt.xticks(*kwargs.get('xticks'), rotation=45)
    else:
        ax.xaxis.set_major_locator(plt.MaxNLocator(20))

    ax.bar(x, y, label=kwargs.get('label'), alpha=0.6, color='C1')
    return ax


def plot_rolling_avg(ax, x, y, roll_days=0, **kwargs):
    if not roll_days: return ax

    ax.plot(x,
            y.rolling(roll_days).mean(),
            label=kwargs.get('label', f'rolling average ({roll_days})'),
            marker='o',
            markersize=4,
            linestyle='--',
            color=kwargs.get('color', 'k'))
    return ax


def pretty_plot(ax, show_legend=True, **kwargs):
    ax.tick_params(labelrotation=90, axis='x')
    if kwargs.get('xticks'):
        plt.xticks(*kwargs.get('xticks'), rotation=90)
    else:
        num_x_locators = kwargs.get('num_x_locators', 20)
        ax.xaxis.set_major_locator(plt.MaxNLocator(num_x_locators))

    if kwargs.get('log'):
        plt.yscale('log')

    if kwargs.get('title'):
        ax.set_title(kwargs.get('title'))

    if show_legend:
        ax.legend(loc='best')
    plt.tight_layout()
