#||AUM||
#||Shree Ganeshaya Namaha||
import csv
import os
import pandas as pd

s = os.listdir('/deneb_disk/bfp_oasis3')
sub_ids = list()
sub_clinical_ids = list()

gord_fname_list = list()

for n in range(len(s)):
    gord_fname = os.path.join('/deneb_disk/bfp_oasis3', s[n],'anat',s[n]+'_T1w.SCT.GOrd.mat')

    if os.path.exists(gord_fname):
        sub_ids.append(s[n][4:12])
        sub_clinical_ids.append(s[n][4:12]+'_MR_'+s[n][17:22])
        gord_fname_list.append(gord_fname)
    
print(sub_ids)



csvname1 = '/ImagePTE1/ajoshi/code_farm/AD_processing/oasis3_clinical_data.csv'
csvname2 = '/ImagePTE1/ajoshi/code_farm/AD_processing/oasis3_MR_scans.csv'

df1 = pd.read_csv(csvname1,index_col='Subject')
df2 = pd.read_csv(csvname2,index_col='Label')

data1 = df1['M/F'][sub_ids]
data2 = df1['UDS B9: Clin. Judgements'][sub_ids]
data3 = df2['Age'][sub_clinical_ids]
data3.index = sub_ids # Change the index to the subject id
data3.index.name = 'Subject'

"""
data4 = data3.copy()
data4[:] = gord_fname_list
data4.index.name = 'Filename'
"""
d={'FileName':gord_fname_list}
data4 = pd.DataFrame(index=data2.index.copy(), data=d)
result = pd.merge(left=data1, right=data3, on='Subject')
result = pd.merge(left=result, right=data2, on='Subject')
result = pd.merge(left=result, right=data4, on='Subject')


print(result)

result.rename(columns={'M/F':'Gender', "UDS B9: Clin. Judgements":'UDSB9'},inplace=True)

result.to_csv('oasis3_bfp_SCT.csv')

print('done')


