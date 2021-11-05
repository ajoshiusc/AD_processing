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

rois = [147, 225, 373, 247, 186, 187, 188, 189, 227, 145]

#fname = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-22-2021/func/10-22-2021_016_left_finger_bold.32k.GOrd.filt.mat'
fname = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-22-2021/func/10-22-2021_025_resting_bold.32k.GOrd.filt.mat'
#fname = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-22-2021/func/10-22-2021_021_L_reach_bold.32k.GOrd.filt.mat'

def main():

    atlas = spio.loadmat('/ImagePTE1/ajoshi/code_farm/bfp/supp_data/USCBrain_grayordinate_labels.mat')

    labs = atlas['labels']
    labs = np.mod(labs,1000)
    labs = np.squeeze(labs)

    dtseries = np.zeros((LEN_TIME,len(rois)))
    conn_mat = np.zeros((len(rois),len(rois),NUM_SUB))

    sub1_data = spio.loadmat(fname)['dtseries'].T

    for i, r in enumerate(rois):
        dtseries[:,i] = np.mean(sub1_data[:LEN_TIME, np.where(labs==r)[0]],axis=1)
    
    sub1_data, _, _ = normalizeData(dtseries)

    conn_mat = np.matmul(sub1_data.T, sub1_data)

    #np.savez('AD_conn_AJC_sub1_left_finger.npz', conn_mat = conn_mat)
    np.savez('AD_conn_AJC_sub1_rest.npz', conn_mat = conn_mat)


if __name__ == "__main__":
    main()