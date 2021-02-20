# Bokeh basics
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Div
from bokeh.models.widgets import Tabs


# Create a dictionairy to store all plot titles, axes etc.
plot_list = [
    "tax_revenue",
    "Impact_heatmap",
    "individual_view",
    "lorenz_curves",
    "behavioral_response",
    "revenue_bevavior",
]
plot_attributes = [
    "title",
    "x_axis_label",
    "y_axis_label",
    "x_axis_format",
    "y_axis_format",
    "legend_location",
]
attribute_dict = {
    "current_system": [
        "Separate income and capital tax",
        "",
        "taxable income",
        "",
        "0€",
        "bottom_right",
    ],
    "Impact_heatmap": [
        "Impact heatmap: Mechanical effect of the reform by taxable capital and labor income",
        "Taxable labor income (in €)",
        "Taxable capital income (in €)",
        "0€",
        "0€",
        "",
    ],
    "individual_view": [
        "Individual mechanical impact of reform",
        "Status quo labor and capital taxation (S) vs. Reform integrated income taxation (R)",
        "Value (in €)",
        "",
        "0€",
        "top_left",
    ],
    "lorenz_curves": [
        "Lorenz curves Germany 2017",
        "Income deciles",
        "Share of income",
        "0.0",
        "0%",
        "top_left",
    ],
    "tax_revenue": [
        "Aggregate mechanical tax revenue effects of reform",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
    ],
    "behavioral_response": [
        "Average change to reported tax base per decile",
        "",
        "Avg. changes to reported tax base (in €)",
        "",
        "0€",
        "top_left",
    ],
    "revenue_bevavior": [
        "Aggregate tax revenue change after behavioral responses per decile",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
    ],
}
plot_dict = {
    p: {a: attribute_dict[p][counter] for counter, a in enumerate(plot_attributes)}
    for p in plot_list
}


# Each tab is drawn by one script
from Scripts.tax_revenue import tax_revenue
from Scripts.heatmap import heatmap_tab
from Scripts.individual_view import individual_view
from Scripts.lorenz_curves import lorenz_tab
from Scripts.behavioral_response import behavioral_response

# Call tab functions
tab1 = lorenz_tab(plot_dict)
tab2 = individual_view(plot_dict)
tab3 = heatmap_tab(plot_dict)
tab4 = tax_revenue(plot_dict)
tab5 = behavioral_response(plot_dict)

tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5])

header = Div(
    text="""<h1>Comparing Germanys flat capital income tax to an integrated income tax</h1>""",
    width=900,
    height=80,
)

intro = Div(
    text="""This dashboard is part of a master thesis in economics. It compares on several tabs 
    how capital income is taxed currently in Germany (Status Quo) with a potential alternative policy (Reform). 
    Currently capital income is taxed with a flat final tax of 25%, the considered reform would 
    integrate capital income into the progressive income tax schedule with a 60 percent taxable rule
    for dividends to limit the double taxation of paid out corporate income.""",
    width=800,
    height=100,
)

print("INFO - Server is receiving request")

curdoc().add_root(column(header, intro, tabs))
