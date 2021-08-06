import logging
from abc import ABC
from typing import Tuple

import matplotlib.axes
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class Plot(ABC):

    df: pd.DataFrame
    figure: Figure
    ax: matplotlib.axes.Axes
    canvas: FigureCanvasTkAgg
    toolbar: NavigationToolbar2Tk
    figsize: Tuple

    def setup_figure(self):
        self.figure = plt.figure()
        self.ax = self.figure.subplots()
        self.ax.minorticks_on()

        self.ax.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(side="top", fill='both', expand=True)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.toolbar.pack()

    def calc_avg_std_sem(self, sample):
        if sample in self.df:
            logger.warning(f"column {sample} already exists")
            return
        col_names = [col for col in self.df if col.startswith(f"{sample}§")]
        self.df[f"{sample}"] = self.df[col_names].mean(axis=1)
        self.df[f"{sample}" + "-STD"] = self.df[col_names].std(axis=1)
        self.df[f"{sample}" + "-SEM"] = self.df[col_names].sem(axis=1)

    def plot_lines_with_errorbars(self, sample, error, color):
        if error is not None:
            yerr = self.df[error]
        else:
            yerr = None
        return self.df[f"{sample}"].plot(figsize=self.figsize, yerr=yerr, alpha=0.4, legend=False, grid=True,
                                         color=color, ax=self.ax)

    def plot_dots(self, sample, color):
        return self.df[f"{sample}"].plot(figsize=self.figsize, style=['o'], color=color, markersize=4, ax=self.ax,
                                         grid=True, legend=True)
