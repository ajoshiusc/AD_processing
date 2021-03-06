clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/home/ajoshi/projects/bfp/src'));
%    1050345 rest 2

% Set the input arguments
configfile='/home/ajoshi/projects/AD_processing/src/config_bfp_preproc.ini';

t1='/ImagePTE1/ajoshi/oasis3_bids/sub-OAS30001/ses-d0129/anat/sub-OAS30001_ses-d0129_run-02_T1w.nii.gz';

fmri='/ImagePTE1/ajoshi/oasis3_bids/sub-OAS30001/ses-d0129/func/sub-OAS30001_ses-d0129_task-rest_run-02_bold.nii.gz';

%fmri='/home/ajoshi/Downloads/BFP_issues/ACTL005/ACTL005.BOLD.resting.nii.gz';
%studydir='/ImagePTE1/ajoshi/bfp_oasis3';
studydir='/deneb_disk/bfp_oasis3';

subid='sub-OAS30001';
sessionid='ses-d0129';
TR='';
 
% Call the bfp function
%bfp(configfile, t1, fmri, studydir, subid, sessionid,TR);
bfp(configfile, t1, fmri, studydir, [subid,'_',sessionid,'_run_02'], 'rest',TR);

%bfp.sh config.ini input/sub08001/anat/mprage_anonymized.nii.gz /big_disk/ajoshi/bfp_sample/input/sub08001/func/rest.nii.gz /big_disk/ajoshi/bfp_sample/output sub11 rest 2
