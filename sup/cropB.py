from scipy.misc import imread, imsave
import matplotlib.pylab as plt
from glob import glob

for f in glob('*b.png'):
    print(f)
    img = imread(f)
    if img[849,1836,0]==0:
        img=img[54:851,192:1838]
    else:
        img=img[54:562,192:1838]
    imsave(f,img)