
from Scripts.plotstyle import plotstyle

import pandas as pd
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import FactorRange
from bokeh.models import LabelSet
from bokeh.models import LinearColorMapper
from bokeh.models import Panel
from bokeh.models.widgets import Slider
from bokeh.palettes import Category10
from bokeh.palettes import RdYlGn
from bokeh.plotting import figure
from bokeh.transform import factor_cmap


def behavioral_response(plot_dict):
    plot_dict1 = plot_dict["behavioral_response"]
    plot_dict2 = plot_dict["revenue_bevavior"]

    def prepare_data():

        deciles = [
            "1. Decile",
            "2. Decile",
            "3. Decile",
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

        delta_tax_burden_avg = pd.Series(
            data=[0, 0, 0, -3, -8, -10, -11, -11, -11, -10, 8, 439, -2]
        )  # from Bach & Buslei 2017 table 4-7
        delta_tax_burden = [
            0,
            0,
            -1,
            -12,
            -31,
            -41,
            -48,
            -49,
            -52,
            -23,
            13,
            171,
            -73,
        ]  # Aggregated impact based on Bach and Buslei 2017 Table 4-5
        number_of_taxpayers = (
            pd.Series(
                data=[
                    5768,
                    5354,
                    5273,
                    4584,
                    4005,
                    4028,
                    4188,
                    4407,
                    4502,
                    2235,
                    1715,
                    389,
                    46449,
                ]
            )
            * 1000
        )  # from Bach & Buslei 2017 table 3-2

        # Calculation for ETR impact
        total_income = pd.Series(
            data=[
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
                28922,
            ]
        )  # from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"
        capital_income_tax = pd.Series(
            data=[0, 0, 0, 0, 4, 15, 36, 52, 84, 167, 559, 13873, 163]
        )  # from Bach & Buslei 2017 table 3-2
        income_tax = pd.Series(
            data=[
                0,
                9,
                99,
                655,
                1927,
                3524,
                5412,
                7812,
                11850,
                18978,
                36095,
                159230,
                7870,
            ]
        )  # from Bach & Buslei 2017 table 3-2
        net_income = total_income - capital_income_tax - income_tax
        net_income_reform = net_income - delta_tax_burden_avg

        ETR_current = (total_income - net_income) / total_income
        ETR_reform = (total_income - net_income_reform) / total_income
        Delta_ETR = ETR_reform - ETR_current

        # Reform estimates
        ETI = pd.Series(data=range(201))  # Define range of plausible elasticities

        recovered_percent = pd.Series(data=range(101))

        delta_tax_base = {}
        data_full = pd.DataFrame(columns=ETI)

        # Calculate the changes for all deciles except the bottom 3 -> change is always 0 there
        for i in ETI:
            delta_tax_base[i] = total_income[3:] - total_income[3:] * (
                1 + Delta_ETR[3:] * (ETI[i] / 100)
            )

        for i in delta_tax_base.keys():
            data_full[i] = [
                {
                    "delta_tax_base": delta_tax_base[i].round(0),
                    "externalities": (
                        delta_tax_base[i] * (-1 * recovered_percent[j] / 100)
                    ).round(0),
                    "total": (
                        delta_tax_base[i] * (-1 * recovered_percent[j] / 100)
                        + delta_tax_base[i]
                    ).round(0),
                    "aggr_delta_after_eti": (
                        (
                            delta_tax_base[i] * (-1 * recovered_percent[j] / 100)
                            + delta_tax_base[i]
                        )
                        * number_of_taxpayers[3:]
                    )
                    / 1000000
                    + delta_tax_burden[3:],
                    "deciles": deciles[3:],
                    "offset": [
                        -32 if v < 0 else 2
                        for v in (
                            (
                                (
                                    delta_tax_base[i]
                                    * (-1 * recovered_percent[j] / 100)
                                    + delta_tax_base[i]
                                )
                                * number_of_taxpayers[3:]
                            )
                            / 1000000
                            + delta_tax_burden[3:]
                        )
                    ],
                }
                for j in recovered_percent
            ]

        return data_full

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

    data_full = prepare_data()


    src, src2 = make_dataset(100, 10, data_full)

    p, p2 = make_plot(src, src2)

    layout = column(ETI_selection, recovery_selection, p, p2)

    tab = Panel(child=layout, title="Behavioral responses (Reform)")

    return tab
