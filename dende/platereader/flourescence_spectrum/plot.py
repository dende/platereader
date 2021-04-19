import logging

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def plot(df, plain_plots, autofluorescence_plots=None, control=None, title=None):  #
    legends = []
    ax = None
    for sample, color in plain_plots:
        line, treatment = sample.split("$")
        sample_cols = [col for col in df if col.startswith(sample)]
        df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[sample + "-STD"] = df[sample_cols].std(axis=1)  # calculate the errors column
        df[sample + "-SEM"] = df[sample_cols].sem(axis=1)  # calculate the errors column
        ax = df[sample].plot(figsize=(12, 8), yerr=df[f"{sample}-STD"], alpha=0.4, legend=False, grid=True, title=title,
                             color=color)
        legends.append(f"{line} {treatment}")
        df[sample].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                        ax=ax, grid=True, legend=True)

    if autofluorescence_plots:
        for sample, color in enumerate(autofluorescence_plots, start=len(plain_plots)):
            line, treatment = sample.split("$")
            baseline = f"{control}${treatment}"
            baseline_cols = [col for col in df if col.startswith(baseline)]
            df[baseline] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
            df[baseline + "-STD"] = df[baseline_cols].std(axis=1)
            df[baseline + "-SEM"] = df[baseline_cols].sem(axis=1)
            sample_cols = [col for col in df if col.startswith(sample)]
            df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
            df[sample + "-STD"] = df[sample_cols].std(axis=1)
            df[sample + "-SEM"] = df[sample_cols].sem(axis=1)
            df[sample + "-adjusted"] = df[sample] - df[f"{baseline}"]
            df[sample + "-gaussian-error"] = (df[sample + "-SEM"] ** 2 + df[f"{baseline}-SEM"] ** 2) ** 0.5
            ax = df[sample + "-adjusted"].plot(figsize=(12, 8), yerr=df[sample + "-gaussian-error"], alpha=0.4,
                                               legend=False, grid=True, title=title, color=color)
            legends.append(f"{line} {treatment}, corrected for autofluorescence")
            df[sample + "-adjusted"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                          ax=ax, grid=True, legend=True)

    plt.legend(labels=legends)
    plt.show()
