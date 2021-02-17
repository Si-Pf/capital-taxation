import pandas as pd
import numpy as np
from math import pi


from bokeh.models import BasicTicker
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.models import Slider
from bokeh.models import Panel
from bokeh.models import LabelSet
from bokeh.palettes import Magma256, Turbo256
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.layouts import column


from gettsim import set_up_policy_environment
from gettsim.taxes.eink_st import st_tarif

from Scripts.plotstyle import plotstyle

def heatmap_tab(plot_dict):
    plot_dict = plot_dict["Impact_heatmap"]

    def prepare_data():
        LI = pd.Series(data=np.linspace(0, 310000, 250)) # Labor Income
        CI = pd.Series(data=np.linspace(0, 100000, 250)) # Capital Income
        TI= LI+CI # Total Income

        #Get relevant policy params from GETTSIM
        policy_params, policy_functions = set_up_policy_environment(2020)
        Tau_flat = (st_tarif(LI,policy_params["eink_st"])/LI) # Income tax rate - flat
        #Tau_integrated = (st_tarif(TI,policy_params["eink_st"])/TI) # Income tax rate - integrated
        CD = policy_params["eink_st_abzuege"]["sparerpauschbetrag"] 
        CTau = policy_params["abgelt_st"]["abgelt_st_satz"] # Capital income tax rate

        TLI = LI # taxable labor income
        TCI = CI-CD # taxable capital income
        TCI[TCI<0]=0 # replace negative taxable income
        # taxable capital income
        LT = TLI*Tau_flat # Labor income tax
        CT = TCI*CTau # Capital income tax  
        TT = LT+CT # Total tax burden

        heatmap_df = pd.DataFrame(columns=LI)

        # Iterate through LI and CI combinations for separate taxes
        for i in range(len(LI)):
            this_column = heatmap_df.columns[i]
            e = pd.Series(data=[LI[i]] * len(LI))
            c = e+CI
            heatmap_df[this_column] = (st_tarif(c,policy_params["eink_st"]))-(st_tarif(e,policy_params["eink_st"])+CT)
            
        heatmap_df.index = CI

        heatmap_source = pd.DataFrame(
        heatmap_df.stack(), columns=["Change to tax burden"]
        ).reset_index()
        heatmap_source.columns = ["Capital income", "Labor income", "Change to tax burden"]

        # Data to show where average household per decile is located in heatmap
        deciles = ["","","","","","","","","","P90","P95","P99","P100"]
        capital_income_tax = pd.Series(data=[0,0,0,0,0,4,15,36,52,84,167,559,13873]) # from Bach & Buslei 2017 table 3-2
        capital_income = (capital_income_tax/0.26375)
        total_income = pd.Series(data=[0,-868,4569,9698,14050,18760,23846,29577,36769,47676,63486,95899,350423]) #from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"
        labor_income = total_income-capital_income

        household_dict = {"deciles":deciles,
        "capital_income":capital_income,
        "labor_income":labor_income}

        # Data for heatmap hight lines

        line_source_dict = {}
        for i in range(-1,14):
            line_source_dict[i] = ColumnDataSource(heatmap_source[heatmap_source["Change to tax burden"].between(0+(i)*1500,75+(i)*1500)])


        return ColumnDataSource(heatmap_source), ColumnDataSource(household_dict), line_source_dict

    def setup_plot(src_heatmap, src_household, line_source_dict):
        colors = Turbo256[145:256]
        colors = list(colors)
        #colors.reverse()
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

        p.scatter(x="labor_income",y="capital_income", source=src_household, color = "black")
       

        labels = LabelSet(x="labor_income",y="capital_income", text="deciles", x_offset=-15, y_offset=5, source=src_household)


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
            p.line(x="Labor income", y="Capital income",source=line_source_dict[i], line_width=1, line_color="grey")

        p.xaxis.tags=["numeric"]

        plot = plotstyle(p,plot_dict)

        return plot
    
    src_heatmap, src_household, line_source_dict = prepare_data()

    p = setup_plot(src_heatmap, src_household, line_source_dict)

    layout = column(p)

    

    tab = Panel(child = layout, title="Household heatmap (Reform)")



    return tab