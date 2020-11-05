import numpy as np
from matplotlib import pyplot as plt

WEEKDAYS = ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday')


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
            label=f'rolling average ({roll_days})',
            marker='o',
            markersize=4,
            linestyle='--')
    return ax


def pretty_plot(ax, **kwargs):
    plt.xticks(rotation=45)
    if kwargs.get('xticks'):
        plt.xticks(*kwargs.get('xticks'), rotation=45)
    else:
        ax.xaxis.set_major_locator(plt.MaxNLocator(20))

    if kwargs.get('log'):
        plt.yscale('log')

    plt.legend(loc='best')
    plt.tight_layout()
