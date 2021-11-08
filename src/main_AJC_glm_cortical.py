#Intro to GLM Analysis: a single-session, single-subject fMRI dataset
#=====================================================================
from nilearn import image
import matplotlib.pyplot as plt
import scipy.io as spio
import numpy as np
from brainsync import normalizeData, brainSync
from grayord_utils import visdata_grayord, vis_grayord_sigpval



class Subject_Data:
    pass

subject_data = Subject_Data()

#subject_data.gord = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-22-2021/func/10-22-2021_016_L_tap_bold.32k.GOrd.mat'
#subject_data.func = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-22-2021/func/10-22-2021_016_L_tap_bold.gms2standard.nii.gz'

subject_data.gord = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-29-2021/func/10-29-2021_009_L_pen_minimal_bold.32k.GOrd.mat'
subject_data.func = '/ImagePTE1/ajoshi/for_abhijit/bfp_out/10-29-2021/func/10-29-2021_009_L_pen_minimal_bold.gms2standard.nii.gz'

from nilearn.image import concat_imgs, mean_img
fmri_img = concat_imgs(subject_data.func)

import pandas as pd
events = pd.read_table('/ImagePTE1/ajoshi/code_farm/AD_processing/src/ajc_events.tsv')
events

from nilearn.glm.first_level import FirstLevelModel
fmri_glm = FirstLevelModel(t_r=.75,
                           noise_model='ar1',smoothing_fwhm=3,
                           standardize=True,
                           hrf_model='spm',
                           drift_model='cosine',
                           high_pass=.01)

###############################################################################
# Now that we have specified the model, we can run it on the :term:`fMRI` image
fmri_glm = fmri_glm.fit(fmri_img, events)

###############################################################################
# One can inspect the design matrix (rows represent time, and
# columns contain the predictors).
design_matrix = fmri_glm.design_matrices_[0]

plt.plot(design_matrix['active'])
plt.xlabel('scan')
plt.title('Expected Auditory Response')
plt.show()

e_haemo = design_matrix['active']

#from scipy.interpolate import interp1d

#f = interp1d(range(len(e_haemo)),e_haemo)
#e_haemo=f(np.arange(0,len(e_haemo),0.75))

e_haemo = np.array(e_haemo)
e_haemo, _, _ = normalizeData(e_haemo)

plt.plot(np.array(e_haemo))
plt.xlabel('scan')
plt.title('Expected  Response')
plt.show()



fdata = spio.loadmat(subject_data.gord)['dtseries'].T

fdata, _, _ = normalizeData(fdata)

#rho = np.sum(fdata * e_haemo[:,None],axis=0)
from scipy.stats import pearsonr
from tqdm import tqdm

rho = np.zeros(fdata.shape[1])
pval = np.zeros(fdata.shape[1])

for i in tqdm(range(fdata.shape[1])):
    rho[i], pval[i] = pearsonr(fdata[:,i],e_haemo)


from statsmodels.stats.multitest import fdrcorrection
rejected, pval_fdr = fdrcorrection(pval,alpha=0.01)


BFPPATH = '/ImagePTE1/ajoshi/code_farm/bfp'
FSL_PATH = '/usr/share/fsl/5.0'

visdata_grayord(rho, # - 1000*(1.-rejected),
                surf_name='sub3_corr_pen',
                out_dir='.',
                smooth_iter=1000,
                colorbar_lim=[-1, 1],
                colormap='jet',
                save_png=True,
                bfp_path=BFPPATH,
                fsl_path=FSL_PATH)



print('done')