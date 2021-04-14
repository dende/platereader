import matplotlib.pyplot as plt


def plot(df, plain_plots):

    legends = []
    ax = None
    for sample in plain_plots:  # the variable specimen is first WT15, then CytroGFP2Orp1#1 and then SecrroGFP2Orp1#19
        wavelength, line, treatment = sample.split("$")
        sample_cols = [col for col in df if col.startswith(sample)]
        df[sample] = df[sample_cols].mean(axis=1)  # caluclate the new mean column
        df[sample + "-STD"] = df[sample_cols].std(axis=1)  # calculate the errors column
        df[sample + "-SEM"] = df[sample_cols].sem(axis=1)  # calculate the errors column
        ax = df[sample].plot(figsize=(12, 8), yerr=df[f"{sample}-STD"], alpha=0.4, legend=False, grid=True)
        legends.append(f"{line} + {treatment} at {wavelength}")
        df[sample].plot(figsize=(12, 8), style=['o'], color=ax.lines[-1].get_color(),
                        markersize=4, ax=ax, grid=True, legend=True)

    plt.legend(labels=legends)
    plt.show()

#         df[specimen] = df[[f"{specimen}-{i}" for i in range(1, repetitions + 1)]].mean(axis=1)
#         df[specimen + "-STD"] = df[[f"{specimen}-{i}" for i in range(1, repetitions + 1)]].std(axis=1)
#         df[specimen + "-SEM"] = df[[f"{specimen}-{i}" for i in range(1, repetitions + 1)]].sem(axis=1)
#
#     average_columns = [f"{specimen}" for specimen in specimens]
#     error_columns = [f"{specimen}-STD" for specimen in specimens]
#
#     errors = df[error_columns]
#     errors.columns = average_columns
#
#     ax = df[average_columns].plot(figsize=(12, 8), yerr=errors, alpha=0.4, legend=False, grid=True)
#
#     ax.set_ylabel("Fluorescence intensity")
#     ax.set_prop_cycle(None)
#     markerstyles = ['o'] * len(specimens)
#
#     df[average_columns].plot(figsize=(12, 8), style=markerstyles, markersize=4, ax=ax,grid=True)
#
#     if "legends" in config:
#         ax.legend(config["legends"])
#
#     if "limits" in config:
#         ax.set_ylim(tuple(config['limits']['y']))
#     if "labels" in config:
#         ax.set_xlabel(config['labels']['x'])
#     if 'ticks' in config:
#         xticks = list(config['ticks']['x'].keys())
#         xticklabels = list(config['ticks']['x'].values())
#         ax.set_xticks(xticks)
#         ax.set_xticklabels(xticklabels)
#         ax.xaxis.set_minor_locator(MultipleLocator(config['ticks']['xminor']))
#         ax.xaxis.grid(True, which='minor')
#
#     plt.show()
#
#
# def autofluorescence_plot(df, config):
#     repetitions = config['repetitions']
#     for sensor, baseline in config['mappings'].items():
#             df[sensor] = df[[f"{sensor}-{i}" for i in range(1, repetitions + 1)]].mean(axis=1)
#             df[sensor + "-STD"] = df[[f"{sensor}-{i}" for i in range(1, repetitions + 1)]].std(axis=1)
#             df[sensor + "-SEM"] = df[[f"{sensor}-{i}" for i in range(1, repetitions + 1)]].sem(axis=1)
#             if baseline != None:
#                 df[baseline] = df[[f"{baseline}-{i}" for i in range(1, repetitions + 1)]].mean(axis=1)
#                 df[baseline + "-STD"] = df[[f"{baseline}-{i}" for i in range(1, repetitions + 1)]].std(axis=1)
#                 df[baseline + "-SEM"] = df[[f"{baseline}-{i}" for i in range(1, repetitions + 1)]].sem(axis=1)
#
#             if baseline == None:
#                 df[sensor + "-adjusted"] = df[sensor]
#                 df[sensor + "-gaussian-error"] = df[sensor + "-SEM"]
#             else:
#                 df[sensor + "-adjusted"] = df[sensor] - df[baseline]
#                 df[sensor + "-gaussian-error"] = (df[sensor + "-SEM"] ** 2 + df[baseline + "-SEM"] ** 2) ** (0.5)
#
#     adjusted_sensor_columns = [f"{sensor}-adjusted" for sensor, baseline in config['mappings'].items()]
#     adjusted_error_columns = [f"{sensor}-gaussian-error" for sensor, baseline in config['mappings'].items()]
#
#     adjusted_errors = df[adjusted_error_columns]
#     adjusted_errors.columns = adjusted_sensor_columns
#
#     ax = df[adjusted_sensor_columns].plot(figsize=(12, 8), yerr=adjusted_errors, alpha=0.4, grid=True)
#     ax.set_ylabel("Fluorescence intensity")  # set the label for the y-axis
#     ax.set_prop_cycle(None)  # reset the colors
#     markerstyles = ['o'] * len(config['mappings'])  # let each marker be a big dot
#     df[adjusted_sensor_columns].plot(figsize=(12, 8), style=markerstyles, markersize=4, ax=ax, grid=True)
#     if "legends" in config:
#         ax.legend(config["legends"])
#     if 'ticks' in config:
#         xticks = list(config['ticks']['x'].keys())
#         xticklabels = list(config['ticks']['x'].values())
#         ax.set_xticks(xticks)
#         ax.set_xticklabels(xticklabels)
#         ax.xaxis.set_minor_locator(MultipleLocator(config['ticks']['xminor']))
#         ax.xaxis.grid(True, which='minor')
#     if "labels" in config:
#         ax.set_xlabel(config['labels']['x'])
#
#     plt.show()
#
#     if "ratio" in config:
#         for specimen in config["ratio"]["mappings"]:
#             df[f"{specimen}-ratio"] = df[f"{specimen} 400nm"] / df[f"{specimen} 482nm"]
#             df[f"{specimen}-ratio-gaussian-error"] = df[f"{specimen}-ratio"] *
#               ((df[f"{specimen} 400nm-gaussian-error"] / df[f"{specimen} 400nm"] )**2 +
#               (df[f"{specimen} 482nm-gaussian-error"] / df[f"{specimen} 482nm"])**2)**(.5)
#         ratio_columns = [f"{specimen}-ratio" for specimen in config['ratio']['mappings']]
#         ratio_error_columns = [f"{specimen}-ratio-gaussian-error" for specimen in config['ratio']['mappings']]
#
#         ratio_erros = df[ratio_error_columns]
#         ratio_erros.columns = ratio_columns
#
#         ax = df[ratio_columns].plot(figsize=(12, 8), yerr=ratio_erros, alpha=0.4, grid=True)
#         ax.set_prop_cycle(None)
#         df[ratio_columns].plot(figsize=(12, 8), style='o-', markersize=4, ax=ax, grid=True)
#         if "limits" in config["ratio"]:
#             ax.set_ylim(config["ratio"]["limits"]["y"])
#
#         ax.set_ylabel("roGFP2-Orp1 oxidation (I$_{400nm}$/I$_{482nm}$)")
#         if "legends" in config["ratio"]:
#             ax.legend(config["ratio"]["legends"])
#     if 'ticks' in config:
#         xticks = list(config['ticks']['x'].keys())
#         xticklabels = list(config['ticks']['x'].values())
#         ax.set_xticks(xticks)
#         ax.set_xticklabels(xticklabels)
#         ax.xaxis.set_minor_locator(MultipleLocator(config['ticks']['xminor']))
#         ax.xaxis.grid(True, which='minor')
#     if "labels" in config:
#         ax.set_xlabel(config['labels']['x'])
#
#     plt.show()
#
#
# def main():
#     for config_name, filtered_config in get_configs(['mean_plot_WT3', 'mean_plot_secr3']).items():
#         filename = filtered_config['filename']
#         df = pd.read_csv(f"{time_course_dir}/{filename}").set_index(x_axis_column)
#         errorplot(df, filtered_config)
#
# #    autofluorescence_config = config['autofluorescence']
# #   filename = autofluorescence_config['filename']
# #   df = pd.read_csv(f"{time_course_dir}/{filename}").set_index(x_axis_column)
# #   autofluorescence_plot(df, autofluorescence_config)
#
#
#     autofluorescence_config = config['autofluorescence3']
#     filename = autofluorescence_config['filename']
#     df = pd.read_csv(f"{time_course_dir}/{filename}").set_index(x_axis_column)
#     autofluorescence_plot(df, autofluorescence_config)
#
#
# #    autofluorescence_config = config['autofluorescence3']
# #   filename = autofluorescence_config['filename']
# #   df = pd.read_csv(f"{time_course_dir}/{filename}").set_index(x_axis_column)
# #   autofluorescence_plot(df, autofluorescence_config)
