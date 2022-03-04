
function surf_screenshots(subbasename,out_dir)

[d,subid]=fileparts(subbasename);

left_inner = readdfs([subbasename,'.left.inner.cortex.svreg.dfs']);
left_pial = readdfs([subbasename,'.left.pial.cortex.svreg.dfs']);
right_inner = readdfs([subbasename,'.right.inner.cortex.svreg.dfs']);
right_pial = readdfs([subbasename,'.right.pial.cortex.svreg.dfs']);

h=figure;hold on;
patch('faces',left_inner.faces,'vertices',left_inner.vertices,'facevertexcdata',left_inner.vcolor,'edgecolor','none','facecolor','interp');
axis equal;
patch('faces',right_inner.faces,'vertices',right_inner.vertices,'facevertexcdata',right_inner.vcolor,'edgecolor','none','facecolor','interp');
axis off;axis tight;camlight;material dull;

saveas(h,fullfile(out_dir,[subid,'_inner.png']));


h=figure;hold on;
patch('faces',left_pial.faces,'vertices',left_pial.vertices,'facevertexcdata',left_pial.vcolor,'edgecolor','none','facecolor','interp');
axis equal;
patch('faces',right_pial.faces,'vertices',right_pial.vertices,'facevertexcdata',right_pial.vcolor,'edgecolor','none','facecolor','interp');
axis off;axis tight;camlight;material dull;

saveas(h,fullfile(out_dir,[subid,'_pial.png']));



