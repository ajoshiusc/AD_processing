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
        sessionslist{s}=sessions{1}(5:end);
        subnamelist{s}=subname(5:end);
        runlist{s}=runname;
    end
end

C = [subnamelist;sessionslist;runlist;t1list]';
%Process all subjects using BFP
writecell(C,'sub_used.csv');


good_sub_list = readtable('/home/ajoshi/projects/AD_processing/src/good_subids.txt','ReadVariableNames', false);

adrc=readtable('/home/ajoshi/projects/AD_processing/ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv');
mrscans = readtable('/home/ajoshi/projects/AD_processing/oasis3_MR_scans.csv');
mr_subjects=cell(height(mrscans),1);
mr_sessions=cell(height(mrscans),1);

for i = 1:height(mrscans)
    mr_sessions{i}=mrscans.Label{i}(end-4:end);
    mr_subjects{i}=mrscans.Label{i}(1:8);
end



adrc_sessions=cell(height(adrc),1);
for i = 1:height(adrc)
    adrc_sessions{i}=adrc.Label{i}(end-4:end);
end

good_sub_list = table2array(good_sub_list);


Subject={};
for s=1:length(good_sub_list)
    subname = good_sub_list{s};
    adrc_indices = find(strcmp(adrc{:,3},subname));
    sub_sessions = adrc_sessions(adrc_indices);
    cind = find(strcmp(C(:,1),subname));

    mrscans_indices = find(strcmp(mr_subjects,subname));
    mr_sessions_sub = mr_sessions(mrscans_indices);
    ind = find(strcmp(mr_sessions_sub,C{cind,2}));


    Subject{s} = subname;
    Session{s} = C{cind,2};
    Run{s} = C(cind,3);
    T1file{s} = C(cind,4);

    mmse{s} = mean(adrc.mmse(adrc_indices));
    cdr{s} = mean(adrc.cdr(adrc_indices));
    Age{s} = mrscans.Age(mrscans_indices(ind));
    M_F{s} = mrscans.M_F(mrscans_indices(ind));
    Hand{s} = mrscans.Hand(mrscans_indices(ind));

end
Subject = Subject';
Session = Session';
M_F = M_F';
Age = Age';
Hand = Hand';
T1file=T1file';mmse=mmse';cdr=cdr';
T=table(Subject,Session,Age,M_F,Hand,T1file,mmse,cdr);
writetable(T,'OASIS3_T1files_used_by_Anand_10_05_2022.csv');

