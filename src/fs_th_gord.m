
function fs_th_gord(subbasename,GOrdSurfIndFile,GOrdFile)

left_inner = readdfs([subbasename,'.left.inner.cortex.svreg.dfs']);
left_pial = readdfs([subbasename,'.left.pial.cortex.svreg.dfs']);
right_inner = readdfs([subbasename,'.right.inner.cortex.svreg.dfs']);
right_pial = readdfs([subbasename,'.right.pial.cortex.svreg.dfs']);

left_th=readdfs([subbasename,'.left.mid.cortex.fs.dfs']);
right_th=readdfs([subbasename,'.right.mid.cortex.fs.dfs']);
left_data = left_th.attributes;
right_data = right_th.attributes;

surfdata2gord(subbasename, left_data, right_data, GOrdSurfIndFile, GOrdFile)
