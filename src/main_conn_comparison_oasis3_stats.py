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
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import itertools

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

    a = np.load('AD_conn.npz')
    conn_mat = a['conn_mat']
    cdr=a['cdr']

    ncind = np.where(cdr < 0.5)[0]
    mciind = np.where((cdr > 0.5) & (cdr < 1))[0]
    adind = np.where((cdr > 1.5))[0]
    
    conn_NC = conn_mat[:,:,ncind]
    conn_MCI = conn_mat[:,:,mciind]
    conn_AD = conn_mat[:,:,adind]

    avg_conn_NC = np.mean(conn_NC,axis=2)
    avg_conn_MCI = np.mean(conn_MCI,axis=2)
    avg_conn_AD = np.mean(conn_AD,axis=2)


    fig, axes = plt.subplots(nrows=1, ncols=3)

    ax0 = axes.flat[0]
    im = ax0.imshow(avg_conn_NC,vmin=0, vmax=1)
    ax0.set_title('NC')
    ax0.set_xticks(range(conn_mat.shape[0]))
    ax0.set_yticks(range(conn_mat.shape[1]))


    ax1 = axes.flat[1]
    im = ax1.imshow(avg_conn_MCI,vmin=0, vmax=1)
    ax1.set_title('MCI')
    ax1.set_xticks(range(conn_mat.shape[0]))
    ax1.set_yticks(range(conn_mat.shape[1]))

    ax2 = axes.flat[2]
    im = ax2.imshow(avg_conn_AD,vmin=0, vmax=1)
    ax2.set_title('AD')
    ax2.set_xticks(range(conn_mat.shape[0]))
    ax2.set_yticks(range(conn_mat.shape[1]))


    plt.colorbar(im,ax=axes.ravel().tolist())

    plt.show()

    p_ad_mci = np.zeros(conn_mat.shape[:2])
    p_nc_mci = np.zeros(conn_mat.shape[:2])
    p_ad_nc = np.zeros(conn_mat.shape[:2])

    for r,c in itertools.product(range(conn_mat.shape[0]),range(conn_mat.shape[1])):

        t, p_ad_mci[r,c] = ttest_ind(conn_NC[r,c,:],conn_MCI[r,c,:])
        t, p_nc_mci[r,c] = ttest_ind(conn_NC[r,c,:],conn_MCI[r,c,:])
        t, p_ad_nc[r,c] = ttest_ind(conn_NC[r,c,:],conn_MCI[r,c,:])


    fig, axes = plt.subplots(nrows=1, ncols=3)

    ax0 = axes.flat[0]
    im = ax0.imshow(p_nc_mci,vmin=0, vmax=.05)
    ax0.set_title('NC_vs_MCI')
    ax0.set_xticks(range(conn_mat.shape[0]))
    ax0.set_yticks(range(conn_mat.shape[1]))

    ax1 = axes.flat[1]
    im = ax1.imshow(p_ad_mci,vmin=0, vmax=.05)
    ax1.set_title('AD_vs_MCI')
    ax1.set_xticks(range(conn_mat.shape[0]))
    ax1.set_yticks(range(conn_mat.shape[1]))

    ax2 = axes.flat[2]
    im = ax2.imshow(p_ad_nc,vmin=0, vmax=.05)
    ax2.set_title('AD_vs_NC')
    ax2.set_xticks(range(conn_mat.shape[0]))
    ax2.set_yticks(range(conn_mat.shape[1]))

    plt.colorbar(im,ax=axes.ravel().tolist())

    plt.show()


    


if __name__ == "__main__":
    main()