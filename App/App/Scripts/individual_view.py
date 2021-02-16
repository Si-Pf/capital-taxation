from Scripts.plotstyle import plotstyle

import numpy as np
import pandas as pd
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Label
from bokeh.models import Panel
from bokeh.models import Div
from bokeh.models import DataTable, TableColumn
from bokeh.models.widgets import Slider
from bokeh.plotting import figure
from gettsim import set_up_policy_environment
from gettsim.taxes.eink_st import st_tarif



def individual_view(plot_dict):
    plot_dict = plot_dict["individual_view"]

    def prepare_data():

        LI = pd.Series(data=range(0,2500001))  # Labor Income
        CI = pd.Series(data=range(0,1000001))  # Capital Income
        #np.linspace(-1, 300001, 300001)
        LD = 0.2 * LI  # To do add slider?
        TTI = LI + CI  # Total Income
        TD = 0.2 * TTI  # To do add realistic assumptions
        TI = TTI - TD  # taxable income

        # Calculate variables separated taxes
        TLI = LI - LD  # taxable labor income

        # Get relevant policy params from GETTSIM
        policy_params, policy_functions = set_up_policy_environment(2020)
        # labor_income = pd.Series(data=[LI])
        # integrated_income = pd.Series(data=[LI+CI])
        Tau_flat = (
            st_tarif(TLI, policy_params["eink_st"]) / TLI
        ).fillna(0).round(2)  # Income tax rate - flat

        Tau_integrated = (
            st_tarif(TI, policy_params["eink_st"]) / TI
        ).fillna(0).round(2)  # Income tax rate - integrated
        
        CD = pd.Series(
            data=[policy_params["eink_st_abzuege"]["sparerpauschbetrag"]] * len(LI)
        )  # Capital income deductions

        CTau = policy_params["abgelt_st"]["abgelt_st_satz"]  # Capital income tax rate

        TCI = CI - CD  # taxable capital income
        TCI[TCI < 0] = 0  # replace negative taxable income
        # Calculate variables integrated taxes
        # D = d*(LI+CI) #Dedcutions

        T = (TI * Tau_integrated)  # Total tax

        # taxable capital income
        LT = (TLI * Tau_flat).round(2)  # Labor income tax
        CT = TCI * CTau  # Capital income tax

        # Net incomes
        NCI = TCI - CT  # Capital
        NLI = (TLI - LT).round(2)  # Labor
        NI = (TI - T).round(2) # Total

        # blank placeholder
        B = [0] * len(LI)

        # columns = [CI,LI,CD,LD,TCI,TLI,CT,LT,NCI,NLI,NI,T,TI]

        data_full = {
            "x_range": [
                "Gross income (S)",
                "Taxable income (S)",
                "Net income (S)",
                "Gross income (R)",
                "Taxable income (R)",
                "Net income (R)",
            ],
            "CI": [CI, B, B, CI, B, B],
            "LI": [LI, B, B, LI, B, B],
            "TI": [B, B, B, B, TI, B],
            "NI": [B, B, B, B, B, NI],
            "T": [B, B, B, B, B, T],
            "CD": [B, CD, CD, B, B, B],
            "LD": [B, LD, B, B, B, B],
            "TCI": [B, TCI, B, B, B, B],
            "TLI": [B, TLI, B, B, B, B],
            "CT": [B, B, CT, B, B, B],
            "LT": [B, B, LT, B, B, B],
            "NCI": [B, B, NCI, B, B, B],
            "NLI": [B, B, NLI, B, B, B],
            "TD": [B, B, B, B, TD, B],
            "LI_list": ["LI", "TLI", "LT", "NLI", "LD"],
            "CI_list": ["CI", "CD", "TCI", "CT", "NCI"],
            "Total_list": ["TI", "NI", "T", "TD"],
            "Final_order": [
                "CI",
                "LI",
                "CD",
                "TCI",
                "TLI",
                "TI",
                "LD",
                "TD",
                "CT",
                "NCI",
                "NLI",
                "LT",
                "NI",
                "T",
            ],
        }

        return data_full

    def make_dataset(LI, CI, data_full):
        Total_income_index, selected_data = int((CI + LI) / 2), {}

        # Parameters depending on LI only:

        for i in data_full["LI_list"]:
            selected_data[i] = [data_full[i][j][LI] for j in range(6)]

        # Parameters depending on CI only:
        for i in data_full["CI_list"]:
            selected_data[i] = [data_full[i][j][CI] for j in range(6)]

        # Parameters depending on TI & LI:
        for i in data_full["Total_list"]:
            selected_data[i] = [data_full[i][j][Total_income_index] for j in range(6)]

        reordered_dict = {k: selected_data[k] for k in data_full["Final_order"]}
        reordered_dict["x_range"] = data_full["x_range"]

        return ColumnDataSource(reordered_dict)

    def make_plot(src):
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=src.data["x_range"],
            y_range=(0, 360000),
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
        p.vbar_stack(
            y_list,
            x="x_range",
            width=0.5,
            source=src,
            color=color,
            hatch_pattern=hatch_pattern,
            legend_label=y_list,
            line_color=None,
        )
        p.legend.orientation = "horizontal"

        # Table to display source data
        
        columns = [TableColumn(field="x_range",  title = "Bar", width=None)]+[TableColumn(field=i,  title = i, width=None) for i in y_list
                
        ]

        data_table = DataTable(source=src, columns=columns, width=900, height=200, index_position=None, autosize_mode="fit_columns")

        plot = plotstyle(p, plot_dict)

        return plot, data_table

    def update_plot(attr, old, new):
        LI = LI_selection.value
        CI = CI_selection.value
        new_src = make_dataset(LI, CI, data_full)

        src.data.update(new_src.data)
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

    LI_selection = Slider(
        start=0, end=250000, value=60000, step=1000, title="Labor income (€)"
    )
    CI_selection = Slider(
        start=0, end=100000, value=10000, step=500, title="Capital income (€)"
    )

    CI_selection.on_change("value", update_plot)
    LI_selection.on_change("value", update_plot)

    data_full = prepare_data()

    src = make_dataset(60000, 10000, data_full)

    p, table = make_plot(src)

    Net_income_s = Label(x=1.85, y=60000, text="Net income: 41909€")
    Net_income_i = Label(x=4.75, y=60000, text="Net income: 41440")
    p.add_layout(Net_income_s)
    p.add_layout(Net_income_i)

    table_title = Div(text="""<b>Source data</b>""",width=800, height=20)

    reference = Div(text="""Data from own calculations. Assumed is a uniform deduction of 20% of labor income
                         (status quo) and 20% of total income (reform). The tax amounts are calculated with GETTSIM.""",
                         width=800, height=80)

    layout = column(LI_selection, CI_selection, p, table_title, table, reference)

    tab = Panel(child=layout, title="Net incomes")

    return tab
