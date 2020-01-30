from funcion_borovicka import construct_altura_deg, construct_azimuth_deg
from amoeba import construct_alt_xi, construct_az_xi, drop_outlayers_by_center, amoeba
from scipy import optimize, stats
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from tqdm import tqdm

"""
En funcion_borovicka.py tambien estan definidos
X0, Y0, a0 = float(724), float(472), float(-3*np.pi/4)
"""
X0, Y0, a0 = float(724), float(472), float(-3*np.pi/4)
C, A, F = 0.07, 0.01, 1
V, S, D, P, Q = 0.03, 0.007, 0.09, 2.2*10**-6, 0.006
E, ep = 0, 0

def plot_plano(plano):
    x = np.linspace(0, 1200, 100)
    y = np.linspace(0, 900, 100)
    X, Y = np.meshgrid(x, y)
    Z = plano(X, Y)
    fig,ax=plt.subplots(1,1)
    cp = ax.contourf(X, Y, Z, 10)
    fig.colorbar(cp) # Add a colorbar to a plot
    ax.set_title('Toda una linea que minimiza y=mx+n')
    plt.gca().invert_yaxis()
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    plt.show()

def construct_acumulate_alt_xi(x_list, y_list, z_list):
    def acumulate_xi(params):
        C, A, F, V, S, D, P, Q, E, ep = params
        suma_xi = 0
        for x, y, z in zip(x_list, y_list, z_list):
            xi = construct_alt_xi(int(x), int(y), int(z))
            suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep)
        pbar.update()
        return suma_xi
    return acumulate_xi

def construct_acumulate_az_xi(x_list, y_list, z_list):
    def acumulate_xi(params):
        C, A, F, V, S, D, P, Q, E, ep = params
        suma_xi = 0
        for x, y, z in zip(x_list, y_list, z_list):
            xi = construct_az_xi(int(x), int(y), int(z))
            suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep)
        pbar.update()
        return suma_xi
    return acumulate_xi

if __name__=="__main__":
    data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    data = drop_outlayers_by_center(data, X0, Y0)

    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = data.az.values

    plt.gca().invert_yaxis()
    plt.scatter(x_exp, y_exp, c=az_catalogo, s=0.01)
    plt.show()

    # mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo)
    # mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo)
    # results_list = []
    #
    # pbar = tqdm(total=220, desc="Aproximando altura y azimuth")
    # results_list += amoeba([C,A,F,V,S,D,P,Q,E,ep], mega_alt_xi, mega_az_xi)
    # pbar.close()
    # print(results_list[-1])
