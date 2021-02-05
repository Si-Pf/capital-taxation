# Bokeh basics 
from bokeh.io import curdoc
from bokeh.models.widgets import Tabs
from bokeh.models import NumeralTickFormatter
from bokeh.models import Div
from bokeh.layouts import column

# Each tab is drawn by one script
from Scripts.tax_revenue import tax_revenue
from Scripts.heatmap import heatmap_tab
from Scripts.individual_view import individual_view
from Scripts.lorenz_curves import lorenz_tab
from Scripts.behavioral_response import behavioral_response

# Create a dictionairy to store all plot titles, axes etc. 
plot_list = ["tax_revenue","Impact_heatmap","individual_view","lorenz_curves", "behavioral_response"]
plot_attributes = ["title","x_axis_label","y_axis_label","x_axis_format","y_axis_format","legend_location"]
attribute_dict = {"current_system":["Separate income and capital tax","","taxable income", "","0€","bottom_right"],
                "Impact_heatmap":["Impact heatmap","Taxable labor income", "Taxable capital income", "0€", "0€", ""],
                "individual_view":["Individual view","Separate labor and capital taxation (S) vs. integrated income taxation (I)","Value in €","","0€","top_left"],
                "lorenz_curves":["Lorenz curves","Income deciles","Share of income","0.0","0%","top_left"],
                "tax_revenue":["Tax revenue effects of reform","Change to tax revenue (in Million Euro)","Deciles","0€","",""],
                "behavioral_response":["Behavioral responses","Deciles","Changes to reported tax base","","0€","top_left"]
}
plot_dict = {p:{a:attribute_dict[p][counter] for counter,a in enumerate(plot_attributes)} for p in plot_list}




#Call tab functions
tab1 = lorenz_tab(plot_dict)
tab2 = individual_view(plot_dict)
tab3 = heatmap_tab(plot_dict)
tab4 = tax_revenue(plot_dict)
tab5 = behavioral_response(plot_dict)

tabs = Tabs(tabs=[tab1,tab2,tab3,tab4,tab5])

header = Div(text="""<h1>Comparing Germanys flat capital income tax to an integrated income tax</h1>""",width=900, height=90)

curdoc().add_root(column(header, tabs))