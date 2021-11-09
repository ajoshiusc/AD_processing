import scipy.io as spio
import scipy as sp
import numpy as np
from surfproc import view_patch_vtk, patch_color_attrib, smooth_surf_function, smooth_patch
from dfsio import readdfs
import os
import sys
from brainsync import normalizeData, brainSync
from sklearn.decomposition import PCA
from statsmodels.stats.multitest import fdrcorrection
from stats_utils import randpairs_regression
#from dev_utils import read_fcon1000_data
from utils_oasis3 import read_oasis3_data
from grayord_utils import visdata_grayord, vis_grayord_sigpval
# ### Set the directorie
# s for the data and BFP software
from tqdm import tqdm
import time
import glob
import scipy as sp

BFPPATH = '/home/ajoshi/projects/bfp'
FSL_PATH = '/usr/share/fsl/5.0'
# study directory where all the grayordinate files lie
DATA_DIR = '/deneb_disk/bfp_oasis3'

# ### Read CSV file to read the group IDs. This study has three subgroups:
# 1. Normal controls,
# 2. ADHD-hyperactive, and
# 3. ADHD-inattentive.

LEN_TIME = 164  # length of the time series
NUM_SUB = 350  # Number of subjects for the study

rois = [147, 225, 373, 247, 186, 187, 188, 189, 227, 145]


def main():

    s = glob.glob(
        '/home/ajoshi/projects/AD_processing/csv_files/oasis3_bfp_mmse.csv')

    atlas = spio.loadmat(
        '/home/ajoshi/projects/bfp/supp_data/USCBrain_grayordinate_labels.mat')

    labs = atlas['labels']
    labs = np.mod(labs, 1000)
    labs = np.squeeze(labs)

    dtseries = np.zeros((LEN_TIME, len(rois)))
    conn_mat = np.zeros((len(rois), len(rois), NUM_SUB))

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
        #reg_var = sp.random.permutation(reg_var)

        #ran_perm = sp.random.permutation(len(reg_var))
        #reg_var = reg_var
        #sub_files = [sub_files[i] for i in ran_perm]

        for sind, f in enumerate(sub_files):
            sub1_data = spio.loadmat(f)['dtseries'].T

            for i, r in enumerate(rois):
                dtseries[:, i] = np.mean(sub1_data[:LEN_TIME,
                                                   np.where(labs == r)[0]],
                                         axis=1)

            sub1_data, _, _ = normalizeData(dtseries)

            conn_mat[:, :, sind] = np.matmul(sub1_data.T, sub1_data)

    np.savez('AD_conn', conn_mat=conn_mat, reg_var=reg_var)
    print('Results saved')


if __name__ == "__main__":
    main()