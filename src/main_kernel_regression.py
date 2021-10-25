import time
from tqdm import tqdm
from grayord_utils import visdata_grayord, vis_grayord_sigpval
from stats_utils import kernel_regression
from statsmodels.stats.multitest import fdrcorrection
from sklearn.decomposition import PCA
from brainsync import normalizeData, brainSync
import scipy.io as spio
import scipy as sp
import numpy as np
from surfproc import view_patch_vtk, patch_color_attrib, smooth_surf_function, smooth_patch
from utils_oasis3 import read_oasis3_data
from dfsio import readdfs
import os
import sys
import glob
sys.path.append('../BrainSync')
# ### Set the directorie
# s for the data and BFP software
# In[2]:

BFPPATH = '/home/ajoshi/projects/bfp'
FSL_PATH = '/usr/share/fsl/5.0'
# study directory where all the grayordinate files lie
DATA_DIR = '/deneb_disk/bfp_oasis3'


# ### Read CSV file to read the group IDs. This study has three subgroups:
# 1. Normal controls,
# 2. ADHD-hyperactive, and
# 3. ADHD-inattentive.
LEN_TIME = 164  # length of the time series
NUM_SUB = 35  # Number of subjects for the study


def main():

    print('Reading subjects')

    s = glob.glob('/home/ajoshi/projects/AD_processing/csv_files/*.csv')

    for i in range(len(s)):

        measure = s[i][57:-4]
        CSV_FILE = s[i]

        print('Reading subjects')
        _, reg_var, sub_files = read_oasis3_data(csv_fname=CSV_FILE,
                                                 data_dir=DATA_DIR,
                                                 reg_var_name=measure,
                                                 num_sub=NUM_SUB,
                                                 len_time=LEN_TIME)

        # Shuffle reg_var and subjects for testing
        #reg_var = np.random.permutation(reg_var)
        #ran_perm = sp.random.permutation(len(reg_var))
        #reg_var = reg_var
        #sub_files = [sub_files[i] for i in range(len(reg_var))]

        t0 = time.time()
        print('performing stats based on kernel regression')

        pval, pval_fdr, pval_max, pval_kr_ftest, pval_kr_ftest_fdr = kernel_regression(
            bfp_path=BFPPATH,
            sub_files=sub_files,
            reg_var=reg_var,
            nperm=2000,
            len_time=LEN_TIME,
            num_proc=1,
            fdr_test=False,
            simulation=False)
        t1 = time.time()

        print(t1 - t0)
        np.savez(
            'pval_KR'+measure+'.npz',
            pval=pval,
            pval_fdr=pval_fdr,
            pval_max=pval_max)
    
        print('Results saved')


if __name__ == "__main__":
    main()
