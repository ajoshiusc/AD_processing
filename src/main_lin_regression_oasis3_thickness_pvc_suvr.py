import scipy.io as spio
import scipy as sp
import numpy as np
from surfproc import (
    view_patch_vtk,
    patch_color_attrib,
    smooth_surf_function,
    smooth_patch,
)
from dfsio import readdfs
import os
import sys
from brainsync import normalizeData, brainSync
from sklearn.decomposition import PCA
from statsmodels.stats.multitest import fdrcorrection
from stats_utils import randpairs_regression

# from dev_utils import read_fcon1000_data
from utils_oasis3 import read_oasis3_thickness
from grayord_utils import visdata_grayord, vis_grayord_sigpval

# ### Set the directorie
# s for the data and BFP software
from tqdm import tqdm
import time
import glob
import scipy as sp
from scipy.stats import pearsonr
import matplotlib.pyplot as plt


BFPPATH = "/home/ajoshi/Projects/bfp"
FSL_PATH = "/usr/share/fsl/5.0"
# study directory where all the grayordinate files lie
DATA_DIR = "/deneb_disk/bfp_oasis3"

NUM_VERT = 96854

csv_file = "/home/ajoshi/Projects/AD_processing/csv_files/OASIS_all_subjects_with_mmse_cdr_avgs_suvr_closest_clinical_day_mmse_cdr.csv"

def main():
    smth = 0
    NUM_SUB = 3500  # Number of subjects for the study

    s = glob.glob(csv_file)
    

    measure = "closest_day_suvr_value" #"mmse_avg"
    CSV_FILE = s[0]

    _, reg_var, sub_files = read_oasis3_thickness(
        csv_fname=CSV_FILE,
        data_dir=DATA_DIR,
        reg_var_name=measure,
        reg_var_positive=True,
        num_sub=NUM_SUB,
        good_subs_list='good_subids.txt'
    )

    ind = np.where(reg_var > 0*25)[0]
    ind_mapping = map(sub_files.__getitem__, ind)
    sub_files = list(ind_mapping)
    reg_var = reg_var[ind]
    #reg_var = np.random.permutation(reg_var)

    NUM_SUB = len(sub_files)
    thickness_all = np.zeros((NUM_VERT, NUM_SUB))

    print("Reading subjects")

    for i in tqdm(range(NUM_SUB)):

        f = spio.loadmat(sub_files[i])
        th = f["data"]
        thickness_all[:, i] = th.squeeze()

    ind = ~np.isfinite(np.sum(thickness_all, axis=1))
    thickness_all[ind, :] = 0
    corr_val = np.zeros(NUM_VERT)
    corr_pval = np.zeros(NUM_VERT)

    print("Calculating correlation")
    for v in tqdm(range(NUM_VERT)):
        corr_val[v], corr_pval[v] = pearsonr(thickness_all[v, :], reg_var)

    ind = np.isfinite(corr_pval)
    corr_pval_fdr = np.ones(corr_pval.shape)
    _, corr_pval_fdr[ind] = fdrcorrection(corr_pval[ind])

    vis_grayord_sigpval(
        pval=corr_pval,
        sig_alpha=0.05,
        surf_name="thickness_pvc_smooth" + str(smth),
        out_dir="outputs",
        smooth_iter=0,
        bfp_path=BFPPATH,
        fsl_path=FSL_PATH,
    )
    vis_grayord_sigpval(
        pval=corr_pval_fdr,
        sig_alpha=0.05,
        surf_name="thickness_pvc_smooth" + str(smth) + "fdr",
        out_dir="outputs",
        smooth_iter=0,
        bfp_path=BFPPATH,
        fsl_path=FSL_PATH,
    )

    print("Results saved")

    fig, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    axs.hist(corr_val, bins=100)
    plt.savefig('mmse_hist.png')
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()
