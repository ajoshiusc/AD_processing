import csv
import os
import pandas as pd
import numpy as np
from tqdm import tqdm

th_method = 'pvc_th'
gord_dir = "pvc_th_smooth" 

s = os.listdir("/ImagePTE1/ajoshi/data/bfp_oasis3")
sub_ids = list()
sub_clinical_ids = list()
sub_mr_ids = list()
gord_fname_list = list()

for n in tqdm(range(len(s))):
    gord_fname = os.path.join(
        "/ImagePTE1/ajoshi/data/thickness_data/thickness_" + gord_dir,
        s[n] + "." + th_method + ".gord.smooth.mat",
    )

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
data2_num_values = {'num_'+measure: [df1[measure][s].size for s in sub_ids]}



data2 = pd.DataFrame(index=sub_ids, data=data2_values)
data2.index.name = "Subject"

data2n = pd.DataFrame(index=sub_ids, data=data2_num_values)
data2n.index.name = "Subject"

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
result = pd.merge(left=result, right=data2n, on="Subject")
result = pd.merge(left=result, right=data4, on="Subject")


print(result)

result.rename(columns={"M/F": "Gender", measure: measure_short}, inplace=True)

result.to_csv("outputs/oasis3_bfp_" + measure_short + "_" + th_method + "_smooth.csv")

# result.to_csv('oasis3_bfp_SCT.csv')







print("done")

