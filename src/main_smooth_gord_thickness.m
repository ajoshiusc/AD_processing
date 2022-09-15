clc;clear all;close all;
addpath(genpath('/ImagePTE1/ajoshi/code_farm/bfp/src'));

inp_dir='/ImagePTE1/ajoshi/data/thickness_data/thickness_fs_th';
out_dir='/ImagePTE1/ajoshi/data/thickness_data/thickness_fs_th_smooth';

d = dir(inp_dir);

left_surf = '/ImagePTE1/ajoshi/code_farm/bfp/supp_data/bci32kleft_smooth.dfs';
lsurf = readdfs(left_surf);
right_surf = '/ImagePTE1/ajoshi/code_farm/bfp/supp_data/bci32kright_smooth.dfs';
rsurf = readdfs(right_surf);
NV=length(lsurf.vertices);
parpool(20);
parfor i=3:length(d)

    fname = fullfile(inp_dir,d(i).name);
    outfname = fullfile(out_dir,[d(i).name(1:end-3),'smooth.mat']);
    
    if ~exist(outfname,'file')
        process_data(fname,outfname,NV,lsurf,rsurf)
    end
end


function process_data(fname,outfname,NV,lsurf,rsurf)
    load(fname);

    left_data = data(1:NV);
    right_data = data(NV+1:2*NV);

    data(1:NV)=smooth_surf_function(lsurf,left_data);
    data(NV+1:2*NV)=smooth_surf_function(rsurf,right_data);

    save(outfname,'data');
end