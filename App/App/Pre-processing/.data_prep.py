import pandas as pd


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
                    -30 if v < 0 else 2
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


data_full = prepare_data()

# Create storage object with filename `processed_data`
data_store = pd.HDFStore("data.h5")

# Put DataFrame into the object setting the key as 'preprocessed_df'
data_store["preprocessed_df"] = data_full
data_store.close()
