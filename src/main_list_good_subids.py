import glob, os

flist = glob.glob('/ImagePTE1/ajoshi/data/thickness_data/oasis_surf_screenshots/good_inner/*.png')
#print(flist)

textfile = open("good_subids.txt", "w")
for element in flist:
    sub = os.path.basename(element)
    textfile.write(sub[4:-31])
    textfile.write('\n')
textfile.close()

#with os.open('good_subids.txt','w'):