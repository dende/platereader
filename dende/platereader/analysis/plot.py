from abc import ABC
from typing import Tuple

import matplotlib.axes
import pandas as pd


class Plot(ABC):

    df: pd.DataFrame
    ax: matplotlib.axes.Axes
    figsize: Tuple

    def calc_avg_std_sem(self, column):
        if column in self.df:
            return
        col_names = [col for col in self.df if col.startswith(f"{column}§")]
        self.df[f"{column}"] = self.df[col_names].mean(axis=1)
        self.df[f"{column}" + "-STD"] = self.df[col_names].std(axis=1)
        self.df[f"{column}" + "-SEM"] = self.df[col_names].sem(axis=1)

    def plot_lines_with_errorbars(self, sample, error, color):
        if error is not None:
            yerr = self.df[error]
        else:
            yerr = None
        return self.df[sample].plot(figsize=self.figsize, yerr=yerr, alpha=0.4, legend=False,
                                    grid=True, color=color, ax=self.ax)

    def plot_dots(self, sample, color):
        return self.df[sample].plot(figsize=self.figsize, style=['o'], color=color, markersize=4,
                                    ax=self.ax, grid=True, legend=True)
