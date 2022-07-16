#Intro to GLM Analysis: a single-session, single-subject fMRI dataset
#=====================================================================
from nilearn import image
import matplotlib.pyplot as plt
import scipy.io as spio
import numpy as np
from brainsync import normalizeData, brainSync
from grayord_utils import visdata_grayord, vis_grayord_sigpval

fdata = '/home/ajoshi/sub08001/func/sub08001_rest_bold.ALFF_Z.GOrd.mat'

data = spio.loadmat(fdata)['data'].squeeze()

BFPPATH = '/home/ajoshi/projects/bfp'
FSL_PATH = '/home/ajoshi/webware/fsl'

visdata_grayord(data, # - 1000*(1.-rejected),
                surf_name='ALFF_Z',
                out_dir='.',
                smooth_iter=1000,
                colorbar_lim=[-1, 1],
                colormap='jet',
                save_png=True,
                bfp_path=BFPPATH,
                fsl_path=FSL_PATH)





print('done')