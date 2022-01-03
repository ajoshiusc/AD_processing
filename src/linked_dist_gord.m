
function linked_dist_gord(subbasename,GOrdSurfIndFile,GOrdFile)

left_inner = readdfs([subbasename,'.left.inner.cortex.svreg.dfs']);
left_pial = readdfs([subbasename,'.left.pial.cortex.svreg.dfs']);
right_inner = readdfs([subbasename,'.right.inner.cortex.svreg.dfs']);
right_pial = readdfs([subbasename,'.right.pial.cortex.svreg.dfs']);

left_data = sqrt(sum((left_inner.vertices - left_pial.vertices).^2,2));
right_data = sqrt(sum((right_inner.vertices - right_pial.vertices).^2,2));

surfdata2gord(subbasename, left_data, right_data, GOrdSurfIndFile, GOrdFile)
