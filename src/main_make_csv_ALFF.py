import csv
import os
import pandas as pd
import numpy as np
from tqdm import tqdm

s = os.listdir("/deneb_disk/oasis_alff_data_z_smooth")
sub_ids = list()
sub_clinical_ids = list()
sub_mr_ids = list()
gord_fname_list = list()

for n in tqdm(range(len(s))):
    gord_fname = os.path.join('/deneb_disk/oasis_alff_data_z_smooth',s[n]) #os.path.join('/deneb_disk/bfp_oasis3',s[n],'func',s[n] +'_rest_bold.ALFF_Z.GOrd.mat')

    if os.path.exists(gord_fname):
        sub_ids.append(s[n][4:12])
        sub_mr_ids.append(s[n][4:12] + "_MR_" + s[n][17:22])
        sub_clinical_ids.append(s[n][4:12] + "_ClinicalData_" + s[n][17:22])
        gord_fname_list.append(gord_fname)

print(sub_ids)


csvname1 = "../ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv"
csvname2 = "../oasis3_MR_scans.csv"
measure = "mmse"
measure_short = measure.replace(".", "").replace(" ", "").replace(":", "_")

df1 = pd.read_csv(csvname1, index_col="Subject")
df2 = pd.read_csv(csvname2, index_col="Label")
data1 = df2["M/F"][sub_mr_ids]
data1.index = sub_ids  # Change the index to the subject id
data1.index.name = "Subject"

data2_values = {measure: [np.mean(df1[measure][s]) for s in sub_ids]}
data2 = pd.DataFrame(index=sub_ids, data=data2_values)
data2.index.name = "Subject"

data3 = df2["Age"][sub_mr_ids]
data3.index = sub_ids  # Change the index to the subject id
data3.index.name = "Subject"

"""
data4 = data3.copy()
data4[:] = gord_fname_list
data4.index.name = 'Filename'
"""

d = {"FileName": gord_fname_list}
data4 = pd.DataFrame(index=data2.index.copy(), data=d)
result = pd.merge(left=data1, right=data3, on="Subject")
result = pd.merge(left=result, right=data2, on="Subject")
result = pd.merge(left=result, right=data4, on="Subject")


print(result)

result.rename(columns={"M/F": "Gender", measure: measure_short}, inplace=True)

result.to_csv("oasis3_bfp_alff_z_smooth.csv")

# result.to_csv('oasis3_bfp_SCT.csv')

print("done")

