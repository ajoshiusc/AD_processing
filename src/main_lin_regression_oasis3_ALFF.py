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
from utils_oasis3 import read_oasis3_ALFF, read_oasis3_ALFF
from grayord_utils import visdata_grayord, vis_grayord_sigpval

# ### Set the directorie
# s for the data and BFP software
from tqdm import tqdm
import time
import glob
import scipy as sp
from scipy.stats import pearsonr


BFPPATH = "/home/ajoshi/projects/bfp"
FSL_PATH = "/home/ajoshi/webware/fsl"
# study directory where all the grayordinate files lie
DATA_DIR = "/deneb_disk/bfp_oasis3"

NUM_VERT = 96854


def main():
    NUM_SUB = 3500  # Number of subjects for the study

    s = glob.glob("/home/ajoshi/projects/AD_processing/src/outputs/oasis3_bfp_falff_smooth.csv")

    measure = "mmse"
    CSV_FILE = s[0]

    _, reg_var, sub_files = read_oasis3_ALFF(
        csv_fname=CSV_FILE,
        data_dir=DATA_DIR,
        reg_var_name=measure,
        reg_var_positive=False,
        num_sub=NUM_SUB,
        good_subs_list='good_subids.txt'
    )

    ind = np.where(reg_var > 25)[0]
    ind_mapping = map(sub_files.__getitem__, ind)
    sub_files = list(ind_mapping)
    reg_var = reg_var[ind]
    #reg_var = np.random.permutation(reg_var)

    NUM_SUB = len(sub_files)
    ALFF_all = np.zeros((NUM_VERT, NUM_SUB))

    print("Reading subjects")

    for i in tqdm(range(NUM_SUB)):

        f = spio.loadmat(sub_files[i])
        th = f["data"]
        ALFF_all[:, i] = th.squeeze()

    ind = ~np.isfinite(np.sum(ALFF_all, axis=1))
    ALFF_all[ind, :] = 0
    corr_val = np.zeros(NUM_VERT)
    corr_pval = np.zeros(NUM_VERT)

    print("Calculating correlation")
    for v in tqdm(range(NUM_VERT)):
        corr_val[v], corr_pval[v] = pearsonr(ALFF_all[v, :], reg_var)

    ind = np.isfinite(corr_pval)
    corr_pval_fdr = np.ones(corr_pval.shape)
    _, corr_pval_fdr[ind] = fdrcorrection(corr_pval[ind])

    vis_grayord_sigpval(
        pval=corr_pval,
        sig_alpha=0.05,
        surf_name="fALFF_smooth",
        out_dir="outputs",
        smooth_iter=0,
        bfp_path=BFPPATH,
        fsl_path=FSL_PATH,
    )
    vis_grayord_sigpval(
        pval=corr_pval_fdr,
        sig_alpha=0.05,
        surf_name="fALFF_smooth_fdr",
        out_dir="outputs",
        smooth_iter=0,
        bfp_path=BFPPATH,
        fsl_path=FSL_PATH,
    )

    print("Results saved")


if __name__ == "__main__":
    main()
