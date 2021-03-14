from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.layouts import row
from bokeh.models import ColumnDataSource
from bokeh.models import DataTable
from bokeh.models import Div
from bokeh.models import LabelSet
from bokeh.models import LinearColorMapper
from bokeh.models import NumberFormatter
from bokeh.models import Panel
from bokeh.models import TableColumn
from bokeh.palettes import RdYlGn
from bokeh.plotting import figure


def tax_revenue(plot_dict, data):
    def make_plot(src):
        p = figure(
            plot_width=800,
            plot_height=400,
            y_range=src.data["deciles"],
            tooltips="@deciles: @delta_tax_burden{0€} Mio.€",
        )

        labels = LabelSet(
            x="delta_tax_burden",
            y="deciles",
            text="label",
            source=src,
            x_offset="offset",
            y_offset=-10,
            render_mode="canvas",
        )

        color_mapper = LinearColorMapper(
            palette=RdYlGn[10],
            low=max(src.data["delta_tax_burden"]) - 120,
            high=min(src.data["delta_tax_burden"]),
        )

        p.hbar(
            y="deciles",
            right="delta_tax_burden",
            source=src,
            height=0.8,
            color={"field": "delta_tax_burden", "transform": color_mapper},
            line_color=None,
        )

        # Table to display source data
        columns = [
            TableColumn(field="deciles", title="Deciles"),
            TableColumn(
                field="delta_tax_burden", title="Tax revenue change (in Million €)"
            ),
            TableColumn(
                field="Delta_ETR",
                title="Effective tax rate change (ΔETR)",
                formatter=NumberFormatter(format="0.0000%"),
            ),
        ]

        data_table = DataTable(source=src, columns=columns, width=800, height=350)

        p.add_layout(labels)

        p.xaxis.tags = ["numeric"]
        p.yaxis.tags = ["categorical"]

        plot = plotstyle(p, plot_dict)

        return plot, data_table

    src = ColumnDataSource(data)

    plot, table = make_plot(src)

    description = Div(text=plot_dict["description"], width=1000,)

    table_title = Div(text="""<b>Source data</b>""", width=800, height=20)
    reference = Div(
        text="""Data from <a href="http://hdl.handle.net/10419/172793">Bach and Buslei 2017</a>
        table 4-5 and own calculations. Simulated scenario where the capital income tax is
        included in the progressive income taxation, itemized deductions for capital income and
        "Teileinkünfteverfahren" for dividends are reintroduced.""",
        width=800,
        height=80,
    )

    layout = row(column(description, plot, table_title, table, reference))

    tab = Panel(child=layout, title="Tax revenues (Reform)")

    return tab
