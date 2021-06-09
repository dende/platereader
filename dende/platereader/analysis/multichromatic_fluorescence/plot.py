import logging

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

logger = logging.getLogger(__name__)


def plot(df, config, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index/60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index
    legends = []
    lines = []
    ax = None
    for sample, color in config:  # the variable sample is first WT15, then CytroGFP2Orp1#1 and then SecrroGFP2Orp1#19
        lens_setting, line_and_treatment = sample.split("!")

        try:
            line, treatment = line_and_treatment.split("$")
        except ValueError:
            line, treatment = line_and_treatment + [None]
        sample_cols = [col for col in df if col.startswith(sample)]
        df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[sample + "-STD"] = df[sample_cols].std(axis=1)  # calculate the errors column
        df[sample + "-SEM"] = df[sample_cols].sem(axis=1)  # calculate the errors column
        ax = df[sample].plot(figsize=(12, 8), yerr=df[f"{sample}-STD"], alpha=0.4, color=color, legend=False, grid=True)
        lines.append(Line2D([0], [0], color=color))
        if treatment:
            legends.append(f"{line} + {treatment} at {lens_setting}")
        else:
            legends.append(f"{line} at {lens_setting}")
        df[sample].plot(figsize=(12, 8), style=['o'], color=color,
                        markersize=4, ax=ax, grid=True, legend=True)

    ax.set_ylabel("Fluorescence Intensity")
    plt.legend(lines, legends)
    plt.show()


def autofluorescence_plot(df, config, control, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index/60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index

    legends = []
    lines = []
    ax = None
    for sample, color in config:  # the variable sample is first WT15, then CytroGFP2Orp1#1 and then SecrroGFP2Orp1#19
        wavelength, line_and_treatment = sample.split("!")
        try:
            line, treatment = line_and_treatment.split("$")
            baseline = f"{wavelength}!{control}${treatment}"
        except ValueError:
            line, treatment = sample, None
            baseline = f"{wavelength}!{control}"
        if baseline not in df.columns:
            baseline_cols = [col for col in df if col.startswith(baseline)]
            df[baseline] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
            df[baseline + "-STD"] = df[baseline_cols].std(axis=1)
            df[baseline + "-SEM"] = df[baseline_cols].sem(axis=1)
        sample_cols = [col for col in df if col.startswith(sample)]
        df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[sample + "-STD"] = df[sample_cols].std(axis=1)
        df[sample + "-SEM"] = df[sample_cols].sem(axis=1)
        df[sample + "-adjusted"] = df[sample] - df[baseline]
        df[sample + "-gaussian-error"] = (df[sample + "-SEM"] ** 2 + df[f"{baseline}-SEM"] ** 2) ** 0.5
        ax = df[sample + "-adjusted"].plot(figsize=(12, 8), yerr=df[sample + "-gaussian-error"], alpha=0.4,
                                           legend=False, grid=True, color=color)
        lines.append(Line2D([0], [0], color=color))
        if treatment:
            legends.append(f"{line} + {treatment} at {wavelength}nm, corrected for autofluorescence")
        else:
            legends.append(f"{line} at {wavelength}nm, corrected for autofluorescence")
        df[sample + "-adjusted"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                      ax=ax, grid=True, legend=True)

    ax.set_ylabel("Fluorescence Intensity")
    plt.legend(lines, legends)
    plt.show()


def ratio_plot(df, config, wavelengths, control, time_in_minutes=True):
    if time_in_minutes:
        minutes_index = df.index/60
        minutes_index.set_names("Time [min]", inplace=True)
        df.index = minutes_index

    legends = []
    lines = []
    ax = None
    for sample, color in config["plain"]:
        try:
            line, treatment = sample.split("$")
        except ValueError:
            line, treatment = sample, None
        for wavelength in wavelengths:
            wl_sample = f"{wavelength}!{sample}"
            sample_cols = [col for col in df if col.startswith(f"{wl_sample}")]
            df[f"{wl_sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
            df[f"{wl_sample}-STD"] = df[sample_cols].std(axis=1)
            df[f"{wl_sample}-SEM"] = df[sample_cols].sem(axis=1)

        df[f"{sample}-ratio"] = df[f"{wavelengths[0]}!{sample}"] / df[f"{wavelengths[1]}!{sample}"]
        df[f"{sample}-ratio-error"] = df[f"{sample}-ratio"] * (
                    (df[f"{wavelengths[0]}!{sample}-STD"] / df[f"{wavelengths[0]}!{sample}"]) ** 2 + (
                     df[f"{wavelengths[1]}!{sample}-STD"] / df[f"{wavelengths[1]}!{sample}"]) ** 2
                   ) ** .5
        ax = df[sample + "-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
                                        yerr=df[sample + "-ratio-error"], color=color)
        lines.append(Line2D([0], [0], color=color))
        if treatment:
            legends.append(f"ratio for {line} + {treatment}")
        else:
            legends.append(f"ratio for {line}")
        df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                   ax=ax, grid=True, legend=True)

    for wavelength in wavelengths:
        for sample, color in config["af"]:
            try:
                line, treatment = sample.split("$")
            except ValueError:
                line, treatment = sample, None

            if treatment:
                wl_sample = f"{wavelength}!{line}${treatment}"
                wl_baseline = f"{wavelength}!{control}${treatment}"
            else:
                wl_sample = f"{wavelength}!{line}"
                wl_baseline = f"{wavelength}!{control}"
            if wl_baseline not in df.columns:
                baseline_cols = [col for col in df if col.startswith(wl_baseline)]
                df[f"{wl_baseline}"] = df[baseline_cols].mean(axis=1)  # caluclate the new mean column
                df[f"{wl_baseline}-STD"] = df[baseline_cols].std(axis=1)
                df[f"{wl_baseline}-SEM"] = df[baseline_cols].sem(axis=1)
            sample_cols = [col for col in df if col.startswith(f"{wl_sample}")]
            df[f"{wl_sample}"] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
            df[f"{wl_sample}-STD"] = df[sample_cols].std(axis=1)
            df[f"{wl_sample}-SEM"] = df[sample_cols].sem(axis=1)
            df[f"{wl_sample}-adjusted"] = df[f"{wl_sample}"] - df[f"{wl_baseline}"]
            df[f"{wl_sample}-gaussian-error"] = (df[f"{wl_sample}-SEM"] ** 2 + df[f"{wl_baseline}-SEM"] ** 2) ** .5

    for sample, color in config["af"]:
        try:
            line, treatment = sample.split("$")
        except ValueError:
            line, treatment = sample, None
        df[f"{sample}-ratio"] = df[f"{wavelengths[0]}!{sample}-adjusted"] / df[f"{wavelengths[1]}!{sample}-adjusted"]
        df[f"{sample}-ratio-gaussian-error"] = df[f"{sample}-ratio"] * (
                    (df[f"{wavelengths[0]}!{sample}-gaussian-error"] / df[f"{wavelengths[0]}!{sample}"]) ** 2 + (
                     df[f"{wavelengths[1]}!{sample}-gaussian-error"] / df[f"{wavelengths[1]}!{sample}"]) ** 2
                   ) ** .5
        ax = df[sample + "-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
                                        yerr=df[sample + "-ratio-gaussian-error"], color=color)
        lines.append(Line2D([0], [0], color=color))
        if treatment:
            legends.append(f"ratio for {line} + {treatment}, corrected for autofluorescence")
        else:
            legends.append(f"ratio for {line}, corrected for autofluorescence")
        df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=color, markersize=4,
                                   ax=ax, grid=True, legend=True)
    plt.legend(labels=legends)
    plt.show()
