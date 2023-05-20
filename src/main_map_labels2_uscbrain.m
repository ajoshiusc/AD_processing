clc;clear all;close all;restoredefaultpath;
addpath(genpath('/home/ajoshi/projects/svreg/src'));
addpath(genpath('/home/ajoshi/projects/svreg/3rdParty'));
addpath(genpath('/home/ajoshi/projects/svreg/MEX_Files'));

BrainSuitePath = '/home/ajoshi/BrainSuite19b';
atlasbasename = fullfile(BrainSuitePath,'svreg','BCI-DNI_brain_atlas','BCI-DNI_brain');

subject_mri = '/home/ajoshi/Downloads/Anand/c9397AD_LE/c9397AD_LE.nii.gz';
data_file = '/home/ajoshi/Downloads/Anand/c9397AD_LE/c9397AD_LE.nii.gz'; % This file contains the data in the subject space to be mapped to the MNI space
out_file = '/home/ajoshi/Downloads/Anand/c9397AD_LE/c9397AD_LE.mapped2atlas.nii.gz'; % This file will contain data mapped to the MNI space


% Find path to the subject
mapping_exe = fullfile(BrainSuitePath,'svreg','bin','svreg_apply_map.sh');
[pth,subbasename,ext] = fileparts(subject_mri);

if strcmp(subbasename(end-3:end),'.nii')
    subbasename = fullfile(pth,subbasename(1:end-4));
else
    subbasename = fullfile(pth,subbasename);
end

% This map is computed when you run BrainSuite cortical extraction and
% SVREg sequence on the subject MRI. This can take data from subject space
% to the BCI-DNI space
map2atlas = [subbasename,'.svreg.inv.map.nii.gz'];

atlas_pth = fileparts(atlasbasename);
% This takes data from BCI-DNI space to the MNI space
mni2bcimap = fullfile(atlas_pth,'mni2bci.map.nii.gz');

% Map data from subject to the BCI-DNI atlas
system([mapping_exe,' ',map2atlas,' ',data_file,' ',out_file,' ',[atlasbasename,'.pvc.frac.nii.gz'],' ','0 "" "" ','cubic']);

% Map data from BCI-DNI atlas to MNI space
system([mapping_exe,' ',mni2bcimap,' ',out_file,' ',out_file,' ',fullfile(BrainSuitePath,'svreg','BrainSuiteAtlas1','mri.pvc.frac.nii.gz'),' ','0 "" "" ','cubic']);

