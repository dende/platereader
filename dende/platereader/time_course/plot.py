import matplotlib.pyplot as plt


def plot(df, config):

    legends = []
    ax = None
    for sample in config:  # the variable sample is first WT15, then CytroGFP2Orp1#1 and then SecrroGFP2Orp1#19
        wavelength, line, treatment = sample.split("$")
        sample_cols = [col for col in df if col.startswith(sample)]
        df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[sample + "-STD"] = df[sample_cols].std(axis=1)  # calculate the errors column
        df[sample + "-SEM"] = df[sample_cols].sem(axis=1)  # calculate the errors column
        ax = df[sample].plot(figsize=(12, 8), yerr=df[f"{sample}-STD"], alpha=0.4, legend=False, grid=True)
        legends.append(f"{line} + {treatment} at {wavelength}")
        df[sample].plot(figsize=(12, 8), style=['o'], color=ax.lines[-1].get_color(),
                        markersize=4, ax=ax, grid=True, legend=True)

    # average_columns = [f"{specimen}" for specimen in specimens]
    # error_columns = [f"{specimen}-STD" for specimen in specimens]
    #
    # errors = df[error_columns]
    # errors.columns = average_columns
    #
    # ax = df[average_columns].plot(figsize=(12, 8), yerr=errors, alpha=0.4, legend=False, grid=True)
    #
    # ax.set_ylabel("Fluorescence intensity")
    # ax.set_prop_cycle(None)
    # markerstyles = ['o'] * len(specimens)
    #
    # df[average_columns].plot(figsize=(12, 8), style=markerstyles, markersize=4, ax=ax,grid=True)
    #
    # if "legends" in config:
    #     ax.legend(config["legends"])
    #
    # if "limits" in config:
    #     ax.set_ylim(tuple(config['limits']['y']))
    # if "labels" in config:
    #     ax.set_xlabel(config['labels']['x'])
    # if 'ticks' in config:
    #     xticks = list(config['ticks']['x'].keys())
    #     xticklabels = list(config['ticks']['x'].values())
    #     ax.set_xticks(xticks)
    #     ax.set_xticklabels(xticklabels)
    #     ax.xaxis.set_minor_locator(MultipleLocator(config['ticks']['xminor']))
    #     ax.xaxis.grid(True, which='minor')

    plt.legend(labels=legends)
    plt.show()


def autofluorescence_plot(df, config, control):
    legends = []
    ax = None
    for sample in config:
        wavelength, line, treatment = sample.split("$")
        baseline = f"{wavelength}${control}${treatment}"
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
                                           legend=False, grid=True)
        legends.append(f"{line} {treatment} at {wavelength}nm, corrected for autofluorescence")
        df[sample + "-adjusted"].plot(figsize=(12, 8), style=['o'], color=ax.lines[-1].get_color(), markersize=4,
                                      ax=ax, grid=True, legend=True)
    plt.legend(labels=legends)
    plt.show()


def ratio_plot(df, config, wavelengths, control):
    pass

    legends = []
    ax = None
    for sample in config:
        line, treatment = sample.split("$")
        for wavelength in wavelengths:
            wl_sample = f"{wavelength}${sample}"
            wl_baseline = f"{wavelength}${control}${treatment}"
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

        df[f"{sample}-ratio"] = df[f"{wavelengths[0]}${sample}-adjusted"] / df[f"{wavelengths[1]}${sample}-adjusted"]
        df[f"{sample}-ratio-gaussian-error"] = df[f"{sample}-ratio"] * (
                    (df[f"{wavelengths[0]}${sample}-gaussian-error"] / df[f"{wavelengths[0]}${sample}"]) ** 2 + (
                     df[f"{wavelengths[1]}${sample}-gaussian-error"] / df[f"{wavelengths[1]}${sample}"]) ** 2
                   ) ** .5
        ax = df[sample + "-ratio"].plot(figsize=(12, 8), alpha=0.4, legend=False, grid=True,
                                        yerr=df[sample + "-ratio-gaussian-error"])
        legends.append(f"ratio for {line} + {treatment}")
        df[f"{sample}-ratio"].plot(figsize=(12, 8), style=['o'], color=ax.lines[-1].get_color(), markersize=4,
                                   ax=ax, grid=True, legend=True)
    plt.legend(labels=legends)
    plt.show()

    # if "ratio" in config:
    #     for specimen in config["ratio"]["mappings"]:
    #         df[f"{specimen}-ratio"] = df[f"{specimen} 400nm"] / df[f"{specimen} 482nm"]
    #         df[f"{specimen}-ratio-gaussian-error"] = df[f"{specimen}-ratio"] *
    #           ((df[f"{specimen} 400nm-gaussian-error"] / df[f"{specimen} 400nm"] )**2 +
    #           (df[f"{specimen} 482nm-gaussian-error"] / df[f"{specimen} 482nm"])**2)**(.5)
    #     ratio_columns = [f"{specimen}-ratio" for specimen in config['ratio']['mappings']]
    #     ratio_error_columns = [f"{specimen}-ratio-gaussian-error" for specimen in config['ratio']['mappings']]
    #
    #     ratio_erros = df[ratio_error_columns]
    #     ratio_erros.columns = ratio_columns
    #
    #     ax = df[ratio_columns].plot(figsize=(12, 8), yerr=ratio_erros, alpha=0.4, grid=True)
    #     ax.set_prop_cycle(None)
    #     df[ratio_columns].plot(figsize=(12, 8), style='o-', markersize=4, ax=ax, grid=True)
    #     if "limits" in config["ratio"]:
    #         ax.set_ylim(config["ratio"]["limits"]["y"])
    #
    #     ax.set_ylabel("roGFP2-Orp1 oxidation (I$_{400nm}$/I$_{482nm}$)")
    #     if "legends" in config["ratio"]:
    #         ax.legend(config["ratio"]["legends"])
    # if 'ticks' in config:
    #     xticks = list(config['ticks']['x'].keys())
    #     xticklabels = list(config['ticks']['x'].values())
    #     ax.set_xticks(xticks)
    #     ax.set_xticklabels(xticklabels)
    #     ax.xaxis.set_minor_locator(MultipleLocator(config['ticks']['xminor']))
    #     ax.xaxis.grid(True, which='minor')
    # if "labels" in config:
    #     ax.set_xlabel(config['labels']['x'])
    #
    # plt.show()
    #

