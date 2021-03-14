from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import BasicTicker
from bokeh.models import BooleanFilter
from bokeh.models import CDSView
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.models import Panel
from bokeh.models import RadioButtonGroup
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from bokeh.transform import transform


def parameter_heatmap_tab(plot_dict, data):
    def setup_plot(src_heatmap):

        colors = Turbo256[80:220]
        colors = list(colors)
        colors.reverse()

        mapper = LinearColorMapper(
            palette=colors,
            low=min(src_heatmap.data["total"]),
            high=max(src_heatmap.data["total"]),
        )

        # Actual figure setup
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=(0, 1),
            y_range=(0, 2),
            tools="save",
        )

        p.rect(
            x="Recovered_portion",
            y="Elasticity",
            width=0.05,
            height=0.01,
            source=src_heatmap,
            line_color=None,
            fill_color=transform("total", mapper),
        )

        booleans = [
            True if total > -0.5 and total < 0.5 else False
            for total in src_heatmap.data["total"]
        ]
        view = CDSView(source=src_heatmap, filters=[BooleanFilter(booleans)])
        p.circle(
            x="Recovered_portion",
            y="Elasticity",
            source=src_heatmap,
            view=view,
            fill_color="black",
            line_color=None,
            name="circle",
        )

        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=20),
            formatter=NumeralTickFormatter(format="0€"),
            label_standoff=12,
            title="Reform revenue (in Mio. €)",
        )
        p.add_layout(color_bar, "right")

        p.xaxis.tags = ["numeric"]

        plot = plotstyle(p, plot_dict)

        return plot

    def update_plot(attr, old, new):
        circle = p.select({"name": "circle"})
        src_heatmap.data["total"] = [
            i[radio_button.active + 3] for i in src_heatmap.data["aggr_delta_after_eti"]
        ]
        booleans = [
            True if total > -0.5 and total < 0.5 else False
            for total in src_heatmap.data["total"]
        ]
        circle.view.filters[0] = BooleanFilter(booleans)

    src_heatmap = ColumnDataSource(data)

    # Radio button for selecting the decile
    deciles = [
        "4. Decile",
        "5. Decile",
        "6. Decile",
        "7. Decile",
        "8. Decile",
        "9. Decile",
        "91-95%",
        "96-99%",
        "Top 1%",
        "Total",
    ]
    radio_button = RadioButtonGroup(labels=deciles, active=9)

    radio_button.on_change("active", update_plot)

    p = setup_plot(src_heatmap)

    description = Div(text=plot_dict["description"], width=1000,)

    layout = column(description, radio_button, p)

    tab = Panel(child=layout, title="Behavioral paremeter heatmap")

    return tab
