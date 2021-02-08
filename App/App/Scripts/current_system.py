import pandas as pd
import numpy as np
from math import pi


from bokeh.io import show, output_notebook, push_notebook
from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.transform import cumsum
from bokeh.transform import stack
from bokeh.models.widgets import Tabs

from gettsim import set_up_policy_environment
from gettsim.taxes.eink_st import st_tarif

from Scripts.plotstyle import plotstyle

def current_system(plot_dict):
    plot_dict = plot_dict["current_system"]

    def prepare_data(sel_year):
        LI = pd.Series(data=np.linspace(-1, 300001, 300001)) # Labor Income
        CI = pd.Series(data=np.linspace(-1, 300001, 300001)) # Capital Income
        #d = 0.2 #Deduction % - to be individualized
        TI= LI+CI # Total Income

        #Get relevant policy params from GETTSIM
        policy_params, policy_functions = set_up_policy_environment(sel_year)
        #labor_income = pd.Series(data=[LI])
        #integrated_income = pd.Series(data=[LI+CI])
        Tau_flat = (st_tarif(LI,policy_params["eink_st"])/LI) # Income tax rate - flat
        Tau_integrated = (st_tarif(TI,policy_params["eink_st"])/TI) # Income tax rate - integrated
        CD = policy_params["eink_st_abzuege"]["sparerpauschbetrag"] 
        CTau = policy_params["abgelt_st"]["abgelt_st_satz"] # Capital income tax rate

        # Calculate variables integrated taxes
        #D = d*(LI+CI) #Dedcutions
        #TI = (LI+CI) # taxable income
        T = TI*Tau_integrated # Income tax


        # Calculate variables separated taxes
        TLI = LI # taxable labor income
        TCI = CI-CD # taxable capital income
        TCI[TCI<0]=0 # replace negative taxable income
        # taxable capital income
        LT = TLI*Tau_flat # Labor income tax
        CT = TCI*CTau # Capital income tax  
        data_full = {"x_range":["LI","CI"],
                "top":[LI,CI],
                "tax_due": [LT,CT],
                "radius": [(LT.add(CT))/(max(LT.add(CT))*1.3),(LT.add(CT))/(max(LT.add(CT))*1.3)],
                "color": ["red","yellow"],
                "angle": [(LT/(LT+CT)) * 2*pi, (CT/(LT+CT)) * 2*pi],
                "legend": ["Labor tax","Capital tax"]
                }
                
        return data_full

    def make_dataset(LI,CI, data_full):
        selected_data= {}
        for i in ['top', 'tax_due']:
            selected_data[i] = [data_full[i][0][LI],data_full[i][1][CI]]

        selected_data["x_range"]=data_full["x_range"]
        selected_data["color"]=data_full["color"]
        selected_data["legend"]=data_full["legend"]

        #Select correct radius
        selected_data["radius"]= [data_full["radius"][0][int((CI+LI)/2)],data_full["radius"][1][int((CI+LI)/2)]]
        #Select correct angle
        selected_data["angle"]= [data_full["angle"][0][max(LI,CI)],data_full["angle"][1][max(LI,CI)]]
        #Switch start and end angle if CI>LI
        """
        if CI>LI:
            selected_data["angle"]=[data_full["angle"][1][LI],data_full["angle"][0][CI]]
        else:
            selected_data["angle"]=[data_full["angle"][0][LI],data_full["angle"][1][CI]]
        """
        return ColumnDataSource(selected_data)

    def make_plot(src):
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=["LI","CI","Tax due"],
            y_range=(0,300000+20000)
        )

        p.vbar(x="x_range", top ="top", source = src, width=0.3)
        p.wedge(x=2.5, y = 150000 , radius = "radius", start_angle = cumsum("angle", include_zero = True), end_angle = cumsum("angle"), source=src, fill_color="color", legend_group="legend")
        

        p = plotstyle(p,plot_dict)

        return p

    def update_plot(attr, old, new):
            LI = LI_selection.value
            CI = CI_selection.value
            new_src = make_dataset(LI,CI,data_full)

            src.data.update(new_src.data)


    LI_selection = Slider(start=0, end=300000, value=60000, step=1000, title="Labor income")
    CI_selection = Slider(start=0, end=300000, value=10000, step=1000, title="Capital income")
    

    CI_selection.on_change("value", update_plot)
    LI_selection.on_change("value", update_plot)

    data_full = prepare_data(2020)

    src = make_dataset(60000,10000,data_full)

    p = make_plot(src)

    layout = column(LI_selection, CI_selection, p)

    tab = Panel(child = layout, title="Current System")
    
    return tab