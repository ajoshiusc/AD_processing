clc;clear all;close all;restoredefaultpath;
%addpath(genpath('/big_disk/ajoshi/coding_ground/bfp/supp_data'))
addpath(genpath('/ImagePTE1/ajoshi/code_farm/bfp/src'));


adrc = readmatrix('/ImagePTE1/ajoshi/code_farm/AD_processing/ADRC_Clinical_Data_aajoshi_5_14_2021_1_47_36.csv')

uds = readmatrix('/ImagePTE1/ajoshi/code_farm/AD_processing/oasis3_clinical_data.csv');

