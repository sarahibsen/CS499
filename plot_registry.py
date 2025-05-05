from matplotlib import pyplot as plt
import seaborn as sns
##
class plot_registry:
    registered_plots = {}

    @classmethod
    def register(cls, name):
        def decorator(func):
            cls.registered_plots[name] = func
            return func
        return decorator

    @classmethod
    def get_plot(cls, name):
        return cls.registered_plots.get(name)

    @classmethod
    def get_all(cls):
        return list(cls.registered_plots.keys())


@plot_registry.register("Scatter Plot")
def scatter_plot(ax, x, y, **kwargs):
    ax.scatter(x, y)
    ax.set_title("Scatter Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")


    # Optional: trendline
    if kwargs.get("trendline", False) and len(x) == len(y):
        import numpy as np
        coeffs = np.polyfit(x, y, 1)
        poly_eq = np.poly1d(coeffs)
        ax.plot(x, poly_eq(x), color='red', linestyle='--', label="Trend Line")
        ax.legend()

@plot_registry.register("Vertical Bar Chart")
def vertical_bar_chart(ax, x, y, **kwargs):
    x_labels = [str(label) for label in x]  # Only here
    ax.bar(x_labels, y)
    ax.set_title("Vertical Bar Chart")


@plot_registry.register("Pie Chart")
def pie_chart(ax, x, y, **kwargs):
    # Convert all x-labels to strings to avoid type errors
    x_labels = [str(label) for label in x]
    ax.pie(y, labels=x_labels, autopct="%1.1f%%", startangle=140)
    ax.set_title("Pie Chart")


@plot_registry.register("Normal Distribution Curve")
def normal_distribution_curve(ax, x, y=None, label=None, **kwargs):
    sns.kdeplot(x, ax=ax, fill=True, label=label or "Distribution")
    ax.set_title("Normal Distribution")
    ax.set_xlabel("Value")
    ax.set_ylabel("Density")
    ax.legend()


@plot_registry.register("KDE Plot")
def kde_plot(ax, x, y=None, **kwargs):
    sns.kdeplot(x, ax=ax, fill=True)
    ax.set_title("KDE Plot")

@plot_registry.register("Histogram")
def histogram(ax, x, y=None, **kwargs):
    ax.hist(x, bins=30, alpha=0.7)
    ax.set_title("Histogram")

@plot_registry.register("Box Plot")
def box_plot(ax, x, y=None, **kwargs):
    sns.boxplot(x=x, ax=ax)
    ax.set_title("Box Plot")
