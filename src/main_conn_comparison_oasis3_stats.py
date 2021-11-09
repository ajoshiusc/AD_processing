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
from numpy import std, mean, sqrt

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

#correct if the population S.D. is expected to be equal for the two groups.
def cohen_d(x,y):
    nx = len(x)
    ny = len(y)
    dof = nx + ny - 2
    return 2*np.abs(mean(x) - mean(y)) / sqrt(((nx-1)*std(x, ddof=1) ** 2 + (ny-1)*std(y, ddof=1) ** 2) / dof)

def main():

    afont = {'fontname':'Arial'}

    a = np.load('AD_conn.npz')
    conn_mat = a['conn_mat']
    mmse=a['reg_var']

    adind = np.where((mmse<29) & (mmse>26.5))[0]
    ncind = np.where(mmse>29)[0]
    
    conn_NC = conn_mat[:,:,ncind]
    conn_AD = conn_mat[:,:,adind]

    avg_conn_NC = np.mean(conn_NC,axis=2)
    avg_conn_AD = np.mean(conn_AD,axis=2)


    fig, axes = plt.subplots(nrows=1, ncols=2)

    ax0 = axes.flat[0]
    im = ax0.imshow(avg_conn_NC,vmin=0, vmax=1, cmap='hot')
    ax0.set_title('NC', fontsize=16,**afont)
    ax0.tick_params(axis='both', which='major', labelsize=16)
    ax0.set_xticks(range(conn_mat.shape[0]))
    ax0.set_yticks(range(conn_mat.shape[1]))

    ax2 = axes.flat[1]
    im = ax2.imshow(avg_conn_AD,vmin=0, vmax=1, cmap='hot')
    ax2.set_title('Mild AD', fontsize=16,**afont)
    ax2.tick_params(axis='both', which='major', labelsize=16)
    ax2.set_xticks(range(conn_mat.shape[0]))
    ax2.set_yticks(range(conn_mat.shape[1]))


    cbar = plt.colorbar(im,ax=axes.ravel().tolist())
    cbar.ax.tick_params(labelsize=16)

    plt.show()

    fig, axes = plt.subplots(nrows=1, ncols=1)

    p_ad_nc = np.zeros(conn_mat.shape[:2])
    d_ad_nc = np.zeros(conn_mat.shape[:2])

    for r,c in itertools.product(range(conn_mat.shape[0]),range(conn_mat.shape[1])):

        t, p_ad_nc[r,c] = ttest_ind(conn_NC[r,c,:],conn_AD[r,c,:])
        d_ad_nc[r,c] = cohen_d(conn_NC[r,c,:],conn_AD[r,c,:])

    ax2 = axes
    pval = p_ad_nc
    im = ax2.imshow(pval,vmin=0, vmax=.05, cmap='hot_r')
    ax2.set_title('AD_vs_NC', fontsize=16,**afont)
    ax2.tick_params(axis='both', which='major', labelsize=16)
    ax2.set_xticks(range(conn_mat.shape[0]))
    ax2.set_yticks(range(conn_mat.shape[1]))

    plt.show()


    fig, axes = plt.subplots(nrows=1, ncols=1)

    ax = axes
    im = ax.imshow(d_ad_nc,vmin=0, vmax=1, cmap='hot')
    ax.set_title('Cohen\'s d for AD_vs_NC', fontsize=16,**afont)
    ax.tick_params(axis='both', which='major', labelsize=16)

    ax.set_xticks(range(conn_mat.shape[0]))
    ax.set_yticks(range(conn_mat.shape[1]))


    cbar = plt.colorbar(im,ax=axes)
    cbar.ax.tick_params(labelsize=16)

    plt.show()


    


if __name__ == "__main__":
    main()