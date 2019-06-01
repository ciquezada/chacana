import numpy as np
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt

def interp_spline(x, y):
    """
    x,y: numpy arrays
    retorna una funcion que recibe numpy array y devuelve el equivalente
    interpolado
    """
    t, c, k = interpolate.splrep(x, y, s=0, k=1)
    # print('''\
    # t: {}
    # c: {}
    # k: {}
    # '''.format(t, c, k))
    # N = 100
    # xmin, xmax = x.min(), x.max()
    # xx = np.linspace(xmin, xmax, N)
    spline = interpolate.BSpline(t, c, k, extrapolate=False)

    # plt.plot(x, y, 'bo', label='Original points')
    # plt.plot(xx, spline(xx), 'r', label='BSpline')
    # plt.grid()
    # plt.legend(loc='best')
    # plt.show()
    return spline

def interp_cubicspline(x, y):
    return interpolate.CubicSpline(x, y)
