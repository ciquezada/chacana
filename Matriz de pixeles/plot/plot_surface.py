import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d, Axes3D
import lib as lib
from class_pixeltable import PixelTable


PATH = ".." + os.sep + "Interpolated_Data.pixtab"

def show_surface(X, Y, Z):
    """
    Z: numpy array
    X,Y: meshgrid
    """
    fig = plt.figure(figsize=(12,12))
    ax = fig.gca(projection='3d')
    ax.plot_surface(X, Y, Z, cmap='summer', rstride=1, cstride=1, alpha=None, antialiased=True)

    plt.show()

def plot_surface(table, skip_data = 10, col = "alt"):
    print("\nCreando vista previa de superficie de pixeles")
    total = table.df.shape[0]
    X = np.arange(300, 1200)
    Y = np.arange(0, 900)
    XX, YY = np.meshgrid(X,Y)
    ZZ = np.zeros([900,900])
    lib.printProgressBar(0, 810000)
    for i, indx in enumerate(table.df.query("300<=x<1200 and 0<=y<900").index):
        x = table[indx,'x']
        y = table[indx,'y']
        val = table[indx, col]
        ZZ[y-0,x-300] = val
        lib.printProgressBar(i, 810000)
    show_surface(XX[::10,::10],YY[::10,::10],ZZ[::10,::10])

def plot_surface2(table, skip_data = 10, col = "alt"):
    print("\nCreando vista previa de superficie de pixeles")
    total = table.df.shape[0]
    X = np.arange(300, 1200)
    Y = np.arange(0, 900)
    ZZ = np.zeros([900,900])
    lib.printProgressBar(0, 810000)
    for i, indx in enumerate(table.df.query("300<=x<1200 and 0<=y<900").index):
        x = table[indx,'x']
        y = table[indx,'y']
        val = table[indx, col]
        ZZ[y-0,x-300] = val
        lib.printProgressBar(i, 810000)
    show_surface(XX[::10,::10],YY[::10,::10],ZZ[::10,::10])

if __name__=="__main__":
    table = PixelTable(data_path = PATH)
    plot_surface(table)
