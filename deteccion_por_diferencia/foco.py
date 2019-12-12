# -*- coding: utf-8 -*-
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from astropy.io import fits
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils.segmentation import detect_sources
from photutils import source_properties

# Valores por defecto
npix        = [3352,2532]   # npix_x npix_y de la cámara
namedir     = './'          # Nombre del directorio de las imágenes
show_cut    = False         # Muestra la posición del corte para cada imagen
show_adjust = False         # Para visualizar ajustes gaussianos a cada imagen
times       = 1             # Número de veces que se calcula un mínimo
sig_clip    = 0             # Sigma clip. 0 omite el paso

# El usuario puede sobreescribir los valores por defecto
namedir = raw_input('Ruta del directorio de archivos ['+namedir+']: ') or namedir
show_cut = raw_input('Mostrar posicion del corte? (Yes/[No]): ').lower() or show_cut
show_adjust = raw_input('Mostrar ajuste para cada imagen? (Yes/[No]): ').lower() or show_adjust
times = raw_input('Numero de iteraciones (valor/[1]): ') or times
sig_clip = raw_input('Sigma clip? (valor/[No]): ') or sig_clip

times = int(times)
sig_clip = float(sig_clip)

files = [f for f in os.listdir(namedir) if f.endswith('.FIT')]
optimum, optimum_fit = [], []

# (Re)inicializa variables
def reset():
    global FLEN # Foco
    global FWHM # FWHM
    global vcut_x # posición del corte
    global centroid_x_ref # posición de la estrella
    FLEN, FWHM = [], []
    vcut_x = random.randrange(1700,1900)
    #vcut_x = input('Vertical cut position: ')
    
def Gauss(x, a, x0, sigma):
    return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def get_fwhm(fitsfile):
    #print fitsfile
    hdulist = fits.open(fitsfile)
    image = hdulist[0].data
    image = image-np.mean(image) # casi una resta del cielo
    
    threshold = np.max(image)
    segm = detect_sources(image, threshold = 0.5*threshold, npixels = 6)
    sources = source_properties(image, segm)
    centroid_x = int(sources[0].centroid[1].value)
    centroid_y = int(sources[0].centroid[0].value)
    
    # La posición del corte es relativa a la posición de la estrella
    # Si es la primera imagen de la lista toma sus valores como referencia
    if (fitsfile == namedir+'/'+files[0]):
        globals().update(centroid_x_ref = centroid_x)
        vcut_x_aux = vcut_x
    else:
        diff_x = centroid_x_ref - centroid_x
        vcut_x_aux = vcut_x - diff_x
    
    y = image[:,vcut_x_aux]
    x = range(len(y))

    # correction for weighted arithmetic mean
    mean = sum(x*y)/sum(y)
    sigma = np.sqrt(abs(sum(y*(x-mean)**2)/sum(y)))
    popt, pcov = curve_fit(Gauss, x, y, p0=[max(y), mean, sigma])

    fwhm = 2.355*np.abs(popt[2]) # approx 2.355*sigma
        
    # obtiene el foco del nombre de la imagen
    # debe estar precedido por '_' y sucedido por la extensión del archivo
    focus = fitsfile.split('.')[0].split('_')[-1]
    #focus = raw_input('Enter focus for '+fitsfile+': ') or focus
    #focus = int(focus)
    
    FLEN.append(focus)
    FWHM.append(fwhm)
        
    if show_cut=='y' or show_cut=='yes':
        norm = ImageNormalize(stretch=SqrtStretch())
        fig, ax = plt.subplots(figsize=(15,10))
        ax.set_title(focus)
        ax.set_ylim(centroid_y-200,centroid_y+200)
        ax.imshow(image, cmap='Greys', origin='lower', norm=norm)
        ax.axvline(x=vcut_x_aux, label='Cut', c='g')
        ax.axvline(centroid_x, label='Star', c='r')
        ax.set_xticks([vcut_x_aux, centroid_x])
        plt.legend()
        plt.show()
        plt.close()
        
    if show_adjust=='y' or show_adjust=='yes':
        fig, ax = plt.subplots(figsize=(10,5))
        ax.set_xlim(centroid_y-50, centroid_y+50)
        ax.set_title(focus)
        ax.set_xlabel('Pixel')
        ax.set_ylabel('Counts')
        ax.plot(x,y,label='Profile')
        ax.plot(x, Gauss(x, *popt), 'r-', label='Fit')
        fwhm_label = 'FWHM ('+str(round(fwhm,2))+')'
        plt.hlines(y=popt[0]/2, xmin=popt[1]-fwhm/2, xmax=popt[1]+fwhm/2,linestyles='dashed',label=fwhm_label)
        plt.legend()
        plt.show()
        plt.close()

for i in range(times):
    reset()
    for fitsfile in files:
        get_fwhm(namedir+'/'+fitsfile)

    container = np.array(zip(FLEN,FWHM),dtype=[('focus',int),('fwhm',float)]).reshape(-1,1)
    if sig_clip > 0:
        idx = np.where(
                (container['fwhm'] < np.mean(container['fwhm']) - sig_clip*np.std(container['fwhm'])) |
                (container['fwhm'] > np.mean(container['fwhm']) + sig_clip*np.std(container['fwhm']))
                )[0]
        container = np.delete(container,idx,axis=0)

    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_xlim(min(container['focus'])-100, max(container['focus'])+100)
    ax.set_title('Cut at x = '+str(vcut_x))
    ax.set_xlabel('Focus')
    ax.set_ylabel('FWHM (pix)')
    ax.plot(container['focus'], container['fwhm'], 'b.--', label='FWHM')
    
    fit = np.poly1d(np.polyfit(container['focus'].reshape(1,-1)[0], container['fwhm'].reshape(1,-1)[0], 2))
    fit_x = np.linspace(min(container['focus']), max(container['focus']), 100)
    fit_y = fit(fit_x)
    ax.plot(fit_x, fit_y, 'r-', label='Fit')
    
    plt.legend()
    plt.show()
    plt.close()
    
    idx = np.where(container['fwhm'] == container['fwhm'].min())
    opt_focus = container['focus'][idx]
    optimum.append(opt_focus)
    
    idx = np.where(fit_y == fit_y.min())
    opt_focus_fit = fit_x[idx]
    optimum_fit.append(opt_focus_fit)
    
    print '[%d/%d] Minimum FWHM at focus %d (obs), %.2f (fit)' % (i+1, times, opt_focus, opt_focus_fit)

# Calcula y muestra algunas estadísticas
print 40*'-', '\nOptimal focus statistics\n', 40*'-'
if (sig_clip>0): print 'Optimal FWHM values sigma-clipped at %.2f sigma!' % (sig_clip)
print '\nFrom observed:'
print 'Min: %d' % (min(optimum))
print 'Max: %d' % (max(optimum))
print 'Mean: %.2f' % (np.mean(optimum))
print '\nFrom fit:'
print 'Min: %.2f' % (min(optimum_fit))
print 'Max: %.2f' % (max(optimum_fit))
print 'Mean: %.2f' % (np.mean(optimum_fit))
