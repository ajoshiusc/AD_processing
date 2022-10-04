clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/ImagePTE1/ajoshi/code_farm/bfp/src'));
%    1050345 rest 2

studydir='/ImagePTE1/ajoshi/data/bfp_oasis3';

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

C = [subnamelist;sessionslist;runlist;t1list]';
%Process all subjects using BFP
writecell(C,'sub_used.csv');


good_sub_list = readtable('/home/ajoshi/projects/AD_processing/src/good_subids.txt','ReadVariableNames', false);



