from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import DataTable
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.models import TableColumn
from bokeh.palettes import Category10
from bokeh.plotting import figure


def lorenz_tab2(plot_dict, data):
    def make_plot(src, src_raw):
        p = figure(plot_width=800, plot_height=400, tooltips="$name: $y{0.00%} ",)
        lines = [
            "deciles",
            "total_income_share",
            "net_income_share",
            "net_income_share_simulated",
        ]
        labels = [
            "Perfect equality",
            "Total income (pre tax)",
            "Total income (after tax status quo)",
            "Total income (after tax simulated reform)",
        ]
        colors = Category10[len(lines)]

        for i in range(len(lines)):
            p.line(
                "deciles",
                lines[i],
                source=src,
                line_color=colors[i],
                legend_label=labels[i],
                alpha=0.8,
                muted_color=colors[i],
                muted_alpha=0.2,
                name=labels[i],
            )
            p.circle(
                "deciles",
                lines[i],
                source=src,
                fill_color=colors[i],
                legend_label=labels[i],
                line_color=None,
                name=labels[i],
                alpha=0.8,
                muted_color=colors[i],
                muted_alpha=0.2,
            )

        p.xaxis.tags = ["numeric"]

        plot = plotstyle(p, plot_dict)

        # Table to display source data

        columns = [
            TableColumn(field="deciles", title="Deciles"),
            TableColumn(field="total_income", title="Total income (before tax)"),
            TableColumn(
                field="net_income", title="Total income (after tax status quo)"
            ),
            TableColumn(
                field="net_income_simulated", title="Total income (after tax reform)"
            ),
            TableColumn(field="weights", title="Decile weights"),
        ]

        data_table = DataTable(
            source=src_raw,
            columns=columns,
            width=800,
            height=350,
            selectable=False,
            autosize_mode="fit_columns",
        )

        return plot, data_table

    src, src_raw = (
        ColumnDataSource(data["income_share_dict"]),
        ColumnDataSource(data["raw_dict"]),
    )

    plot, table = make_plot(src, src_raw)

    description = Div(text=plot_dict["description"], width=1000,)

    table_title = Div(
        text="""<b>Source data: Average (taxable) income per decile (in €)</b>""",
        width=800,
        height=20,
    )
    reference = Div(
        text="""Data from <a href="http://hdl.handle.net/10419/172793">Bach and Buslei 2017</a>
        table 3-2 and own calculations. Columns show average taxable income per decile in Euro.
        Capital income calculated as avg. capital tax / 0.26375.""",
        width=800,
        height=80,
    )

    layout = column(description, plot, table_title, table, reference)

    tab = Panel(child=layout, title="Lorenz curves (Reform)")

    return tab
