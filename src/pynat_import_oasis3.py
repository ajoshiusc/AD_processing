import sys, os
from subprocess import Popen
import multiprocessing as mp

import pyxnat

URL = 'https://central.xnat.org' # central URL
BET = '/usr/share/fsl/5.0/bin/bet'              # BET executable path

central = pyxnat.Interface(server=URL,user='aajoshi',password='Opensimsim') # connection object

def bet(in_img, in_hdr): # Python wrapper on FSL BET, essentially a system call
    in_image = in_img.get()     # download .img
    in_hdr.get()                # download .hdr
    path, name = os.path.split(in_image)
    in_image = os.path.join(path, name.rsplit('.')[0])
    out_image = os.path.join(path, name.rsplit('.')[0] + '_brain')
    print('==> %s' % in_image[-120:])
    Popen('%s %s %s' % (BET, in_image, out_image), 
          shell=True).communicate()
    return out_image

notify = lambda m: sys.stdout.write('<== %s\n' % m[-120:]) # print finish message
pool = mp.Pool(processes=mp.cpu_count() * 2) # pool of concurrent workers
images = {}
print('pool opened with %d workers'%mp.cpu_count())
query = ('/projects/CENTRAL_OASIS_CS/subjects/*'
          '/archive/experiments/*_MR1/scans/mpr-1*/resources/*/files/*')
filter_ = [('xnat:mrSessionData/AGE', '>', '80'), 'AND']

#print('checking query')
query_out=central.select(query).where(filter_)
print('entering loop')

for f in query_out:
    label = f.label()
    print(label)
    # images are stored in pairs of files (.img, .hdr) in this project
    if label.endswith('.img'):
        images.setdefault(label.split('.')[0], []).append(f)
    if f.label().endswith('.hdr'):
        images.setdefault(label.split('.')[0], []).append(f)
    # download and process both occur in parallel within the workers
    for name in images.keys():  
        if len(images[name]) == 2: # if .img and .hdr XNAT references are ready
            img, hdr = images.pop(name)                        # get references
            pool.apply_async(bet, (img, hdr), callback=notify) # start worker
pool.close()
pool.join()