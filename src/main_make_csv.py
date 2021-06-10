#||AUM||
#||Shree Ganeshaya Namaha||
import csv
import os
import pandas as pd

s = os.listdir('/deneb_disk/bfp_oasis3')
sub_ids = list()

for n in range(len(s)):
    gord_fname = os.path.join('/deneb_disk/bfp_oasis3', s[n],'func',s[n]+'_rest_bold.32k.GOrd.filt.mat')

    if os.path.exists(gord_fname):
        sub_ids.append(s[n][4:12])
    
print(sub_ids)




csvname1 = '/ImagePTE1/ajoshi/code_farm/AD_processing/oasis3_clinical_data.csv'
csvname2 = '/ImagePTE1/ajoshi/code_farm/AD_processing/ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv'

df1 = pd.read_csv(csvname1,index_col='Subject')
df2 = pd.read_csv(csvname2,index_col='Subject')

data1 = df1['M/F'][sub_ids]
data2 = df1['UDS B9: Clin. Judgements'][sub_ids]
data3 = df2['ageAtEntry'][sub_ids]

result = pd.merge(left=data1,right=data3,on='Subject')
result = pd.merge(left=result,right=data2,on='Subject')

print(result)

result.rename(columns={'ageAtEntry':'Age', 'M/F':'gender', 'UDS B9: Clin. Judgements':'UDSB9'},inplace=True)

result.to_csv('oasis3_bfp.csv')

print('done')


