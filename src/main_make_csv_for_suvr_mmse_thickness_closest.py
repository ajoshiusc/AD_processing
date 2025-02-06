import csv
import os
import pandas as pd
import numpy as np
from tqdm import tqdm

csvname1 = "../ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv"
csvname_pet = "/home/ajoshi/Projects/AD_processing/csv_files/OASIS3_PUP.csv"


df1 = pd.read_csv(csvname1, index_col="Subject")
df_pet = pd.read_csv(csvname_pet, index_col="MRId")


# sub_ids_pet should be first 8 letters of the index in df_pet

sub_ids_pet = [s[0:8] for s in df_pet.index]

# pet_day should be the last 4 letters of the index in df_pet
all_pet_days = [s[-4:] for s in df_pet.index]



pet_measure = "PET_fSUVR_rsf_TOT_CORTMEAN"
th_method = 'pvc_th'
gord_dir = "pvc_th_smooth" 

s = os.listdir("/deneb_disk/bfp_oasis3")
sub_ids = list()
sub_clinical_ids = list()
sub_mr_ids = list()
gord_fname_list = list()
session_id = list()

for n in tqdm(range(len(s))):
    gord_fname = os.path.join(
        "/deneb_disk/thickness_data/thickness_" + gord_dir,
        s[n] + "." + th_method + ".gord.smooth.mat",
    )

    if os.path.exists(gord_fname):
        sub_ids.append(s[n][4:12])
        sub_mr_ids.append(s[n][4:12] + "_MR_" + s[n][17:22])
        sub_clinical_ids.append(s[n][4:12] + "_ClinicalData_" + s[n][17:22])
        gord_fname_list.append(gord_fname)
        session_id.append(s[n][17:22])

print(sub_ids)



sub_ids_clinical = df1.index.unique()


mmse_values = {"mmse_avg": [np.mean(df1["mmse"][s]) for s in sub_ids]}
cdr_values = {"cdr_avg": [np.mean(df1["cdr"][s]) for s in sub_ids]}
suvr_values = {"suvr_avg": []}


for s in sub_ids:

    # in sub_ids_pet find the indices of the subject s
    idx = [i for i, x in enumerate(sub_ids_pet) if x == s]

    suvr_avg = np.mean(df_pet[pet_measure].iloc[idx])
    suvr_values["suvr_avg"].append(suvr_avg)


# initialize df as datadrame
df2 = pd.DataFrame(
    index=sub_ids,
    columns=[
        "Subject",
        "M/F",
        "Age",
        "Session",
        "mmse_avg",
        "cdr_avg",
        "suvr_avg",
        "mri_day",
        "closest_clnical_day",
        "closest_suvr_day",
        "closest_day_mmse_value",
        "closest_day_cdr_value",
        "closest_day_suvr_value",
    ],
)

# add subject
df2["Subject"] = sub_ids

#df2["M/F"] = df1["M/F"][sub_ids]
#df2["Age"] = df1["Age"][sub_ids]
df2["Session"] = session_id

# add mmse values to df2 as a column and write to a new csv file
df2["mmse_avg"] = mmse_values["mmse_avg"]
df2["cdr_avg"] = cdr_values["cdr_avg"]
df2["suvr_avg"] = suvr_values["suvr_avg"]

# get the session day from the session column
session_day = df2["Session"][sub_ids]

# remove d from the session day and convert to int
session_day = session_day.str.replace("d", "").astype(int)


df2["mri_day"] = session_day
df2["closest_clnical_day"] = np.nan
df2["closest_suvr_day"] = np.nan
df2["closest_day_mmse_value"] = np.nan
df2["closest_day_cdr_value"] = np.nan
df2["closest_day_suvr_value"] = np.nan

for s in sub_ids:

    # print(s, session_day[s])

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
        # print(abs(session_day[s] - clinical_day))
        if abs(session_day[s] - clinical_day) < diff_days:
            diff_days = abs(session_day[s] - clinical_day)
            session_days_clinical = clinical_day
            df2.loc[s, "closest_clnical_day"] = clinical_day
            df2.loc[s, "closest_day_mmse_value"] = df1["mmse"][[s]].iloc[day]
            df2.loc[s, "closest_day_cdr_value"] = df1["cdr"][[s]].iloc[day]


    # find the closest suvr day
    diff_days = 1e6
    for i, sub_id_pet in enumerate(sub_ids_pet):
        if sub_id_pet == s:
            suvr_day = int(all_pet_days[i])
            if abs(session_day[s] - suvr_day) < diff_days:
                diff_days = abs(session_day[s] - suvr_day)
                session_days_suvr = suvr_day
                df2.loc[s, "closest_suvr_day"] = suvr_day
                df2.loc[s, "closest_day_suvr_value"] = df_pet[pet_measure].iloc[i]





df2.to_csv(
    "../csv_files/OASIS_all_subjects_with_mmse_cdr_avgs_suvr_closest_clinical_day_mmse_cdr.csv"
)
# sort subject ids alphabetically
