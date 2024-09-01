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


BFPPATH = "/home/ajoshi/projects/BrainSuite/bfp"
FSL_PATH = "/usr/share/fsl/5.0"
# study directory where all the grayordinate files lie
DATA_DIR = "/deneb_disk/bfp_oasis3"

NUM_VERT = 96854


def main():
    smth = 0
    NUM_SUB = 3500  # Number of subjects for the study

    s = glob.glob(
        "/home/ajoshi/Projects/AD_processing/src/outputs/oasis3_bfp_mmse_pvc_th_smooth.csv"
    )

    measure = "num_mmse"
    CSV_FILE = s[0]

    _, reg_var, sub_files = read_oasis3_thickness(
        csv_fname=CSV_FILE,
        data_dir=DATA_DIR,
        reg_var_name=measure,
        reg_var_positive=True,
        num_sub=NUM_SUB,
        good_subs_list='good_subids.txt'
    )

    # plot histogram of the number of measurements Only have integers on x axis. Plot in grayscale
    import matplotlib.pyplot as plt
    plt.hist(reg_var,color='gray', bins=20, edgecolor='black')
    plt.xticks(np.arange(0, 20, 1))
    plt.xlabel('Number of MMSE measurements')
    plt.ylabel('Number of subjects')
    plt.title('Histogram of number of MMSE measurements')
    #make the image grayscale
    plt.set_cmap('gray')
    plt.savefig('outputs/histogram_num_mmse_measurements.png')
    plt.show()



if __name__ == "__main__":
    main()
