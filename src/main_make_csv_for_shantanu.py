import csv
import os
import pandas as pd
import numpy as np


csvname1 = "../ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv"
csvname2 = "../csv_files/for_shantanu/replicate_OASIS_all_subjects.csv"

df1 = pd.read_csv(csvname1, index_col="Subject")
df2 = pd.read_csv(csvname2, index_col="Subject")

# get a list of unique subject ids in df2
sub_ids_ucla = df2.index
sub_ids_clinical = df1.index.unique()


mmse_values = {"mmse_avg": [np.mean(df1["mmse"][s]) for s in sub_ids_ucla]}
cdr_values = {"cdr_avg": [np.mean(df1["cdr"][s]) for s in sub_ids_ucla]}


# add mmse values to df2 as a column and write to a new csv file
df2["mmse_avg"] = mmse_values["mmse_avg"]
df2["cdr_avg"] = cdr_values["cdr_avg"]

# get the session day from the session column
session_day_ucla = df2["Session"][sub_ids_ucla]

# remove d from the session day and convert to int
session_day_ucla = session_day_ucla.str.replace("d", "").astype(int)


df2["mri_day"] = session_day_ucla
df2["closest_clnical_day"] = np.nan
df2["closest_day_mmse"] = np.nan
df2["closest_day_cdr"] = np.nan

for s in sub_ids_ucla:

    # print(s, session_day_ucla[s])

    # check if df1['Label'][s] is a string or a list
    if isinstance(df1["Label"][[s]], str):
        df1["Label"][s] = {s: df1["Label"][[s]]}

    # find session days in df1 for the same subject

    num_clinical_days = len(df1["Label"][[s]])  # [end-4:end]

    diff_days = 1e6

    for day in range(num_clinical_days):
        # print(day)
        clinical_day = int(df1["Label"][[s]].iloc[day][-4:])
        # print(clinical_day)
        # find the difference between clinical day and ucla day
        # print(abs(session_day_ucla[s] - clinical_day))
        if abs(session_day_ucla[s] - clinical_day) < diff_days:
            diff_days = abs(session_day_ucla[s] - clinical_day)
            session_days_clinical = clinical_day
            df2.loc[s, "closest_clnical_day"] = clinical_day
            df2.loc[s, "closest_day_mmse"] = df1["mmse"][[s]].iloc[day]
            df2.loc[s, "closest_day_cdr"] = df1["cdr"][[s]].iloc[day]


df2.to_csv(
    "../csv_files/for_shantanu/replicate_OASIS_all_subjects_with_mmse_cdr_avgs_closest_clinical_day_mmse_cdr.csv"
)
# sort subject ids alphabetically
