# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from astropy.io import fits
from astropy.io import ascii
#from astropy.stats import sigma_clipped_stats
from photutils.segmentation import detect_sources 
from photutils import source_properties

#nombre del directorio
namedir = './'

namedir = raw_input('Ruta del directorio de archivos ['+namedir+']: ') or namedir
files = [f for f in os.listdir(namedir) if f.endswith('.FIT')]

dispersion = 3.898 # Angstrom/pixel
h_alpha = [6562.851, 'H$_\\alpha$', 'red']
h_beta = [4861.2786, 'H$_\\beta$', 'aqua']
h_gamma = [4340.462, 'H$_\\gamma$', 'blue']
h_delta = [4101.74, 'H$_\\delta$', 'violet']
h_epsilon = [3970.072, 'H$_\\epsilon$', 'purple']

lines = [h_alpha, h_beta, h_gamma, h_delta, h_epsilon]

def extract_spectra(fitsfile, npix=5, saveplot=True):
    hdulist = fits.open(namedir+'/'+fitsfile)
    image = hdulist[0].data
    image = image-np.mean(image) # casi una resta del cielo
    
    #mean, median, std = sigma_clipped_stats(image, sigma=3, iters=5)
    threshold = np.max(image)
    segm = detect_sources(image, threshold = .8*threshold, npixels = 5)
    sources = source_properties(image, segm)
    
    # Definir centroide por rutina o de manera manual.
    # Los ejes estan al reves (y,x)
    star_centroid = (int(sources[0].centroid[0].value), int(sources[0].centroid[1].value))
    #star_centroid = (CENTROIDE Y, CENTROIDE X)
    
    cutimage = image[star_centroid[0]-npix:star_centroid[0]+npix,:star_centroid[1]]
    counts = np.sum(cutimage,axis = 0)/(2*npix+1)
    counts = counts[::-1] # el eje y
    pixel = range(len(counts)) # el eje x
    wavelenght = np.multiply(pixel, dispersion)
    
    minima = argrelextrema(counts, np.less, order=38)
    
    fig, ax = plt.subplots(figsize=(10,5))
    fig2, ax2 = plt.subplots(figsize=(10,5))
    
    ax.set_title('Proposed wavelenght calibration')
    ax.set_xlabel('Wavelenght ($\\AA$)')
    ax.set_ylabel('ADUs')
    ax.set_xlim(800*dispersion, 1800*dispersion)
    ax.set_ylim(0, max(counts[800:1800]))
    ax.plot(wavelenght, counts, c='k')
    for line in lines:
        ax.axvline(line[0], label=line[1], color=line[2])
    ax.legend()
    
    j = 0
    color = ['r','g','b','c','m','y']
    
    ax2.set_title('Uncalibrated')
    ax2.set_xlabel('Pixel')
    ax2.set_ylabel('ADUs')
    ax2.set_xlim(800, 1800)
    ax2.set_ylim(0, max(counts[800:1800]))
    ax2.plot(pixel, counts, c='k')
    for value in minima[0]:
        if 800<value<1800:
            ax2.axvline(pixel[value], label=str(pixel[value])+'px', c=color[(j+1)%len(color)-1])
            j += 1
    ax2.legend()

    plt.show()
    plt.close(fig)
    plt.close(fig2)
    
    if saveplot:
        fig.savefig(namedir+'/images/'+fitsfile.split('.')[0]+'_image.pdf', format = 'pdf')
        fig2.savefig(namedir+'/images/'+fitsfile.split('.')[0]+'_spec.pdf', format = 'pdf')

    ascii.write([pixel, counts], names=['pixel','counts'], output=namedir+'/spec/'+fitsfile.split('.')[0]+'.dat', overwrite=True)
    ascii.write([pixel, counts], names=['wavelenght','counts'], output=namedir+'/spec/'+fitsfile.split('.')[0]+'_calibrated.dat', overwrite=True)
    return 0


for fitsfile in files:
    extract_spectra(fitsfile)
