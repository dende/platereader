class Plot:

    def __init__(self, df):
        self.df = df
        self.figsize = (12, 8)
        pass

    def plot_lines_with_errorbars(self, sample, error, color):
        return self.df[sample].plot(figsize=self.figsize, yerr=self.df[error], alpha=0.4, legend=False,
                                    grid=True, color=color)

    def plot_dots(self, sample, color, ax):
        return self.df[sample].plot(figsize=self.figsize, style=['o'], color=color, markersize=4,
                                    ax=ax, grid=True, legend=True)
