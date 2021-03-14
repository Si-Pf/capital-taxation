from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import BasicTicker
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import HoverTool
from bokeh.models import LabelSet
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.models import Panel
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from bokeh.transform import transform


def heatmap_tab(plot_dict, data):
    def setup_plot(src_heatmap, src_household, line_source_dict):
        colors = Turbo256[145:256]
        colors = list(colors)
        mapper = LinearColorMapper(
            palette=colors,
            low=min(src_heatmap.data["Change to tax burden"]),
            high=max(src_heatmap.data["Change to tax burden"]),
        )

        # Actual figure setup
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=(0, 310000),
            y_range=(0, 100000),
            tools="save",
        )

        p.rect(
            x="Labor income",
            y="Capital income",
            width=3000,
            height=1000,
            source=src_heatmap,
            line_color=None,
            fill_color=transform("Change to tax burden", mapper),
        )

        p.scatter(
            x="labor_income", y="capital_income", source=src_household, color="black"
        )

        labels = LabelSet(
            x="labor_income",
            y="capital_income",
            text="deciles",
            x_offset=-15,
            y_offset=5,
            source=src_household,
        )

        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=20),
            formatter=NumeralTickFormatter(format="0€"),
            label_standoff=12,
            title="Impact (in €)",
        )

        p.add_layout(color_bar, "right")
        p.add_layout(labels)

        for i in line_source_dict.keys():
            i = p.line(
                x="Labor income",
                y="Capital income",
                source=line_source_dict[i],
                line_width=1,
                line_color="grey",
                name=str(i),
            )

        hover = HoverTool(
            tooltips=[
                ("Impact to tax burden", "@{Change to tax burden}{0€} €"),
                ("Taxable labor income", "$x{0€} €"),
                ("Taxable capital income", "$y{0€} €"),
            ],
            names=[str(i) for i in line_source_dict.keys()],
        )
        p.add_tools(hover)

        p.xaxis.tags = ["numeric"]

        plot = plotstyle(p, plot_dict)

        return plot

    src_heatmap, src_household = (
        ColumnDataSource(data["heatmap_source"]),
        ColumnDataSource(data["household_dict"]),
    )

    # Build the data sources for the contour lines
    line_source_dict = {}
    for i in range(-1, 14):
        line_source_dict[i] = ColumnDataSource(
            data["heatmap_source"][
                data["heatmap_source"]["Change to tax burden"].between(
                    0 + (i) * 1500, 75 + (i) * 1500
                )
            ]
        )

    p = setup_plot(src_heatmap, src_household, line_source_dict)

    description = Div(text=plot_dict["description"], width=1000,)

    layout = column(description, p)

    tab = Panel(child=layout, title="Household heatmap (Reform)")

    return tab
