
function linked_dist_gord(subbasename,GOrdSurfIndFile)

left_inner = readdfs([subbasename,'.left.inner.cortex.svreg.dfs']);
left_pial = readdfs([subbasename,'.left.pial.cortex.svreg.dfs']);
right_inner = readdfs([subbasename,'.right.inner.cortex.svreg.dfs']);
right_pial = readdfs([subbasename,'.right.pial.cortex.svreg.dfs']);

[pth, sub] = fileparts(subbasename);
atlas_left = readdfs(fullfile(pth,'atlas.left.mid.cortex.svreg.dfs'))
atlas_right = readdfs(fullfile(pth,'atlas.right.mid.cortex.svreg.dfs'))

left_ld.attributes = sqrt(sum((left_inner.vertices - left_pial.vertices).^2,2));
right_ld.attributes = sqrt(sum((right_inner.vertices - right_pial.vertices).^2,2));

writedfs([subbasename,'.left.mid.cortex.ld.dfs'],left_ld);
writedfs([subbasename,'.right.mid.cortex.ld.dfs'],right_ld);

atlas_left = map_data_flatmap(left_ld,left_ld,atlas_left);
atlas_right = map_data_flatmap(right_ld,right_ld,atlas_right);


writedfs(fullfile(pth,'atlas.left.mid.cortex.ld.dfs'),atlas_left);
writedfs(fullfile(pth,'atlas.right.mid.cortex.ld.dfs'),atlas_right);


generateGOrdSCT(subbasename, GOrdSurfIndFile);
