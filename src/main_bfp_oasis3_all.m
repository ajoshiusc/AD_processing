clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/ImagePTE1/ajoshi/code_farm/bfp/src'));
%    1050345 rest 2

studydir='/ImagePTE1/ajoshi/bfp_oasis3';
TR='';
% Set the input arguments
configfile='/ImagePTE1/ajoshi/code_farm/AD_processing/src/config_bfp_preproc.ini';

subdir='/ImagePTE1/ajoshi/oasis3_bids';
l=dir(subdir);

s=0;
parpool(6);
for j=3:length(l)
    subname=l(j).name;
    
    l2=dir(fullfile(subdir,subname));
    
    sessions={};
    for k=3:length(l2)
        
        sessions{k-2}=l2(k).name;
        
        % fprintf('%s %s\n',subname,sessions{k-2});
        
    end
    
    %fprintf('--------\n')
    
    t1=fullfile('/ImagePTE1/ajoshi/oasis3_bids/',subname,sessions{1},'anat',[subname,'_',sessions{1},'_run-01_T1w.nii.gz']);
    fmri=fullfile('/ImagePTE1/ajoshi/oasis3_bids/',subname,sessions{1},'func',[subname,'_',sessions{1},'_task-rest_run-01_bold.nii.gz']);
    
    if ~exist(t1,'file')
        t1=fullfile('/ImagePTE1/ajoshi/oasis3_bids/',subname,sessions{1},'anat',[subname,'_',sessions{1},'_T1w.nii.gz']);
    end
    
    if ~exist(fmri,'file')
        fmri=fullfile('/ImagePTE1/ajoshi/oasis3_bids/',subname,sessions{1},'func',[subname,'_',sessions{1},'_task-rest_bold.nii.gz']);
    end
    
    if exist(t1,'file')  &&  exist(fmri,'file')
        s=s+1;
        disp(subname);
 
        t1list{s}=t1;
        fmrilist{s}=fmri;
        sessionslist{s}=sessions{1};
        subnamelist{s}=subname;
    end
end

%Process 300 subjects using BFP
parfor s = 1:5%300
    try
        bfp(configfile, t1list{s}, fmrilist{s}, studydir, subnamelist{s}, sessionslist{s},TR);
    catch 
        fprintf('subject failed:%d  %s',s,subnamelist{s});
    end
end

