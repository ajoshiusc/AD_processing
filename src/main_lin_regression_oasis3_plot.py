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

BFPPATH = '/home/ajoshi/projects/bfp'
FSL_PATH = '/usr/share/fsl/5.0'
# study directory where all the grayordinate files lie
DATA_DIR = '/deneb_disk/bfp_oasis3'
CSV_FILE = '/home/ajoshi/projects/AD_processing/src/oasis3_bfp.csv'

# ### Read CSV file to read the group IDs. This study has three subgroups:
# 1. Normal controls,
# 2. ADHD-hyperactive, and
# 3. ADHD-inattentive.

LEN_TIME = 164  # length of the time series
NUM_SUB = 350  # Number of subjects for the study

measure = 'mmse'


def main():

    print('Reading subjects')

    #a = np.load('src/pval_num_pairs20000_nsub350_nperm2000_mmse_perm.npz')
    #a = np.load('src/pval_num_pairs20000_nsub_50_mmse_gt27_nperm2000_' + measure + '.npz')
    a = np.load('pval_num_pairs20000_mmse_all_nperm2000_mmse_filt.npz')

    power = a['power']
    rho = a['rho']
    effect = a['effect']
    estN = a['estN']
    corr_pval_max = a['corr_pval_max']
    corr_pval_fdr = a['corr_pval_fdr']

    # corr_pval_max=a['corr_pval_max']
    # corr_pval_fdr=a['corr_pval_fdr']
    corr_pval_max = corr_pval_max
    vis_grayord_sigpval(corr_pval_max,
                        surf_name='corr_perm_pairs20000_max_' +
                        measure,
                        out_dir='.',
                        smooth_iter=1000,
                        bfp_path=BFPPATH,
                        fsl_path=FSL_PATH,
                        sig_alpha=0.15)
    vis_grayord_sigpval(corr_pval_fdr,
                        surf_name='corr_perm_pairs20000_fdr' +
                        measure,
                        out_dir='.',
                        smooth_iter=1000,
                        bfp_path=BFPPATH,
                        fsl_path=FSL_PATH,
                        sig_alpha=0.15)

    visdata_grayord(rho,
                    surf_name='corr_perm_pairs20000_rho' + measure,
                    out_dir='.',
                    smooth_iter=000,
                    colorbar_lim=[0, .04],
                    colormap='jet',
                    save_png=True,
                    bfp_path=BFPPATH,
                    fsl_path=FSL_PATH)

    visdata_grayord(effect,
                    surf_name='corr_perm_pairs20000_effect' +
                    measure,
                    out_dir='.',
                    smooth_iter=1000,
                    colorbar_lim=[-1, 1],
                    colormap='jet',
                    save_png=True,
                    bfp_path=BFPPATH,
                    fsl_path=FSL_PATH)
    visdata_grayord(power,
                    surf_name='corr_perm_pairs20000_power' + measure,
                    out_dir='.',
                    smooth_iter=1000,
                    colorbar_lim=[0.95, 1],
                    colormap='jet',
                    save_png=True,
                    bfp_path=BFPPATH,
                    fsl_path=FSL_PATH)

    visdata_grayord(estN,
                    surf_name='corr_perm_pairs20000_estN' + measure,
                    out_dir='.',
                    smooth_iter=1000,
                    colorbar_lim=[0, 1000],
                    colormap='jet',
                    save_png=True,
                    bfp_path=BFPPATH,
                    fsl_path=FSL_PATH)
    print('Results saved')


if __name__ == "__main__":
    main()