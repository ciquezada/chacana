import numpy as np
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from tools import PBarATP, ProgressBar
from borovicka import construct_altura_deg, construct_azimuth_deg
from amoeba_pipeline import paso1, paso2, paso3, paso4, paso5
from multiprocessing import Pool


class InterpolatorSimple:
    INTERP_THRESHOLD = 400
    X_MIN = 300
    X_MAX = 1200
    Y_MIN = 0
    Y_MAX = 900


    def __init__(self, *args, **kwargs):
        pass

    def interpolate_pixtab(self, pixtab_df, *args, **kwargs):
        print("Iniciando interpolacion de filas y columnas...")
        df_rows = self._interpolate_df(pixtab_df, by="y")
        df_cols = self._interpolate_df(pixtab_df, by="x")
        print("Interpolacion finalizada.")
        pixtab_df = pd.concat([df_rows, df_cols], ignore_index=True)
        pixtab_df = df.groupby(['xcentroid',"ycentroid"], as_index=False).mean()
        return pixtab_df


    def _interpolate_df(self, data, by):
        """
        data: dataframe del tipo .pixtab
        by: determina si se interpolan filas o columnas

        retorna un dataframe del tipo .dat
        """
        if by=="x":
            x = "y"
            var_cte_range = range(self.X_MIN, self.X_MAX)
            total = self.X_MAX
            ini = self.X_MIN
        elif by=="y":
            x = "x"
            var_cte_range = range(self.Y_MIN, self.Y_MAX)
            total = self.Y_MAX
            ini = self.Y_MIN
        var_cte = by
        query_str = "{}<=x<={} and {}<=y<={}".format(self.X_MIN, self.X_MAX,
                                                            self.Y_MIN, self.Y_MAX)
        data = data.dropna(thresh = 7).query(query_str)
        df_header = ["xcentroid", "ycentroid", "alt", "az"]
        df_data = []
        print("Interpolando datos en {} ...".format(var_cte))
        lib.printProgressBar(0, total)
        for var_cte_value in var_cte_range:
            data_row = data.query("{}=={}".format(var_cte, var_cte_value)).sort_values(by=x)
            data_row = data_row.reset_index(drop=True)
            for indx in data_row.index:
                if indx>2:
                    x_2 = data_row.at[indx-3, x]
                    x_1 = data_row.at[indx-2, x]
                    x_0 = data_row.at[indx-1, x]
                    x_val = data_row.at[indx, x]
                    if x_2>x_val-self.INTERP_THRESHOLD:
                        xx = np.arange(x_2,x_val+1)
                        spl_alt = interp_spline(np.array([x_2, x_1, x_0, x_val]),
                                            np.array([data_row.at[indx-3, "alt"],
                                                        data_row.at[indx-2, "alt"],
                                                        data_row.at[indx-1, "alt"],
                                                        data_row.at[indx, "alt"]]))
                        spl_az = interp_spline(np.array([x_2, x_1, x_0, x_val]),
                                            np.array([data_row.at[indx-3, "az"],
                                                        data_row.at[indx-2, "az"],
                                                        data_row.at[indx-1, "az"],
                                                        data_row.at[indx, "az"]]))
                        new_data_alt = spl_alt(xx)
                        new_data_az = spl_az(xx)
                        for xnew, altnew, aznew in zip(xx, new_data_alt, new_data_az):
                            if x=="x":
                                df_data.append([xnew, var_cte_value, altnew, aznew])
                            else:
                                df_data.append([var_cte_value, xnew, altnew, aznew])
            lib.printProgressBar(var_cte_value, total)
        print("Done!\n")
        df = pd.DataFrame(df_data, columns= df_header)
        df = df.groupby(['xcentroid',"ycentroid"],as_index=False).mean()
        return df

class InterpolatorBycenter:
    """
    Primero calcula el posible cenith según lo que entregue el módulo
    circles_detector (carpeta)
    Luego hace el merge con una tabla vacía
    """
    INTERP_THRESHOLD = 400
    X_MIN = 300
    X_MAX = 1200
    Y_MIN = 0
    Y_MAX = 900

    def __init__(self, *args, **kwargs):
        pass

    def interpolate_pixtab(self, pixtab_df, *args, **kwargs):
        print("Calculando cenith...")
        self._get_cenith()
        print("Iniciando interpolación con cenith x: {}, y: {}...".format(
                                                self.x_center, self.y_center))
        pixtab_df = self._interpolate_df(pixtab_df)
        print("Interpolacion finalizada.")
        return pixtab_df

    def _interpolate_df(self, data):
        """
        data: dataframe del tipo .pixtab
        by: determina si se interpolan filas o columnas

        retorna un dataframe del tipo .dat
        """
        query_str = "{}<=x<={} and {}<=y<={}".format(self.X_MIN, self.X_MAX,
                                                            self.Y_MIN, self.Y_MAX)
        data = data.dropna(thresh = 7).query(query_str)
        df_header = ["xcentroid", "ycentroid", "alt", "az"]
        df_data = []
        r_range = np.linspace(0, self.MAX_RADIO, self.RADIO_STEPS)
        lib.printProgressBar(0, self.MAX_RADIO)
        for r in r_range:
            query = "{}//0.1 == ((x-{})**2 + (y-{})**2)**(1/2)//0.1"
            df_circle = data.query(query.format(r, self.x_center,
                                                        self.y_center)).dropna()
            if len(df_circle)>0:
                z = stats.zscore(df_circle.alt.values)
                indx = np.where(np.abs(z) < 1)
                alt = np.mean(df_circle.alt.values[indx])
                theta_range = np.linspace(0, 2*np.pi, 2*np.pi * r)
                for theta in theta_range:
                    df_data.append([self.x_center + r*np.cos(theta),
                                        self.y_center + r*np.sin(theta),
                                                                alt, theta])
            lib.printProgressBar(r, self.MAX_RADIO)
        print("Done!\n")
        df = pd.DataFrame(df_data, columns= df_header)
        return df.dropna(thresh = 4)

    def _get_cenith(self):
        circle = circle_detector()
        self.x_center = int(circle.detections_mean[1])
        self.y_center = int(circle.detections_mean[0])

class InterpolatorBorovicka:
    TIME_FORMAT = "%d-%m-%Y_%Hh%Mm%Ss"
    """
    parametros del pipeline (hacer a0 para la imagen de 7/09)
    """
    C, A, F =   1.12716604e+00, 2.47858246e-03, 7.04388456e-01
    V, S, D, P, Q = (2.99517405e-03, 1.41721867e-04, 1.56466343e-05,
                                        -3.94352535e-03, -3.82198376e-03)
    E, ep = -6.06531026e-03, -6.84149304e-03
    X0, Y0, a0 = 7.26230277e+02, 4.79906209e+02, 7.73715459e-01

    PARAMS = np.array([C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0])

    X_MIN = 300
    X_MAX = 1201
    Y_MIN = 0
    Y_MAX = 901

    def __init__(self, params = None, *args, **kwargs):
        if params:
            self.PARAMS = params
        self.altura = construct_altura_deg(*self.PARAMS)
        self.azimut = construct_azimuth_deg(*self.PARAMS)

    def interpolate_pixtab(self, pixtab_df, update_params=False, *args, **kwargs):
        print("Iniciando interpolador Amoeba-Borovicka...")
        if update_params:
            self.PARAMS = self.update_params(self.PARAMS, pixtab_df, *args, **kwargs)
            self.altura = construct_altura_deg(*self.PARAMS)
            self.azimut = construct_azimuth_deg(*self.PARAMS)
        X0, Y0 = self.PARAMS[10:12]
        print("Interpolando con cenith x: {}, y: {}...".format(X0, Y0))
        df = self._interpolate_df()
        print("Interpolacion finalizada.")
        return df

    def _interpolate_df(self):
        df_header = ["xcentroid", "ycentroid", "alt", "az"]
        df_data = self._interpolate_df_data()
        df = pd.DataFrame(df_data, columns= df_header)
        df = self._azimut_corrector(df)
        return df

    def _interpolate_df_data(self):
        Y_MIN = InterpolatorBorovicka.Y_MIN
        Y_MAX = InterpolatorBorovicka.Y_MAX
        X_MIN = InterpolatorBorovicka.X_MIN
        X_MAX = InterpolatorBorovicka.X_MAX
        x = np.arange(X_MIN, X_MAX)
        y = np.arange(Y_MIN, Y_MAX)
        X, Y = np.meshgrid(x, y)
        ALT = self.altura(X, Y)
        AZ = self.azimut(X, Y)
        for row_x, row_y, row_alt, row_az in PBarATP(zip(X,Y,ALT,AZ),
                                                    total=len(X),
                                                        name="Interpolation"):
            for x, y, alt, az in zip(row_x, row_y, row_alt, row_az):
                yield [int(x), int(y), alt, az]

    def _azimut_corrector(self, df):
        for x in PBarATP(range(self.X_MIN, self.X_MAX+1),
                                                    name="Correcting Azimut"):

            if x in range(self.X_MIN, int(self.X0)):
                col_data = df.query("xcentroid=={}".format(x))
                if len(col_data):
                    y_min = col_data.at[col_data.idxmin().az, "ycentroid"]
                    for indx in col_data.query("ycentroid<{}".format(y_min)).index:
                        df.at[indx, "az"] = 360 - col_data.at[indx, "az"]
                # pbar.update()
            elif x in range(int(self.X0), self.X_MAX+1):
                col_data = df.query("xcentroid=={}".format(x))
                if len(col_data):
                    y_min = col_data.at[np.abs(col_data.az - 180).idxmin(), "ycentroid"]
                    for indx in col_data.query("ycentroid<{}".format(y_min)).index:
                        df.at[indx, "az"] = 360 - col_data.at[indx, "az"]
        return df

    def update_params(self, init_params, pixtab_df, save=True):
        print("Actualizando parametros iniciales (AMOEBA)...")
        result_0 = init_params
        result_1 = paso1(result_0, pixtab_df, drop_outlayers=False)
        result_2 = paso2(result_1, pixtab_df, drop_outlayers=False)
        result_3 = paso3(result_2, pixtab_df, drop_outlayers=False)
        result_4 = paso4(result_3, pixtab_df, drop_outlayers=False)
        result_5 = paso5(result_4, pixtab_df, drop_outlayers=False)

        if save:
            time = datetime.now().strftime(self.TIME_FORMAT)
            file_name = "{}_updated_params.csv".format(time)
            df_header = ["C", "A", "F", "V", "S", "D", "P",
                                        "Q", "E", "ep", "X0", "Y0", "a0"]
            df_data = [result_0, result_1, result_2,
                                            result_3, result_4, result_5]
            df = pd.DataFrame(df_data, columns= df_header)
            df.to_csv(file_name, sep=',', index=False)
        return result_5
