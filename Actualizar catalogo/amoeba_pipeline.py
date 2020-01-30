from scipy import optimize
import numpy as np
from tqdm import tqdm
from tools import PBarATP


"""
Estos son constructores de una funcion de Xi**2
"""
def construct_alt_xi(x, y, z):
    def xi(C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0):
        alt_teorico = construct_altura_deg(C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0)
        return (z - alt_teorico(x, y))**2
    return xi

def construct_az_xi(x, y, z):
    def xi(C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0):
        az_teorico = construct_azimuth_deg(C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0)
        return (z - az_teorico(x, y))**2
    return xi

"""
Recibe un pixtab y reduce sus datos según los que difieran mucho
del plano entregado
"""
def drop_outlayers_by_borovicka(pixtab_df, plano, diff = 1):

    X_MIN = 250
    X_MAX = 1250
    Y_MIN = 0
    Y_MAX = 950
    MAX_RADIO = 500
    RADIO_STEPS = 2000
    query_str = "{}<=x<={} and {}<=y<={}".format(X_MIN, X_MAX,
                                                            Y_MIN, Y_MAX)
    data = pixtab_df.dropna(thresh = 7).query(query_str)

#     pbar = tqdm(total=len(data.x.values), desc="Droping Outlayers")
    new_df_indx = []
    for indx in PBarATP(data.index, name = "Droping Outlayers"):
#     for indx in data.index:
        x = data.at[indx,"x"]
        y = data.at[indx,"y"]
        alt = data.at[indx,"alt"]
        if np.abs(plano(x,y)-alt) < diff:
            new_df_indx.append(indx)
#         pbar.update()
#     pbar.close()
    return data.loc[new_df_indx]

"""
Esto lo definimos por cada paso segun los parametros que
queramos buscar
"""
def ejemplo_paso(params):

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, a0 = ctes
            C, A, F, E, ep, X0, Y0 = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, a0 = ctes
            C, A, F, E, ep, X0, Y0 = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xii
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
        new_alt_params = optimize.fmin(mega_alt_xi, params, maxfun=1100)
        new_az_params = optimize.fmin(mega_az_xi, params, maxfun=1100)
        return [new_alt_params, new_az_params]

    def amoeba2(params, mega_alt_xi, mega_az_xi):
        """ se pueden usar otro tipo de funcion para minimizar """
        new_alt_params = optimize.least_squares(mega_alt_xi, params)
        new_az_params = optimize.least_squares(mega_az_xi, params)
        return [new_alt_params, new_az_params]

"""
Aqui empiezan los pasos del pipeline
"""
def paso1(params, data, drop_outlayers=False):
    """
    314 - V, S, D, P, Q, X0, Y0, a0
    Primero haremos un acercamiento 314 para buscar
    parametros C,A,F,E,ep que nos ayuden a reducir mejor los datos outlayers
    """

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, X0, Y0, a0 = ctes
            C, A, F, E, ep, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, X0, Y0, a0 = ctes
            C, A, F, E, ep, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
        new_alt_params = optimize.fmin(mega_alt_xi, params)#, maxfun=100)
    #     new_az_params = optimize.fmin(mega_az_xi, params, maxfun=1100)
        return new_alt_params

    C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0 = params
    init_params = [C, A, F, E, ep]
    ctes = [V, S, D, P, Q, X0, Y0, a0]

    # data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    if drop_outlayers:
        data = drop_outlayers_by_borovicka(data,
                                construct_altura_deg(*init_params[:3],
                                 *ctes[:-3], *init_params[-2:], *ctes[-3:]), 5)
    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = np.rad2deg(np.arccos(np.cos(np.deg2rad(data.az.values))))
    mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo, ctes)
    mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo, ctes)

    pbar = tqdm(total=1000, desc="C, A, F, E, ep")
    result = amoeba(init_params, mega_alt_xi, mega_az_xi)
    pbar.close()

    result_1 =  np.array([*result[:3], *ctes[:-3], *result[-2:], *ctes[-3:]])
    print(result_1)
    return result_1

def paso2(params, data, drop_outlayers=False):
    """
    Ahora buscamos a0 quitando datos outlayers reduciendo azimut.
    Al ser solo a0 deberia ser mas fácil.
    """

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, V, S, D, P, Q, E, ep, X0, Y0 = ctes
            a0, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, V, S, D, P, Q, E, ep, X0, Y0 = ctes
            a0, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
    #     new_alt_params = optimize.fmin(mega_alt_xi, params, maxfun=1100)
        new_az_params = optimize.fmin(mega_az_xi, params)#, maxfun=10)
        return new_az_params

    C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0 = params
    init_params = [a0]
    ctes = [C, A, F, V, S, D, P, Q, E, ep, X0, Y0]

    # data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    if drop_outlayers:
        data = drop_outlayers_by_borovicka(data,
                                construct_altura_deg(*ctes, *init_params), 5)
    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = np.rad2deg(np.arccos(np.cos(np.deg2rad(data.az.values))))
    mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo, ctes)
    mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo, ctes)

    pbar = tqdm(total=1000, desc="a0")
    result = amoeba(init_params, mega_alt_xi, mega_az_xi)
    pbar.close()


    result_2 = np.array([*ctes, *result])
    print(result_2)
    return result_2

def paso3(params, data, drop_outlayers=False):
    """
    Ahora buscamos E,X0,Y0,a0 quitando datos outlayers reduciendo azimut.
    Como a0 esta más cerca del resultado pude que se demore menos.
    (19min menos y mejor resultado)
    """

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, V, S, D, P, Q, ep = ctes
            E, X0, Y0, a0, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, V, S, D, P, Q, ep = ctes
            E, X0, Y0, a0, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
    #     new_alt_params = optimize.fmin(mega_alt_xi, params, maxfun=1100)
        new_az_params = optimize.fmin(mega_az_xi, params)#, maxfun=100)
        return new_az_params

    C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0 = params
    init_params = [E, X0, Y0, a0]
    ctes = [C, A, F, V, S, D, P, Q, ep]

    # data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    if drop_outlayers:
        data = drop_outlayers_by_borovicka(data,
         construct_altura_deg(*ctes[:-1], init_params[0], ctes[-1],
                                                        *init_params[-3:]), 5)
    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = np.rad2deg(np.arccos(np.cos(np.deg2rad(data.az.values))))
    mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo, ctes)
    mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo, ctes)

    pbar = tqdm(total=100, desc="E, X0, Y0, a0")
    result = amoeba(init_params, mega_alt_xi, mega_az_xi)
    pbar.close()


    result_3 = np.array([*ctes[:-1], result[0], ctes[-1], *result[-3:]])
    print(result_3)
    return result_3

def paso4(params, data, drop_outlayers=False):
    """
    314 - V, S, D, P, Q
    Ahora buscamos V,S,D,P,Q reduciendo la altura. Según lo que experimentamos
    no deberia afectar al azimut.
    Algo particular es que si reducimos discriminando datos apunta mal,
    debe ser que necesita mas datos en el horizonte.
    """

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, E, ep, X0, Y0, a0 = ctes
            V, S, D, P, Q, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            C, A, F, E, ep, X0, Y0, a0 = ctes
            V, S, D, P, Q, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
        new_alt_params = optimize.fmin(mega_alt_xi, params)#, maxfun=100)
    #     new_az_params = optimize.fmin(mega_az_xi, params, maxfun=1100)
        return new_alt_params


    C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0 = params
    init_params = [V, S, D, P, Q]
    ctes = [C, A, F, E, ep, X0, Y0, a0]

    # data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    if drop_outlayers:
        data = drop_outlayers_by_borovicka(data,
                    construct_altura_deg(*ctes[:3],*init_params, *ctes[3:]), 5)
    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = np.rad2deg(np.arccos(np.cos(np.deg2rad(data.az.values))))
    mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo, ctes)
    mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo, ctes)

    pbar = tqdm(total=100, desc="V, S, D, P, Q")
    result = amoeba(init_params, mega_alt_xi, mega_az_xi)
    pbar.close()


    result_4 = np.array([*ctes[:3],*result, *ctes[3:]])
    print(result_4)
    return result_4

def paso5(params, data, drop_outlayers=False):
    """
    Ahora buscamos C,A,F reduciendo la altura.
    Según lo que experimentamos no deberia afectar al azimut
    """

    def construct_acumulate_alt_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, E, ep, X0, Y0, a0 = ctes
            C, A, F, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_alt_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    def construct_acumulate_az_xi(x_list, y_list, z_list, ctes = None):
        def acumulate_xi(params):
            V, S, D, P, Q, E, ep, X0, Y0, a0 = ctes
            C, A, F, = params
            suma_xi = 0
            for x, y, z in zip(x_list, y_list, z_list):
                xi = construct_az_xi(int(x), int(y), int(z))
                suma_xi += xi(C, A, F, V, S, D, P, Q, E, ep, float(X0), float(Y0), a0)
            pbar.update()
            return suma_xi
        return acumulate_xi

    ######################################################################################################

    def amoeba(params, mega_alt_xi, mega_az_xi):
        new_alt_params = optimize.fmin(mega_alt_xi, params)#, maxfun=100)
    #     new_az_params = optimize.fmin(mega_az_xi, params, maxfun=1100)
        return new_alt_params

    C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0 = params
    init_params = [C, A, F]
    ctes = [V, S, D, P, Q, E, ep, X0, Y0, a0]

    # data = pd.read_csv("Data.pixtab", sep=" ")
    data = data.dropna()
    if drop_outlayers:
        data = drop_outlayers_by_borovicka(data,
                                construct_altura_deg(*init_params, *ctes), 5)
    x_exp = data.x.values
    y_exp = data.y.values
    alt_catalogo = data.alt.values
    az_catalogo = np.rad2deg(np.arccos(np.cos(np.deg2rad(data.az.values))))
    mega_alt_xi = construct_acumulate_alt_xi(x_exp, y_exp, alt_catalogo, ctes)
    mega_az_xi = construct_acumulate_az_xi(x_exp, y_exp, az_catalogo, ctes)

    pbar = tqdm(total=100, desc="C, A, F")
    result = amoeba(init_params, mega_alt_xi, mega_az_xi)
    pbar.close()


    result_5 = np.array([*result, *ctes])
    print(result_5)
    return result_5
