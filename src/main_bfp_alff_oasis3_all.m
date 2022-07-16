clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/home/ajoshi/projects/bfp/src'));
%    1050345 rest 2

studydir='/deneb_disk/bfp_oasis3';
TR='';
% Set the input arguments
configfile='/home/ajoshi/projects/AD_processing/src/config_bfp_preproc.ini';

subdir='/ImagePTE1/ajoshi/data/oasis3_bids';
l=dir(subdir);

s=0;
for j=3:length(l)
    subname=l(j).name;
    
    l2=dir(fullfile(subdir,subname));
    
    sessions={};
    for k=3:length(l2)
        
        sessions{k-2}=l2(k).name;
        
        % fprintf('%s %s\n',subname,sessions{k-2});
        
    end
    
    %fprintf('--------\n')
    
    t1=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{1},'anat',[subname,'_',sessions{1},'_run-01_T1w.nii.gz']);
    fmri=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{1},'func',[subname,'_',sessions{1},'_task-rest_run-02_bold.nii.gz']);
    
    if ~exist(t1,'file')
        t1=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{1},'anat',[subname,'_',sessions{1},'_T1w.nii.gz']);
    end
    
    if ~exist(fmri,'file')
        fmri=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{1},'func',[subname,'_',sessions{1},'_task-rest_bold.nii.gz']);
        runname='run_00';
    else
        runname='run_02';
    end
    
    if exist(t1,'file')  &&  exist(fmri,'file')
        s=s+1;
        disp(subname);
 
        t1list{s}=t1;
        fmrilist{s}=fmri;
        sessionslist{s}=sessions{1};
        subnamelist{s}=subname;
        runlist{s}=runname;
    end
end


config.FSLPATH = '/home/ajoshi/webware/fsl'
config.FSLOUTPUTTYPE='NIFTI_GZ';
config.AFNIPATH = '/home/ajoshi/abin';
config.FSLRigidReg=0;
config.MultiThreading=0;
config.BFPPATH='/home/ajoshi/projects/bfp';

%Process all subjects using BFP
parpool(6);
parfor s = 1:length(subnamelist)
    %try
        bfp(configfile, t1list{s}, fmrilist{s}, studydir, [subnamelist{s},'_',sessionslist{s},'_',runlist{s}], 'rest',TR);

        subid = [subnamelist{s},'_',sessionslist{s},'_',runlist{s}];
        fmribase = fullfile(studydir,subid,'func',[subid,'_rest_bold']);
        anatbase = fullfile(studydir,subid,'anat',[subid,'_T1w']);

        %function gen_alff_gord()
        get_alff_gord(config, fmribase, anatbase)

    %catch
    %    fprintf('subject failed:%d  %s',s,subnamelist{s});
    %end
end

