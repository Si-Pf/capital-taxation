from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import DataTable
from bokeh.models import Div
from bokeh.models import Label
from bokeh.models import Legend
from bokeh.models import Panel
from bokeh.models import TableColumn
from bokeh.models.widgets import Slider
from bokeh.plotting import figure


def individual_view(plot_dict, data):
    def make_dataset(LI, CI, data_full):
        Total_income_index = int((CI + LI) / 2)

        selected_data_li = {
            i: [data_full[i][j][LI] for j in range(6)] for i in data_full["LI_list"]
        }
        selected_data_ci = {
            i: [data_full[i][j][CI] for j in range(6)] for i in data_full["CI_list"]
        }
        selected_data_t = {
            i: [data_full[i][j][Total_income_index] for j in range(6)]
            for i in data_full["Total_list"]
        }

        selected_data_t.update(selected_data_li)
        selected_data_t.update(selected_data_ci)
        reordered_dict = {k: selected_data_t[k] for k in data_full["Final_order"]}
        reordered_dict["x_range"] = data_full["x_range"]

        return ColumnDataSource(reordered_dict)

    def make_plot(src):
        p = figure(
            plot_width=1000,
            plot_height=400,
            x_range=src.data["x_range"],
            y_range=(0, 360000),
            tooltips="$name: @$name{0€} €",
        )

        y_list = src.column_names
        y_list.remove("x_range")

        # Define static styling options
        hatch_pattern = [
            " ",
            " ",
            "/",
            " ",
            " ",
            " ",
            "/",
            "/",
            "/",
            " ",
            " ",
            "/",
            " ",
            "/",
        ]
        color = [
            "#1f77b4",
            "#aec7e8",
            "#ff7f0e",
            "#ff7f0e",
            "#ffbb78",
            "#ffbb78",
            "#ffbb78",
            "#ffbb78",
            "#2ca02c",
            "#2ca02c",
            "#98df8a",
            "#98df8a",
            "#2ca02c",
            "#2ca02c",
        ]
        renderers = p.vbar_stack(
            y_list,
            x="x_range",
            width=0.5,
            source=src,
            color=color,
            hatch_pattern=hatch_pattern,
            line_color=None,
        )

        labels = [
            "Capital income",
            "Labor income",
            "Capital income deduction",
            "Taxable capital income",
            "Taxable labor income",
            "Taxable total income",
            "Labor income deduction",
            "Total income deduction",
            "Capital income tax",
            "Net capital income",
            "Net labor income",
            "Labor income tax",
            "Net total income",
            "Total income tax",
        ]

        legend = Legend(
            items=[(labels[count], [r]) for count, r in enumerate(renderers)],
            location="center",
        )

        p.add_layout(legend, "right")

        # Table to display source data

        columns = [TableColumn(field="x_range", title="Bar")] + [
            TableColumn(field=i, title=i) for i in y_list
        ]

        data_table = DataTable(
            source=src,
            columns=columns,
            width=900,
            height=200,
            index_position=None,
            autosize_mode="fit_columns",
        )

        plot = plotstyle(p, plot_dict)

        return plot, data_table

    def update_plot(attr, old, new):
        LI = int(LI_selection.value / 500)
        CI = int(CI_selection.value / 500)
        new_src = make_dataset(LI, CI, data_full)

        src.data.update(new_src.data)

        # Dynamic update for the net income labels
        Net_income_s.text = (
            "Net income: " + str(int(src.data["NLI"][2] + src.data["NCI"][2])) + "€"
        )
        Net_income_s.y = (
            int(
                src.data["NLI"][2]
                + src.data["NCI"][2]
                + src.data["CT"][2]
                + src.data["LT"][2]
            )
            + 10000
        )

        Net_income_i.text = "Net income: " + str(int(src.data["NI"][5])) + "€"
        Net_income_i.y = int(src.data["NI"][5] + src.data["T"][5]) + 10000

    # Sliders for dynamic update
    LI_selection = Slider(
        start=0, end=250000, value=60000, step=1000, title="Labor income (€)"
    )
    CI_selection = Slider(
        start=0, end=100000, value=10000, step=500, title="Capital income (€)"
    )

    CI_selection.on_change("value", update_plot)
    LI_selection.on_change("value", update_plot)

    data_full = data

    src = make_dataset(60, 20, data_full)

    p, table = make_plot(src)

    # Net income Labels
    Net_income_s = Label(x=1.85, y=60000, text="Net income: 41909€")
    Net_income_i = Label(x=4.75, y=60000, text="Net income: 41440")
    p.add_layout(Net_income_s)
    p.add_layout(Net_income_i)

    table_title = Div(
        text="""<b>Source data: Individual mechanical impact of the reform (in €)</b>""",
        width=800,
        height=20,
    )

    description = Div(text=plot_dict["description"], width=1000,)

    reference = Div(
        text="""Data from own calculations. Assumed is a uniform deduction of 20% of
        labor income (status quo) and 20% of total income (reform). The tax amounts
        are calculated with <a href="https://gettsim.readthedocs.io/en/stable/">GETTSIM</a>.""",
        width=800,
        height=80,
    )

    layout = column(
        description, LI_selection, CI_selection, p, table_title, table, reference
    )

    tab = Panel(child=layout, title="Net incomes")

    return tab
