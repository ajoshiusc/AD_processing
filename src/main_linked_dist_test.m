clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/home/ajoshi/projects/bfp/src'));


subbasename='/ImagePTE1/ajoshi/data/bfp_oasis3/sub-OAS30001_ses-d0129_run_02/anat/sub-OAS30001_ses-d0129_run_02_T1w';

GOrdSurfIndFile = '/home/ajoshi/projects/bfp/supp_data/bci_grayordinates_surf_ind.mat';
GOrdFile='temp.gord.mat';

a=tic;
linked_dist_gord(subbasename,GOrdSurfIndFile,GOrdFile);
toc(a)
