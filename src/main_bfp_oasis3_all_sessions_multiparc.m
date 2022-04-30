clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/home/ajoshi/projects/svreg_multiparc/src'));
%    1050345 rest 2
num_sub=50;
studydir='/deneb_disk/bfp_oasis3_timeseries';

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



        %fprintf('--------\n')

        t1=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{k-2},'anat',[subname,'_',sessions{k-2},'_run-01_T1w.nii.gz']);
        fmri=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{k-2},'func',[subname,'_',sessions{k-2},'_task-rest_run-02_bold.nii.gz']);

        if ~exist(t1,'file')
            t1=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{k-2},'anat',[subname,'_',sessions{k-2},'_T1w.nii.gz']);
        end

        if ~exist(fmri,'file')
            fmri=fullfile('/ImagePTE1/ajoshi/data/oasis3_bids/',subname,sessions{k-2},'func',[subname,'_',sessions{k-2},'_task-rest_bold.nii.gz']);
            runname='run_00';
        else
            runname='run_02';
        end

        if exist(t1,'file')  &&  exist(fmri,'file')
            s=s+1;
            disp(subname);

            t1list{s}=t1;
            fmrilist{s}=fmri;
            sessionslist{s}=sessions{k-2};
            subnamelist{s}=subname;
            runlist{s}=runname;
        end
    end
end

%Process all subjects using BFP
delete(gcp('nocreate'));
parpool(6);
parfor s = 1:length(subnamelist(1:num_sub))
    try

        uscbrain_multi_atlas = '/ImagePTE1/ajoshi/code_farm/svreg/USCBrainMulti';
        BrainSuitePath='/home/ajoshi/BrainSuite21a';
        subid=[subnamelist{s},'_',sessionslist{s},'_',runlist{s}];
        subdir=fullfile(studydir,subid);
        anatDir=fullfile(subdir,'anat');
        subbasename=fullfile(anatDir,sprintf('%s_T1w',subid));
        svreg_multiparc(subbasename,uscbrain_multi_atlas,BrainSuitePath,'Entorhinal');
        svreg_multiparc(subbasename,uscbrain_multi_atlas,BrainSuitePath,'Perirhinal');

    catch
        fprintf('subject failed:%d  %s',s,subnamelist{s});
    end
end

