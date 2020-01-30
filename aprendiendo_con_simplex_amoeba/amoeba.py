from funcion_borovicka import construct_altura_deg, construct_azimuth_deg
from scipy import optimize, stats
import pandas as pd
import numpy as np
from tqdm import tqdm

"""
En funcion_borovicka.py estan definidos
X0, Y0, a0 = float(724), float(472), float(-3*np.pi/4)
"""
C, A, F = 0.07, 0.01, 1
V, S, D, P, Q = 0.03, 0.007, 0.09, 2.2*10**-6, 0.006
E, ep = 0, 0

def construct_alt_xi(x, y, z):
    def xi(C, A, F, V, S, D, P, Q, E, ep):
        alt_teorico = construct_altura_deg(C, A, F, V, S, D, P, Q, E, ep)
        return (z - alt_teorico(x, y))**2
    return xi

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

def construct_az_xi(x, y, z):
    def xi(C, A, F, V, S, D, P, Q, E, ep):
        az_teorico = construct_azimuth_deg(C, A, F, V, S, D, P, Q, E, ep)
        return (z - az_teorico(x, y))**2
    return xi

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

def drop_outlayers_by_center(pixtab_df, x0, y0):
    X_MIN = 250
    X_MAX = 1250
    Y_MIN = 0
    Y_MAX = 950
    MAX_RADIO = 500
    RADIO_STEPS = 2000
    query_str = "{}<=x<={} and {}<=y<={}".format(X_MIN, X_MAX,
                                                            Y_MIN, Y_MAX)
    data = pixtab_df.dropna(thresh = 7).query(query_str)

    r_list = []
    for indx in data.index:
        x = data.at[indx,"x"]
        y = data.at[indx,"y"]
        r = np.sqrt((x - x0)**2 + (y - y0)**2)
        r_list.append(r)
    data["radio"] = r_list

    rstep = MAX_RADIO/(RADIO_STEPS-1)
    r_range = np.linspace(0, MAX_RADIO, RADIO_STEPS)
    pbar = tqdm(total=RADIO_STEPS, desc="Droping Outlayers")
    new_df = []
    for r in r_range:
        query = "radio > {} and radio <= {}".format(r, r+rstep)
        df_circle = data.query(query).dropna()
        if len(df_circle)==1:
            new_df.append(df_circle)
        elif len(df_circle)>1:
            z = stats.zscore(df_circle.alt.values)
            indx = np.where(np.abs(z) < 0.5)
            new_df.append(df_circle.loc[df_circle.index.values[indx]])
        pbar.update()
    pbar.close()
    new_df = pd.concat(new_df, ignore_index=True)
    return new_df

def amoeba(params, mega_alt_xi, mega_az_xi):
    new_alt_params = optimize.fmin(mega_alt_xi, params, maxfun=1100)
    new_az_params = optimize.fmin(mega_az_xi, params, maxfun=1100)
    return [new_alt_params, new_az_params]
