import pickle

import numpy as np
import pandas as pd
from gettsim import set_up_policy_environment
from gettsim.taxes.eink_st import st_tarif


# Each plot has one data preparation function as defined below


def individiual_view_data():

    LI = pd.Series(data=range(0, 250001, 500))  # Labor Income
    CI = pd.Series(data=range(0, 250001, 500))  # Capital Income
    # np.linspace(-1, 300001, 300001)
    LD = 0.2 * LI  # Assumption
    TTI = LI + CI  # Total Income
    TD = 0.2 * TTI  # Assumption
    TI = TTI - TD  # taxable income

    # Calculate variables separated taxes
    TLI = LI - LD  # taxable labor income

    # Get relevant policy params from GETTSIM
    policy_params, policy_functions = set_up_policy_environment(2020)

    Tau_flat = (
        (st_tarif(TLI, policy_params["eink_st"]) / TLI).fillna(0).round(2)
    )  # Income tax rate - flat

    Tau_integrated = (
        (st_tarif(TI, policy_params["eink_st"]) / TI).fillna(0).round(2)
    )  # Income tax rate - integrated

    CD = pd.Series(
        data=[policy_params["eink_st_abzuege"]["sparerpauschbetrag"]] * len(LI)
    )  # Capital income deductions

    CTau = policy_params["abgelt_st"]["abgelt_st_satz"]  # Capital tax rate

    TCI = CI - CD  # taxable capital income
    TCI[TCI < 0] = 0  # replace negative taxable income
    # Calculate variables integrated taxes

    T = (TI * Tau_integrated).round(2)  # Total tax

    # taxable capital income
    LT = (TLI * Tau_flat).round(2)  # Labor income tax
    CT = TCI * CTau  # Capital income tax

    # Net incomes
    NCI = TCI - CT  # Capital
    NLI = (TLI - LT).round(2)  # Labor
    NI = (TI - T).round(2)  # Total

    # blank placeholder
    B = [0] * len(LI)

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


def heatmap_data():
    LI = pd.Series(data=np.linspace(0, 310000, 250))  # Labor Income
    CI = pd.Series(data=np.linspace(0, 100000, 250))  # Capital Income

    # Get relevant policy params from GETTSIM
    policy_params, policy_functions = set_up_policy_environment(2020)
    CD = policy_params["eink_st_abzuege"]["sparerpauschbetrag"]
    CTau = policy_params["abgelt_st"]["abgelt_st_satz"]  # Capital income tax rate

    TCI = CI - CD  # taxable capital income
    TCI[TCI < 0] = 0  # replace negative taxable income
    CT = TCI * CTau  # Capital income tax

    heatmap_df = pd.DataFrame(columns=LI)

    # Iterate through LI and CI combinations for separate taxes
    for i in range(len(LI)):
        this_column = heatmap_df.columns[i]
        e = pd.Series(data=[LI[i]] * len(LI))
        c = e + CI
        heatmap_df[this_column] = (st_tarif(c, policy_params["eink_st"])) - (
            st_tarif(e, policy_params["eink_st"]) + CT
        )

    heatmap_df.index = CI

    heatmap_source = pd.DataFrame(
        heatmap_df.stack(), columns=["Change to tax burden"]
    ).reset_index()
    heatmap_source.columns = [
        "Capital income",
        "Labor income",
        "Change to tax burden",
    ]

    # Data to show where average household per decile is located in heatmap
    deciles = ["", "", "", "", "", "", "", "", "", "P90", "P95", "P99", "P100"]
    capital_income_tax = pd.Series(
        data=[0, 0, 0, 0, 0, 4, 15, 36, 52, 84, 167, 559, 13873]
    )  # from Bach & Buslei 2017 table 3-2
    capital_income = capital_income_tax / 0.26375
    total_income = pd.Series(
        data=[
            0,
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
        ]
    )  # from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"
    labor_income = total_income - capital_income

    household_dict = {
        "deciles": deciles,
        "capital_income": capital_income,
        "labor_income": labor_income,
    }

    return {
        "heatmap_source": heatmap_source,
        "household_dict": household_dict,
    }


def behavioral_response_data():

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
        data=[0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230, 7870]
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
                                delta_tax_base[i] * (-1 * recovered_percent[j] / 100)
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


def lorenz_curves_data():

    deciles = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
    labels = [
        "0",
        "0-0.1",
        "0.1-0.2",
        "0.2-0.3",
        "0.3-0.4",
        "0.4-0.5",
        "0.5-0.6",
        "0.6-0.7",
        "0.7-0.8",
        "0.8-0.9",
        "0.9-0.95",
        "0.95-0.99",
        "0.99-1",
    ]
    weights = pd.Series(
        data=[0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.04, 0.01]
    )

    capital_income_tax = pd.Series(
        data=[0, 0, 0, 0, 0, 4, 15, 36, 52, 84, 167, 559, 13873]
    )  # from Bach & Buslei 2017 table 3-2
    capital_income = (capital_income_tax / 0.26375).round(2)

    income_tax = pd.Series(
        data=[0, 0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230]
    )  # from Bach & Buslei 2017 table 3-2

    total_income = pd.Series(
        data=[
            0,
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
        ]
    )  # from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"

    labor_income = total_income - capital_income

    net_income = total_income - capital_income_tax - income_tax

    total_income_share = (total_income * weights).cumsum() / (
        total_income * weights
    ).sum()
    capital_income_share = (capital_income * weights).cumsum() / (
        capital_income * weights
    ).sum()
    labor_income_share = (labor_income * weights).cumsum() / (
        labor_income * weights
    ).sum()
    net_income_share = (net_income * weights).cumsum() / (net_income * weights).sum()

    income_share_dict = {
        "deciles": deciles,
        "total_income_share": total_income_share,
        "labor_income_share": labor_income_share,
        "capital_income_share": capital_income_share,
        "net_income_share": net_income_share,
    }

    raw_dict = {
        "deciles": labels,
        "weights": weights,
        "capital_income_tax": capital_income_tax,
        "total_income": total_income,
        "capital_income": capital_income,
        "labor_income": labor_income,
        "net_income": net_income,
    }

    return {"income_share_dict": income_share_dict, "raw_dict": raw_dict}


def tax_revenue_data():
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
        "91-95% Percentile",
        "96-99% Percentile",
        "Top 1% Percentile",
        "Total",
    ]

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
    delta_tax_burden_avg = pd.Series(
        data=[0, 0, 0, -3, -8, -10, -11, -11, -11, -10, 8, 439, -2]
    )  # from Bach & Buslei 2017 table 4-7

    # Needed to plot labels for negative values left of chart
    offset = [-25, -25, -25, -25, -25, -25, -25, -25, -25, -25, 0, 0, -25]

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
        data=[0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230, 7870]
    )  # from Bach & Buslei 2017 table 3-2
    net_income = total_income - capital_income_tax - income_tax
    net_income_reform = net_income - delta_tax_burden_avg

    ETR_current = (total_income - net_income) / total_income
    ETR_reform = (total_income - net_income_reform) / total_income
    Delta_ETR = ETR_reform - ETR_current

    label = [str(i) for i in delta_tax_burden]

    revenue_dict = {
        "deciles": deciles,
        "delta_tax_burden": delta_tax_burden,
        "label": label,
        "offset": offset,
        "Delta_ETR": Delta_ETR,
    }

    return revenue_dict


def lorenz_curves_data2():

    deciles = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1]
    labels = [
        "0",
        "0-0.1",
        "0.1-0.2",
        "0.2-0.3",
        "0.3-0.4",
        "0.4-0.5",
        "0.5-0.6",
        "0.6-0.7",
        "0.7-0.8",
        "0.8-0.9",
        "0.9-0.95",
        "0.95-0.99",
        "0.99-1",
    ]
    weights = pd.Series(
        data=[0, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05, 0.04, 0.01]
    )

    capital_income_tax = pd.Series(
        data=[0, 0, 0, 0, 0, 4, 15, 36, 52, 84, 167, 559, 13873]
    )  # from Bach & Buslei 2017 table 3-2

    income_tax = pd.Series(
        data=[0, 0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230]
    )  # from Bach & Buslei 2017 table 3-2

    total_income = pd.Series(
        data=[
            0,
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
        ]
    )  # from Bach & Buslei 2017 table 3-2 "Äquivalenzgewichtetes Einkommen"

    net_income = total_income - capital_income_tax - income_tax

    simulated_change_reform = pd.Series(
        data=[0, 0, 0, 0, -3, -8, -10, -11, -11, -11, -10, 8, 439]
    )  # from Bach & Buslei 2017 table 4-7

    net_income_simulated = net_income - simulated_change_reform

    total_income_share = (total_income * weights).cumsum() / (
        total_income * weights
    ).sum()

    net_income_share = (net_income * weights).cumsum() / (net_income * weights).sum()
    net_income_share_simulated = (net_income_simulated * weights).cumsum() / (
        net_income_simulated * weights
    ).sum()

    # Include Elasticities based of effective tax rate (ETR)
    ETR_current = (total_income - net_income) / total_income
    ETR_reform = (total_income - net_income_simulated) / total_income
    Net_rate_current = 1 - ETR_current
    Net_rate_reform = 1 - ETR_reform

    delta = Net_rate_reform - Net_rate_current

    total_income_reform = total_income * (1 + delta)
    total_income_share_reform = (total_income_reform * weights).cumsum() / (
        total_income_reform * weights
    ).sum()

    income_share_dict = {
        "deciles": deciles,
        "total_income_share": total_income_share,
        "net_income_share": net_income_share,
        "net_income_share_simulated": net_income_share_simulated,
        "total_income_share_reform": total_income_share_reform,
    }

    raw_dict = {
        "deciles": labels,
        "weights": weights,
        "total_income": total_income,
        "net_income": net_income,
        "net_income_simulated": net_income_simulated,
    }

    return {"income_share_dict": income_share_dict, "raw_dict": raw_dict}


def parameter_heatmap():

    delta_tax_burden_avg = pd.Series(
        data=[0, 0, 0, -3, -8, -10, -11, -11, -11, -10, 8, 439, -2]
    )  # from Bach & Buslei 2017 table 4-7
    delta_tax_burden = pd.Series(
        data=[0, 0, -1, -12, -31, -41, -48, -49, -52, -23, 13, 171, -73]
    )  # Aggregated impact based on Bach and Buslei 2017 Table 4-5
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
        data=[0, 9, 99, 655, 1927, 3524, 5412, 7812, 11850, 18978, 36095, 159230, 7870]
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
            (
                (
                    delta_tax_base[i] * (-1 * recovered_percent[j] / 100)
                    + delta_tax_base[i]
                )
                * number_of_taxpayers[3:]
            )
            / 1000000
            + delta_tax_burden[3:]
            for j in recovered_percent
        ]

    heatmap_source = pd.DataFrame(
        data_full.stack(), columns=["aggr_delta_after_eti"]
    ).reset_index()
    heatmap_source.columns = [
        "Recovered_portion",
        "Elasticity",
        "aggr_delta_after_eti",
    ]

    heatmap_source["Recovered_portion"] = heatmap_source["Recovered_portion"] / 100
    heatmap_source["Elasticity"] = heatmap_source["Elasticity"] / 100

    heatmap_source["total"] = [i[12] for i in heatmap_source["aggr_delta_after_eti"]]

    return heatmap_source


# Call all data preparation functions into a single dictionairy


def generate_data():
    all_data = {
        "individual_view": individiual_view_data(),
        "impact_heatmap": heatmap_data(),
        "behavioral_response": behavioral_response_data(),
        "lorenz_curves": lorenz_curves_data(),
        "tax_revenue": tax_revenue_data(),
        "lorenz_curves2": lorenz_curves_data2(),
        "parameter_heatmap": parameter_heatmap(),
    }

    dbfile = open("all_data.pickle", "wb")

    # source, destination
    pickle.dump(all_data, dbfile)
    dbfile.close()
