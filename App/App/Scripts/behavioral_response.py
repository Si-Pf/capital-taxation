import pandas as pd
import numpy as np
from math import pi


from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel, Arrow, NormalHead, Label, FactorRange, LabelSet
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.transform import cumsum
from bokeh.transform import stack, factor_cmap
from bokeh.models.widgets import Tabs
from bokeh.palettes import Category10


from Scripts.plotstyle import plotstyle


def behavioral_response(plot_dict):
    plot_dict = plot_dict["behavioral_response"]

    def prepare_data():
        
        deciles = ["1. Decile","2. Decile","3. Decile","4. Decile","5. Decile","6. Decile","7. Decile","8. Decile","9. Decile","91-95%","96-99%","Top 1%","Total"]

        #effects = ["Delta tax base","Externalities","Total"]

        #factors = [ (decile,effect) for decile in deciles for effect in effects]

        #delta_tax_burden = [0,0,-1,-12,-31,-41,-48,-49,-52,-23,13,171,-73] # Aggregated impact based on Bach and Buslei 2017 Table 4-5
        delta_tax_burden_avg = pd.Series(data=[0,0,0,-3,-8,-10,-11,-11,-11,-10,8,439,-2]) # from Bach & Buslei 2017 table 4-7



        # Needed to plot labels for negative values left of chart 
        #offset = [-25, -25, -25, -25, -25, -25, -25, -25, -25, -25, 0, 0, -25]

        #Calculation for ETR impact
        total_income = pd.Series(data=[-868,4569,9698,14050,18760,23846,29577,36769,47676,63486,95899,350423,28922]) #from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"
        capital_income_tax = pd.Series(data=[0,0,0,0,4,15,36,52,84,167,559,13873,163]) # from Bach & Buslei 2017 table 3-2
        income_tax = pd.Series(data=[0,9,99,655,1927,3524,5412,7812,11850,18978,36095,159230,7870])# from Bach & Buslei 2017 table 3-2
        net_income = total_income-capital_income_tax-income_tax
        net_income_reform = net_income - delta_tax_burden_avg

        ETR_current = (total_income-net_income)/total_income
        ETR_reform = (total_income-net_income_reform)/total_income
        Delta_ETR = ETR_reform-ETR_current

        # Reform estimates
        ETI = pd.Series(data=range(201)) # Define range of plausible elasticities

        recovered_percent = pd.Series(data=range(101))

        delta_tax_base = {}
        data_full = pd.DataFrame(columns=ETI)

        # Calculate the changes for all deciles except the bottom 3 -> change is always 0 there 
        for i in ETI:
            delta_tax_base[i] = total_income[3:] - total_income[3:]*(1+Delta_ETR[3:]*(ETI[i]/100))

        for i in delta_tax_base.keys():
            data_full[i]= [{"delta tax base":delta_tax_base[i].round(0),
            "externalities":(delta_tax_base[i]*(-1*recovered_percent[j]/100)).round(0),
            "total": (delta_tax_base[i]*(-1*recovered_percent[j]/100)+delta_tax_base[i]).round(0),
            "deciles":deciles[3:],
            } for j in recovered_percent]
                        
        return data_full

    def make_dataset(ETI,recovered_percent, data_full):
        selected_data = data_full[ETI][recovered_percent]
        factors = [(decile,effect) for decile in selected_data["deciles"] for effect in ['delta tax base', 'externalities', 'total']]
        change = sum(zip(selected_data["delta tax base"], selected_data["externalities"], selected_data["total"]),())

        return ColumnDataSource(data={"factor":factors,"change": change, "label":[str(int(i)) for i in change]})

    def make_plot(src):
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=FactorRange(*src.data["factor"]),
            
        )

        p.vbar(x="factor", top="change", width=0.8, source=src, fill_color=factor_cmap("factor", palette=Category10[4][1:], factors=["delta tax base","externalities","total"],start=1, end=2), line_color=None)

        labels = LabelSet(x="factor", y="change", text="label", source=src, render_mode='canvas',y_offset=-7,)

        p.add_layout(labels)

        p.xgrid.grid_line_color = None

        #Static styling
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1.4

        plot = plotstyle(p,plot_dict)

        return plot

    def update_plot(attr, old, new):
            ETI = int(ETI_selection.value*100)
            recovered_percent = int(recovery_selection.value*100)
            new_src = make_dataset(ETI,recovered_percent,data_full)
            src.data.update(new_src.data)
 

    ETI_selection = Slider(start=0, end=2, value=1, step=0.01, title="Elasticity of capital income")
    recovery_selection = Slider(start=0, end=1, value=0.1, step=0.01, title="Recovered portion (through externalities)")
    

    ETI_selection.on_change("value", update_plot)
    recovery_selection.on_change("value", update_plot)

    data_full = prepare_data()

    src = make_dataset(100,10,data_full)

    p = make_plot(src)

    layout = column(ETI_selection, recovery_selection, p)

    tab = Panel(child = layout, title="Behavioral responses (Reform)")
    
    return tab