import pandas as pd
import numpy as np



from bokeh.plotting import figure

from bokeh.models import CategoricalColorMapper, HoverTool, ColumnDataSource, Panel, Arrow, NormalHead, Label
from bokeh.models.widgets import CheckboxGroup, Slider, RangeSlider, Tabs, TableColumn, DataTable
from bokeh.models import LinearColorMapper
from bokeh.models import ColorBar
from bokeh.models import BasicTicker
from bokeh.models import NumberFormatter
from bokeh.models import DataTable, TableColumn
from bokeh.models import Div

from bokeh.layouts import column, row, WidgetBox
from bokeh.palettes import Category20_16

from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
from bokeh.transform import cumsum
from bokeh.transform import stack
from bokeh.models.widgets import Tabs
from bokeh.palettes import RdYlGn
from bokeh.models import LabelSet

from Scripts.plotstyle import plotstyle

def tax_revenue(plot_dict):
    plot_dict = plot_dict["tax_revenue"]

    def prepare_data():
        deciles = ["1. Decile","2. Decile","3. Decile","4. Decile","5. Decile","6. Decile","7. Decile","8. Decile","9. Decile","91-95% Percentile","96-99% Percentile","Top 1% Percentile","Total"]

        delta_tax_burden = [0,0,-1,-12,-31,-41,-48,-49,-52,-23,13,171,-73] # Aggregated impact based on Bach and Buslei 2017 Table 4-5
        delta_tax_burden_avg = pd.Series(data=[0,0,0,-3,-8,-10,-11,-11,-11,-10,8,439,-2]) # from Bach & Buslei 2017 table 4-7
        
        

        # Needed to plot labels for negative values left of chart 
        offset = [-25, -25, -25, -25, -25, -25, -25, -25, -25, -25, 0, 0, -25]

        #Calculation for ETR impact
        total_income = pd.Series(data=[-868,4569,9698,14050,18760,23846,29577,36769,47676,63486,95899,350423,28922]) #from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"
        capital_income_tax = pd.Series(data=[0,0,0,0,4,15,36,52,84,167,559,13873,163]) # from Bach & Buslei 2017 table 3-2
        income_tax = pd.Series(data=[0,9,99,655,1927,3524,5412,7812,11850,18978,36095,159230,7870])# from Bach & Buslei 2017 table 3-2
        net_income = total_income-capital_income_tax-income_tax
        net_income_reform = net_income - delta_tax_burden_avg

        ETR_current = (total_income-net_income)/total_income
        ETR_reform = (total_income-net_income_reform)/total_income
        Delta_ETR = ETR_reform-ETR_current

        label = [str(i) for i in delta_tax_burden]
        
        return ColumnDataSource({"deciles":deciles,"delta_tax_burden":delta_tax_burden,"label":label,"offset":offset, "Delta_ETR":Delta_ETR})
    

    def make_plot(src):
        p = figure(
            plot_width=800,
            plot_height=400,
            y_range=src.data["deciles"],
            
        )

        labels = LabelSet(x="delta_tax_burden", y="deciles", text="label", source=src,x_offset="offset", y_offset=-10, render_mode='canvas',)

        color_mapper = LinearColorMapper(palette=RdYlGn[10],low =min(src.data["delta_tax_burden"]) ,high= max(src.data["delta_tax_burden"])-120)

        p.hbar(y="deciles",right="delta_tax_burden", source = src, height = 0.8, color = {"field": "delta_tax_burden", "transform":color_mapper}, line_color=None)


        # Table to display source data 
        columns = [TableColumn(field="deciles",  title = "Deciles"),
                TableColumn(field="delta_tax_burden", title="Tax revenue change (in Mio. Euro)"),
                TableColumn(field="Delta_ETR", title="Effective tax rate change (in %)", formatter= NumberFormatter(format="0.0000%")), ]

        data_table = DataTable(source=src, columns=columns, width=800, height=350)

        

        p.add_layout(labels)

        p.xaxis.tags=["numeric"]
        p.yaxis.tags =["categorical"]

        plot = plotstyle(p,plot_dict)

        return plot, data_table

    src = prepare_data()

    plot, table = make_plot(src)

    table_title = Div(text="""<b>Source data</b>""",width=800, height=20)
    reference = Div(text="""Data from <a href="http://hdl.handle.net/10419/172793">Bach and Buslei 2017</a> table 4-5. Simulated scenario where the capital income tax is included in the progressive income taxation, itemized deductions for capital income and "Teileinkünfteverfahren" for dividends are reintroduced.""",width=800, height=80)

    layout = row(column(plot,table_title,table, reference))

    

    tab = Panel(child = layout, title="Tax revenues (Reform)")

    

    return tab