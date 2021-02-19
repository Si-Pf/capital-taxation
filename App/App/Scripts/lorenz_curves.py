from Scripts.plotstyle import plotstyle

import pandas as pd
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import DataTable
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.models import TableColumn
from bokeh.palettes import Category10
from bokeh.plotting import figure


def lorenz_tab(plot_dict):
    plot_dict = plot_dict["lorenz_curves"]

    def prepare_data():

        deciles = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
        weights = pd.Series(
            data=[0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.04, 0.01]
        )

        capital_income_tax = pd.Series(
            data=[0, 0, 0, 0, 0, 4, 15, 36, 52, 84, 167, 559, 13873]
        )  # from Bach & Buslei 2017 table 3-2
        capital_income = (capital_income_tax / 0.26375).round(2)

        income_tax = pd.Series(
            data=[0, 0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230]
        )  # from Bach & Buslei 2017 table 3-2

        total_income = pd.Series(
            data=[
                0,
                -868,
                4569,
                9698,
                14050,
                18760,
                23846,
                29577,
                36769,
                47676,
                63486,
                95899,
                350423,
            ]
        )  # from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"

        labor_income = total_income - capital_income

        net_income = total_income - capital_income_tax - income_tax

        total_income_share = (total_income * weights).cumsum() / (
            total_income * weights
        ).sum()
        capital_income_share = (capital_income * weights).cumsum() / (
            capital_income * weights
        ).sum()
        labor_income_share = (labor_income * weights).cumsum() / (
            labor_income * weights
        ).sum()
        net_income_share = (net_income * weights).cumsum() / (
            net_income * weights
        ).sum()

        income_share_dict = {
            "deciles": deciles,
            "total_income_share": total_income_share,
            "labor_income_share": labor_income_share,
            "capital_income_share": capital_income_share,
            "net_income_share": net_income_share,
        }

        raw_dict = {
            "deciles": deciles,
            "weights": weights,
            "capital_income_tax": capital_income_tax,
            "total_income": total_income,
            "capital_income": capital_income,
            "labor_income": labor_income,
            "net_income": net_income,
        }

        return ColumnDataSource(income_share_dict), ColumnDataSource(raw_dict)

    def make_plot(src, src_raw):
        p = figure(plot_width=800, plot_height=400, tooltips="$name: $y{0.00%} ",)

        lines = [
            "deciles",
            "total_income_share",
            "labor_income_share",
            "capital_income_share",
            "net_income_share",
        ]
        labels = [
            "Perfect equality",
            "Total income (pre tax)",
            "Labor income (pre tax)",
            "Capital income (pre tax)",
            "Total income (after tax)",
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
            )
        p.xaxis.tags = ["numeric"]

        plot = plotstyle(p, plot_dict)

        # Table to display source data

        columns = [
            TableColumn(field="deciles", title="Deciles"),
            TableColumn(field="total_income", title="Total income (before tax)"),
            TableColumn(field="labor_income", title="Labor income (before tax)"),
            TableColumn(field="capital_income", title="Capital income (before tax)"),
            TableColumn(field="net_income", title="Total income (after tax)"),
            TableColumn(field="weights", title="Decile weights"),
        ]

        data_table = DataTable(
            source=src_raw, columns=columns, width=800, height=350, selectable=False
        )

        return plot, data_table

    src, src_raw = prepare_data()

    plot, table = make_plot(src, src_raw)

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

    layout = column(plot, table_title, table, reference)

    tab = Panel(child=layout, title="Lorenz curves (Status Quo)")

    return tab
