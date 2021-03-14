# Bokeh basics
import pickle
from datetime import datetime

import pytz
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.layouts import row
from bokeh.models import Button
from bokeh.models import Div
from bokeh.models import TextInput
from bokeh.models.widgets import Tabs

tz = pytz.timezone("Europe/Berlin")

# Create a dictionairy to store all plot titles, axes etc.
plot_list = [
    "tax_revenue",
    "Impact_heatmap",
    "individual_view",
    "lorenz_curves",
    "behavioral_response",
    "revenue_bevavior",
    "lorenz_curves2",
    "parameter_heatmap",
]
plot_attributes = [
    "title",
    "x_axis_label",
    "y_axis_label",
    "x_axis_format",
    "y_axis_format",
    "legend_location",
    "description",
]
attribute_dict = {
    "Impact_heatmap": [
        "Impact heatmap: Mechanical effect of the reform by taxable capital and labor income",
        "Taxable labor income (in €)",
        "Taxable capital income (in €)",
        "0€",
        "0€",
        "",
        """Household heatmap for impact to tax burden of moving from the current tax system
        to an integrated tax system. The black points correspond to the average labor and
        capital income per decile of the equivalence weighted distribution. The grey
        contour lines correspond to income combinations with similar impacts.""",
    ],
    "individual_view": [
        "Individual mechanical impact of reform",
        "Status quo labor and capital taxation (S) vs. Reform integrated income taxation (R)",
        "Value (in €)",
        "",
        "0€",
        "top_left",
        """Illustration of the individual mechanical effect of separate capital and labor
        taxation of the status quo (S) compared to the reform with integrated income tax
        system (R). Assumed is constant deduction behavior and  labor / capital supply.
        Slicers select income combinations to be compared.""",
    ],
    "lorenz_curves": [
        "Lorenz curves Germany 2017",
        "Income deciles",
        "Share of income",
        "0.0",
        "0%",
        "top_left",
        """Lorenz curves for taxable capital, labor and total income in Germany 2017. Data
         is a forward iteration of 2007/2008 tax return data. The x-axis comprises the
         income deciles of equivalence-weighted total household income. The y-axis shows
         the cumulative average income share held by the decile. The top decile is split
         into 3 weighted groups.""",
    ],
    "tax_revenue": [
        "Aggregate mechanical tax revenue effects of reform",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
        """Simulation of tax revenue changes of the considered reform in 2017. Shown are the
        aggregate (not average) changes in tax revenue per decile in Million Euro. The table
        also shows the corresponding changes to effective tax rate (ΔETR).""",
    ],
    "behavioral_response": [
        "Average change to reported tax base per decile",
        "",
        "Avg. changes to reported tax base (in €)",
        "",
        "0€",
        "top_left",
        """Based on the changes to the effective tax rate (ΔETR) by decile this figure
        illustrates for different elasticity levels the average change in reported total
        tax base due to behavioral responses. Bottom three deciles omitted (as ΔETR=0).
        The recovered portion can be used to simulate offsetting externalities like
        evaded taxes, recovered in tax audits or income shifted to other tax bases or
        periods.""",
    ],
    "revenue_bevavior": [
        "Aggregate tax revenue change after behavioral responses per decile",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
        """""",
    ],
    "lorenz_curves2": [
        "Lorenz curves Germany 2017 (Status quo vs. Reform)",
        "Income deciles",
        "Share of income",
        "0.0",
        "0%",
        "top_left",
        """Lorenz curves for Germany 2017 after including the simulated changes to
        tax burden per decile. Capital income is small compared to total income for
        all deciles. Changes are hardly visible in the lorenz curve.""",
    ],
    "parameter_heatmap": [
        "Parameter heatmap: Effect of the reform by behavioral response parameter values",
        "Recovered portion (Offsetting externalities to behavioral reactions)",
        "Elasticity of capital income",
        "0.0",
        "0.0",
        "",
        """Parameter heatmap for the elasticity of capital income and recovered portion.
        Displays how combinations of the parameters affect the total revenue effect of
        the simulated reform. The black dots indicate for which combination the reform
        would have an aggregate effect of approximately 0. For most deciles the changes
        are small.""",
    ],
}

print("{} INFO - Creating a plot dict".format(datetime.now(tz)))

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
from Scripts.pre_processing import generate_data
from Scripts.lorenz_curves2 import lorenz_tab2
from Scripts.parameter_heatmap import parameter_heatmap_tab

all_data = pickle.load(open("all_data.pickle", "rb"))

print("{} INFO - Server receives request".format(datetime.now(tz)))


# Call tab functions
tab1 = lorenz_tab(plot_dict["lorenz_curves"], all_data["lorenz_curves"])
tab2 = individual_view(plot_dict["individual_view"], all_data["individual_view"])
tab3 = heatmap_tab(plot_dict["Impact_heatmap"], all_data["impact_heatmap"])
tab4 = tax_revenue(plot_dict["tax_revenue"], all_data["tax_revenue"])
tab5 = lorenz_tab2(plot_dict["lorenz_curves2"], all_data["lorenz_curves2"])
tab6 = behavioral_response(
    plot_dict["behavioral_response"],
    plot_dict["revenue_bevavior"],
    all_data["behavioral_response"],
)
tab7 = parameter_heatmap_tab(
    plot_dict["parameter_heatmap"], all_data["parameter_heatmap"]
)

tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6, tab7])

header = Div(
    text="""<h1>Comparing Germanys flat capital income tax to an integrated income tax</h1>""",
    width=900,
    height=80,
)

intro = Div(
    text="""This dashboard is part of a master thesis in economics. It compares on several tabs
    how capital income is taxed currently in Germany (Status Quo) with a potential alternative
    policy (Reform). Currently capital income is taxed with a flat final tax of 25%, the
    considered reform would integrate capital income into the progressive income tax schedule
    with a 60 percent taxable rule for dividends to limit the double taxation of paid out
    corporate income.""",
    width=800,
    height=100,
)

spacer = Div(text="""""", height=20)

# Functions for regenerating data


def finished_text():
    update_text.value = "Status: Completed"


def update_function():
    update_text.value = "Status: In progress"
    curdoc().add_next_tick_callback(generate_data)
    curdoc().add_next_tick_callback(finished_text)


update_text = TextInput(value="Status: Not started", disabled=True, width=140)

button = Button(
    label="Regenerate data", button_type="success", width=140, background="#c1c1c1"
)
button.on_click(update_function)


print("{} INFO - Server completes processing request".format(datetime.now(tz)))

# Put everything together
curdoc().add_root(column(header, intro, row(button, update_text), spacer, tabs))
curdoc().title = (
    "Comparing Germanys flat capital income tax to an integrated income tax"
)
