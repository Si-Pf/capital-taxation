from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import FactorRange
from bokeh.models import LabelSet
from bokeh.models import LinearColorMapper
from bokeh.models import Panel
from bokeh.models.widgets import Slider
from bokeh.palettes import Category10
from bokeh.palettes import RdYlGn
from bokeh.plotting import figure
from bokeh.transform import factor_cmap


def behavioral_response(plot_dict1, plot_dict2, data):
    def make_dataset(ETI, recovered_percent, data_full):
        selected_data = data_full[ETI][recovered_percent]
        factors = [
            (decile, effect)
            for decile in selected_data["deciles"]
            for effect in ["delta_tax_base", "externalities", "total"]
        ]
        change = sum(
            zip(
                selected_data["delta_tax_base"],
                selected_data["externalities"],
                selected_data["total"],
            ),
            (),
        )

        return (
            ColumnDataSource(
                data={
                    "factor": factors,
                    "change": change,
                    "label": [str(int(i)) for i in change],
                }
            ),
            ColumnDataSource(
                data={
                    "aggr_delta_after_eti": selected_data["aggr_delta_after_eti"],
                    "deciles": selected_data["deciles"],
                    "offset": selected_data["offset"],
                    "label": [
                        str(int(i)) for i in selected_data["aggr_delta_after_eti"]
                    ],
                }
            ),
        )

    def make_plot(src, src2):
        # plot 1
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=FactorRange(*src.data["factor"]),
            tooltips="@factor: @change{0€} €",
        )

        p.vbar(
            x="factor",
            top="change",
            width=0.8,
            source=src,
            fill_color=factor_cmap(
                "factor",
                palette=Category10[4][1:],
                factors=["delta_tax_base", "externalities", "total"],
                start=1,
                end=2,
            ),
            line_color=None,
        )

        labels = LabelSet(
            x="factor",
            y="change",
            text="label",
            source=src,
            render_mode="canvas",
            y_offset=-7,
        )

        p.add_layout(labels)

        p.xgrid.grid_line_color = None

        # Static styling
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1.4

        plot = plotstyle(p, plot_dict1)

        # Plot 2
        p2 = figure(
            plot_width=800,
            plot_height=400,
            y_range=src2.data["deciles"],
            x_range=[-180, 187],
            tooltips="@deciles: @aggr_delta_after_eti{0€} Mio.€",
        )

        labels2 = LabelSet(
            x="aggr_delta_after_eti",
            y="deciles",
            text="label",
            source=src2,
            x_offset="offset",
            y_offset=-10,
            render_mode="canvas",
        )

        color_mapper = LinearColorMapper(
            palette=RdYlGn[10],
            low=max(src2.data["aggr_delta_after_eti"]),
            high=min(src2.data["aggr_delta_after_eti"]),
        )

        p2.hbar(
            y="deciles",
            right="aggr_delta_after_eti",
            source=src2,
            height=0.8,
            color={"field": "aggr_delta_after_eti", "transform": color_mapper},
            line_color=None,
        )

        p2.add_layout(labels2)

        p2.xaxis.tags = ["numeric"]
        p2.yaxis.tags = ["categorical"]

        plot2 = plotstyle(p2, plot_dict2)

        return plot, plot2

    def update_plot(attr, old, new):
        ETI = int(ETI_selection.value * 100)
        recovered_percent = int(recovery_selection.value * 100)
        new_src, new_src2 = make_dataset(ETI, recovered_percent, data_full)
        src.data.update(new_src.data)
        src2.data.update(new_src2.data)

    ETI_selection = Slider(
        start=0, end=2, value=1, step=0.01, title="Elasticity of capital income"
    )
    recovery_selection = Slider(
        start=0,
        end=1,
        value=0.1,
        step=0.01,
        title="Recovered portion (through externalities)",
    )

    ETI_selection.on_change("value", update_plot)
    recovery_selection.on_change("value", update_plot)

    data_full = data

    src, src2 = make_dataset(100, 10, data_full)

    p, p2 = make_plot(src, src2)

    description = Div(text=plot_dict1["description"], width=1000,)

    layout = column(description, ETI_selection, recovery_selection, p, p2)

    tab = Panel(child=layout, title="Behavioral responses (Reform)")

    return tab
