import logging

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


logger = logging.getLogger(__name__)


class LuminescencePlot:

    def __init__(self, df, time_unit, presets, plain_data, diff_data=None, title=None):
        self.df = df
        if time_unit not in ["Seconds", "Minutes"]:
            raise(Exception(f"Unknown time unit: {time_unit}"))
        self.time_unit = time_unit
        if self.time_unit == "Minutes":
            minutes_index = self.df.index / 60
            minutes_index.set_names("Time [min]", inplace=True)
            self.df.index = minutes_index

        self.presets = presets
        self.figsize = (12, 8)
        self.plain_data = plain_data
        self.diff_data = diff_data
        self.title = title
        self.ox_treatments = ["H202"]
        self.red_treatmens = ["DTT", "DPS"]
        self.ratios = {"plain": {}, "af": {}}

    def plot_lines_with_errorbars(self, sample, error, color, ax=None):
        if error is not None:
            yerr = self.df[error]
        else:
            yerr = None
        return self.df[sample].plot(figsize=self.figsize, yerr=yerr, alpha=0.4, legend=False,
                                    grid=True, color=color, ax=ax)

    def plot_dots(self, sample, color, ax):
        return self.df[sample].plot(figsize=self.figsize, style=['o'], color=color, markersize=4,
                                    ax=ax, grid=True, legend=True)

    def calc_avg_std_sem(self, col_name):
        if col_name in self.df:
            logger.warning(f"Already calculated avg and errors for {col_name}")
            return
        col_names = [col for col in self.df if col.startswith(f"{col_name}§")]
        self.df[col_name] = self.df[col_names].mean(axis=1)
        self.df[col_name + "-STD"] = self.df[col_names].std(axis=1)  # calculate the errors column
        self.df[col_name + "-SEM"] = self.df[col_names].sem(axis=1)  # calculate the errors column

    def plot(self):
        lines = []
        legends = []
        ax = None
        for lens_setting, sample, color in self.plain_data:
            material, treatment = sample.material, sample.treatment
            self.calc_avg_std_sem(f"{lens_setting}!{sample}")
            ax = self.plot_lines_with_errorbars(f"{lens_setting}!{sample}",
                                                error=f"{lens_setting}!{sample}-STD", color=color)
            self.plot_dots(f"{lens_setting}!{sample}", color=color, ax=ax)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{material} with {treatment} and {lens_setting}")
            else:
                legends.append(f"{material} with {lens_setting}")

        for p1, p2, sample, color in self.diff_data:
            material, treatment = sample.material, sample.treatment

            self.calc_avg_std_sem(f"{p1}!{sample}")
            self.calc_avg_std_sem(f"{p2}!{sample}")
            self.df[f"{p1}!{p2}"] = self.df[f"{p1}!{sample}"] - self.df[f"{p2}!{sample}"]
            self.df[f"{p1}!{p2}-gauss-error"] = (
                                                       self.df[f"{p1}!{sample}-SEM"] ** 2 +
                                                       self.df[f"{p2}!{sample}-SEM"] ** 2
                                               ) ** .5

            ax = self.plot_lines_with_errorbars(f"{p1}!{p2}", error=f"{p1}!{p2}-gauss-error", color=color, ax=ax)
            self.plot_dots(f"{p1}!{p2}", color=color, ax=ax)
            lines.append(Line2D([0], [0], color=color))
            if treatment:
                legends.append(f"{material} with {treatment} and corrected with filter")
            else:
                legends.append(f"{material} corrected with filter")

        ax.set_ylabel("Luminescence Intensity")
        plt.legend(lines, legends)
        plt.show()
