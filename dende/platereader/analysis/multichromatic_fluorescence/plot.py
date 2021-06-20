import logging

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from dende.platereader.analysis.sample import Sample, Material

logger = logging.getLogger(__name__)


def plot(df, config, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index / 60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index
    legends = []
    lines = []
    ax = None

    for sample, lens_setting, color in config:  # the variable sample is first WT15, then CytroGFP2Orp1#1 and then SecrroGFP2Orp1#19
        sample_cols = [col for col in df if col.startswith(f"{lens_setting}!{sample}§")]
        df[f"{sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[f"{sample}-STD"] = df[sample_cols].std(axis=1)  # calculate the errors column
        df[f"{sample}-SEM"] = df[sample_cols].sem(axis=1)  # calculate the errors column
        ax = df[f"{sample}"].plot(figsize=(12, 8), yerr=df[f"{sample}-STD"], alpha=0.4, color=color, legend=False, grid=True)
        lines.append(Line2D([0], [0], color=color))
        legends.append(f"{sample.get_description()} at {lens_setting}")
        df[f"{sample}"].plot(figsize=(12, 8), style=['o'], color=color,
                                           markersize=4, ax=ax, grid=True, legend=True)

    ax.set_ylabel("Fluorescence Intensity")
    plt.legend(lines, legends)
    plt.show()


def autofluorescence_plot(df, config, control, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index / 60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index

    legends = []
    lines = []
    ax = None
    for sample, lens_setting, color in config:
        ls_sample = f"{lens_setting}!{sample}"  # lens_setting + baseline
        baseline = Sample(Material(control, True), sample.treatment)
        ls_baseline = f"{lens_setting}!{baseline}"  # lens_setting + baseline
        if baseline not in df.columns:
            baseline_cols = [col for col in df if col.startswith(f"{ls_baseline}§")]
            df[ls_baseline] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
            df[f"{ls_baseline}-STD"] = df[baseline_cols].std(axis=1)
            df[f"{ls_baseline}-SEM"] = df[baseline_cols].sem(axis=1)
        sample_cols = [col for col in df if col.startswith(f"{lens_setting}!{sample}§")]
        df[ls_sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[ls_sample + "-STD"] = df[sample_cols].std(axis=1)
        df[ls_sample + "-SEM"] = df[sample_cols].sem(axis=1)
        df[ls_sample + "-adjusted"] = df[ls_sample] - df[ls_baseline]
        df[ls_sample + "-gaussian-error"] = (
                                                df[ls_sample + "-SEM"] ** 2 +
                                                df[f"{lens_setting}!{baseline}-SEM"] ** 2
                                            ) ** 0.5
        ax = df[ls_sample + "-adjusted"].plot(figsize=(12, 8),
                                              yerr=df[ls_sample + "-gaussian-error"],
                                              alpha=0.4,
                                              legend=False, grid=True, color=color)
        lines.append(Line2D([0], [0], color=color))
        legends.append(f"{sample.get_description()} at {lens_setting}nm, corrected for autofluorescence")
        df[ls_sample + "-adjusted"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                         ax=ax, grid=True, legend=True)

    ax.set_ylabel("Fluorescence Intensity")
    plt.legend(lines, legends)
    plt.show()


def ratio_plot(df, config, lens_settings, control, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index / 60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index

    legends = []
    lines = []
    ax = None
    for sample, color in config["plain"]:
        for lens_setting in lens_settings:
            wl_sample = f"{lens_setting}!{sample}"
            sample_cols = [col for col in df if col.startswith(f"{wl_sample}§")]
            df[f"{wl_sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
            df[f"{wl_sample}-STD"] = df[sample_cols].std(axis=1)
            df[f"{wl_sample}-SEM"] = df[sample_cols].sem(axis=1)

        df[f"{sample}-ratio"] = df[f"{lens_settings[0]}!{sample}"] / df[f"{lens_settings[1]}!{sample}"]
        df[f"{sample}-ratio-error"] = df[f"{sample}-ratio"] * (
                (df[f"{lens_settings[0]}!{sample}-STD"] / df[f"{lens_settings[0]}!{sample}"]) ** 2 +
                (df[f"{lens_settings[1]}!{sample}-STD"] / df[f"{lens_settings[1]}!{sample}"]) ** 2
        ) ** .5
        ax = df[f"{sample}-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
                                        yerr=df[f"{sample}-ratio-error"], color=color)
        lines.append(Line2D([0], [0], color=color))
        legends.append(f"ratio for {sample.get_description()}")
        df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                   ax=ax, grid=True, legend=True)

    for lens_setting in lens_settings:
        for sample, color in config["af"]:
            ls_sample = f"{lens_setting}!{sample}"  # lens_setting + baseline
            baseline = Sample(Material(control, True), sample.treatment)
            ls_baseline = f"{lens_setting}!{baseline}"  # lens_setting + baseline

            if ls_baseline not in df.columns:
                baseline_cols = [col for col in df if col.startswith(f"{ls_baseline}§")]
                df[f"{ls_baseline}"] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
                df[f"{ls_baseline}-STD"] = df[baseline_cols].std(axis=1)
                df[f"{ls_baseline}-SEM"] = df[baseline_cols].sem(axis=1)
            sample_cols = [col for col in df if col.startswith(f"{ls_sample}§")]
            df[f"{ls_sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
            df[f"{ls_sample}-STD"] = df[sample_cols].std(axis=1)
            df[f"{ls_sample}-SEM"] = df[sample_cols].sem(axis=1)
            df[f"{ls_sample}-adjusted"] = df[f"{ls_sample}"] - df[f"{ls_baseline}"]
            df[f"{ls_sample}-gaussian-error"] = (df[f"{ls_sample}-SEM"] ** 2 + df[f"{ls_baseline}-SEM"] ** 2) ** .5

    for sample, color in config["af"]:
        df[f"{sample}-ratio"] = df[f"{lens_settings[0]}!{sample}-adjusted"] / df[f"{lens_settings[1]}!{sample}-adjusted"]
        df[f"{sample}-ratio-gaussian-error"] = df[f"{sample}-ratio"] * (
                (df[f"{lens_settings[0]}!{sample}-gaussian-error"] / df[f"{lens_settings[0]}!{sample}"]) ** 2 + (
                df[f"{lens_settings[1]}!{sample}-gaussian-error"] / df[f"{lens_settings[1]}!{sample}"]) ** 2
                   ) ** .5
        ax = df[f"{sample}-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
                                        yerr=df[f"{sample}-ratio-gaussian-error"], color=color)
        lines.append(Line2D([0], [0], color=color))
        legends.append(f"ratio for {sample.get_description()}, corrected for autofluorescence")
        df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                   ax=ax, grid=True, legend=True)
    plt.legend(labels=legends)
    plt.show()
