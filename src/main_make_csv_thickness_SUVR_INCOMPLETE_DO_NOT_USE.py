import csv
import os
import pandas as pd
import numpy as np
from tqdm import tqdm

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


csvname1 = "/home/ajoshi/Projects/AD_processing/csv_files/OASIS3_PUP.csv"
csvname2 = "../oasis3_MR_scans.csv"
csvname3 = "/home/ajoshi/Projects/AD_processing/csv_files/ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv"


measure = "PET_fSUVR_rsf_TOT_CORTMEAN"
measure_mmse = "mmse"
#measure_short = measure.replace(".", "").replace(" ", "").replace(":", "_")


df1 = pd.read_csv(csvname1, index_col="MRId")
df2 = pd.read_csv(csvname2, index_col="Label")

df3 = pd.read_csv(csvname3, index_col="Label")

data1 = df2["M/F"][sub_mr_ids]

data_suvr = np.zeros(len(sub_mr_ids))
data_mmse = np.zeros(len(sub_mr_ids))

all_suvr = df1[measure]
all_mmse = df3[measure_mmse]

pet_available = 0
pet_not_available = 0

pet_positives = 0



for i, s in enumerate(sub_mr_ids):

    # check if the all_suvr has s index
    if s not in all_suvr.index:
        print(f"{s} not in all_suvr")
        pet_not_available += 1
        continue

    pet_available += 1

    data_suvr[i] = np.mean(all_suvr[s])

    sub_clinical_id = s[0:8] + "_ClinicalData_" + s[12:18]
    data_mmse[i] = np.mean(all_mmse[sub_clinical_id])

    if data_suvr[i] > 1.42:
        pet_positives += 1


print(f"pet available: {pet_available}")
print(f"pet not available: {pet_not_available}")
print(f"pet positives: {pet_positives}")

data1 = pd.DataFrame(index=sub_ids, data={"sess":session_id, "M/F": data1, measure: data_suvr,"FileName": gord_fname_list})
data1.index.name = "Subject"

data1.to_csv("test.csv")

#data1.index = sub_ids  # Change the index to the subject id
#data1.index.name = "Subject"

