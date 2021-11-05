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

    a = np.load('AD_conn_AJC_sub1_rest.npz')
    conn_mat = a['conn_mat']
    conn_NC = conn_mat

    a = np.load('AD_conn_AJC_sub1_left_finger.npz')
    conn_mat = a['conn_mat']
    conn_lf = conn_mat

    a = np.load('AD_conn_AJC_sub1_reach.npz')
    conn_mat = a['conn_mat']
    conn_lr = conn_mat

    fig, axes = plt.subplots(nrows=1, ncols=3)

    ax0 = axes.flat[0]
    im = ax0.imshow(conn_NC,vmin=0, vmax=1)
    ax0.set_title('Rest')
    ax0.set_xticks(range(conn_mat.shape[0]))
    ax0.set_yticks(range(conn_mat.shape[1]))


    ax1 = axes.flat[1]
    im = ax1.imshow(conn_lf,vmin=0, vmax=1)
    ax1.set_title('LeftFinger')
    ax1.set_xticks(range(conn_mat.shape[0]))
    ax1.set_yticks(range(conn_mat.shape[1]))

    ax2 = axes.flat[2]
    im = ax2.imshow(conn_lr,vmin=0, vmax=1)
    ax2.set_title('LeftReach')
    ax2.set_xticks(range(conn_mat.shape[0]))
    ax2.set_yticks(range(conn_mat.shape[1]))


    plt.colorbar(im,ax=axes.ravel().tolist())

    plt.show()

    p_ad_mci = np.zeros(conn_mat.shape[:2])
    p_nc_mci = np.zeros(conn_mat.shape[:2])
    p_ad_nc = np.zeros(conn_mat.shape[:2])




if __name__ == "__main__":
    main()