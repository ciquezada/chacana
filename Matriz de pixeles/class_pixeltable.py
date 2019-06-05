import imageio
import numpy as np
import pandas as pd
import parameters_pixeltable as P
import lib as lib
from interpolate_test import interp_spline, interp_cubicspline
from circles_detector.class_circle_detector import circle_detector
from scipy import stats
from datetime import datetime

import matplotlib.pyplot as plt


class ImageHandler:

    TIME_FORMAT = "%m-%d-%Y_%Hh%Mm%Ss"
    PATH_MASK = "mask.png"

    def __init__(self, pixels):
        self._pixels = pixels
        self._image_alt = None
        self._image_az = None

    @property
    def alt(self):
        if not isinstance(self._image_alt, type(np.array([]))):
            self.create()
        plt.imshow(self._image_alt)
        plt.axis("off")
        plt.show()

    @property
    def az(self):
        if not isinstance(self._image_az, type(np.array([]))):
            self.create()
        plt.imshow(self._image_az)
        plt.axis("off")
        plt.show()

    def save(self, dir_path = ""):
        if not isinstance(self._image_az, type(np.array([]))):
            self.create()
        time = datetime.now().strftime(self.TIME_FORMAT)
        imageio.imwrite(dir_path + "{}_altitude.png".format(time),
                                                                self._image_alt)
        imageio.imwrite(dir_path + "{}_azimuth.png".format(time),
                                                                self._image_az)

    def create(self):
        print("\nCreando vista previa de pixeles")
        total = self._pixels.shape[0]
        self._image_alt = imageio.imread(P.PATH_MASK)
        self._image_az = imageio.imread(P.PATH_MASK)
        lib.printProgressBar(0, total)
        for indx in self._pixels.index:
            x = self._pixels.at[indx,'x']
            y = self._pixels.at[indx,'y']
            alt = self._pixels.at[indx, "alt"]
            az = self._pixels.at[indx, "az"]
            self._coloring_pixels_alt(x, y, alt)
            self._coloring_pixels_az(x, y, az)
            lib.printProgressBar(indx, total)
        print("Exito!")

    def _coloring_pixels_alt(self, x, y, val):
        c = [*range(0,86,20)]
        if not np.isnan(val):
            # if 88 <= val < 90:
            #     new_im[y,x,0] = 250
            if any([*(c[i-1]<=val<c[i] for i in range(1, len(c), 3))]):
                self._image_alt[y,x,0] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(2, len(c), 3))]):
                self._image_alt[y,x,1] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(3, len(c), 3))]):
                self._image_alt[y,x,2] = 250
            elif 80 <= val < 85:
                self._image_alt[y,x,1] = 250
            elif 85 <= val:
                self._image_alt[y,x,0] = 140
                self._image_alt[y,x,1] = 140
                self._image_alt[y,x,2] = 250
            else:
                self._image_alt[y,x,0] = 250
                self._image_alt[y,x,1] = 250
                self._image_alt[y,x,2] = 250

    def _coloring_pixels_az(self, x, y, val):
        c = [*range(0,360,20)]
        if not np.isnan(val):
            # if 88 <= val < 90:
            #     new_im[y,x,0] = 250
            if any([*(c[i-1]<=val<c[i] for i in range(1, len(c), 3))]):
                self._image_az[y,x,0] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(2, len(c), 3))]):
                self._image_az[y,x,1] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(3, len(c), 3))]):
                self._image_az[y,x,2] = 250

class PixelTable:
    """
    Por ahora solo con alt y az
    contiene informacion de un lienzo de 1548x1040 pixeles
    """
    X_RESOLUTION = P.X_RESOLUTION
    Y_RESOLUTION = P.Y_RESOLUTION

    def __init__(self, new_matrix = False, data_path = False):
        if new_matrix:
            self.df = self.empty_pixtab()
        elif data_path:
            self.df = pd.read_csv(data_path, sep=" ")
        else:
            print("No se ingresaron parametros")
        self.preview = ImageHandler(self.df)

    @staticmethod
    def empty_pixtab():
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        for j in range(P.Y_RESOLUTION):
            for i in range(P.X_RESOLUTION):
                df_data.append([i, j, np.NaN, np.NaN, np.NaN, np.NaN, 0])
        return pd.DataFrame(df_data, columns= df_header)

    def export_to_file(self, path):
        """
        como es un dataframe con un formato especial
        usemos la extension ".pixtab"
        """
        self.df.to_csv(path, sep=' ', index=False)
        return 1

    def merge_dataframe(self, new_df):
        m_alt, m_az = self._merge_dataframe_extract_3dmatrix(new_df)
        total = self.df.shape[0]
        print("\nReduciendo y fusionando nuevos datos...")
        lib.printProgressBar(0, total)
        for indx in self.df.index:
            x = self[indx,'x']
            y = self[indx,'y']
            samsize = self.df.at[indx,"sample_size"]
            if len(m_alt[y][x]) and not samsize:
                prom_alt = np.mean(m_alt[y][x])
                prom_az = np.mean(m_az[y][x])
                new_samsize = len(m_alt[y][x])
                prom_alt_new = prom_alt
                prom_az_new = prom_az
                new_err_alt = np.sqrt(np.mean((np.array(m_alt[y][x])
                                            -prom_alt)**2))
                new_err_az = np.sqrt(np.mean((np.array(m_az[y][x])
                                            -prom_az)**2))
                #
                # new_err_alt = np.sqrt(np.mean((np.array(m_alt[y][x])
                #                             -prom_alt)**2))/np.sqrt(new_samsize)
                # new_err_az = np.sqrt(np.mean((np.array(m_az[y][x])
                #                             -prom_az)**2))/np.sqrt(new_samsize)
                self._merge_dataframe_save_row(indx, new_samsize,
                    prom_alt_new, prom_az_new, new_err_alt, new_err_az)
            elif len(m_alt[y][x]) and samsize:
                new_samsize = samsize + len(m_alt[y][x])
                prom_alt_old = self[indx, "alt"]
                prom_az_old = self[indx, "az"]
                prom_alt_new = (prom_alt_old*samsize
                                            + sum(m_alt[y][x]))/new_samsize
                prom_az_new = (prom_az_old*samsize
                                            + sum(m_az[y][x]))/new_samsize
                new_err_alt = self._merge_dataframe_new_row_desviation(indx,
                        samsize, "alt_err", prom_alt_old, m_alt[y][x])
                new_err_az = self._merge_dataframe_new_row_desviation(indx,
                            samsize, "az_err", prom_az_old, m_az[y][x])
                self._merge_dataframe_save_row(indx, new_samsize,
                    prom_alt_new, prom_az_new, new_err_alt, new_err_az)
            lib.printProgressBar(indx, total)
        print("Done")
        self.preview = ImageHandler(self.df)

    def _merge_dataframe_extract_3dmatrix(self, df):
        total = df.shape[0]
        m_alt = lib.create_empty_matrix(self.Y_RESOLUTION,self.X_RESOLUTION)
        m_az = lib.create_empty_matrix(self.Y_RESOLUTION,self.X_RESOLUTION)
        print("\nTamaño de la nueva muestra: {}".format(total))
        print("Extrayendo altura y azimuth...")
        lib.printProgressBar(0, total)
        for i in df.index:
            x = int(df.at[i,'xcentroid'])
            y = int(df.at[i,'ycentroid'])
            m_alt[y][x].append(df.at[i,'alt'])
            m_az[y][x].append(df.at[i,'az'])
            lib.printProgressBar(i, total)
        print("Done")
        return m_alt, m_az

    def _merge_dataframe_save_row(self, indx, new_samsize, prom_alt_new, prom_az_new, new_err_alt, new_err_az):
        self[indx, "sample_size"] = new_samsize
        self[indx, "alt"] = prom_alt_new
        self[indx, "az"] = prom_az_new
        self[indx, "alt_err"] = new_err_alt
        self[indx, "az_err"] = new_err_az

    def _merge_dataframe_new_row_desviation(self, indx, samsize, col, prom_old, m):
        #esto podria ser una funcion
        s_n = (self[indx, col]*samsize)**2
        prom_i_old = prom_old
        for i, x_i in enumerate(m):
            prom_i = (prom_i_old * (samsize + i) + x_i)/(samsize + i + 1)
            s_n = s_n + (x_i - prom_i_old)*(x_i - prom_i)
            prom_i_old = prom_i
        new_samsize = samsize + len(m)
        return np.sqrt(s_n/new_samsize)

    def __getitem__(self, coords):
        if len(coords) == 2 and type(coords[1])==int:
            x, y = coords
            return self.df.query("x == {} and y == {}".format(x, y))
        elif len(coords) == 2 and type(coords[1])==str:
            i, col = coords
            return self.df.at[i,col]
        elif len(coords) == 3:
            x, y, col = coords
            return self.df.query("x == {} and y == {}".format(x,
                                                            y))[col].values[0]

    def __setitem__(self, coords, value):
        if len(coords) == 2:
            i, col = coords
            self.df.at[i,col] = value
        elif len(coords) == 3:
            x, y, col = coords
            self.df.loc[self.df.eval("x == {} and y == {}".format(x, y)),
                                                                col] = value

class InterpolatedPixelTable(PixelTable):
    def __init__(self, table):
        super().__init__(new_matrix = True)
        self.init_interpolation(table)

    def init_interpolation(self, table):
        print("Iniciando interpolacion de filas y columnas...")
        df_rows = self._interpolate_df(table.df, by="y")
        df_cols = self._interpolate_df(table.df, by="x")
        print("Interpolacion finalizada.")
        df = pd.concat([df_rows, df_cols], ignore_index=True)
        df = df.groupby(['xcentroid',"ycentroid"], as_index=False).mean()
        self.merge_dataframe(df)


    def _interpolate_df(self, data, by):
        """
        data: dataframe del tipo .pixtab
        by: determina si se interpolan filas o columnas

        retorna un dataframe del tipo .dat
        """
        if by=="x":
            x = "y"
            var_cte_range = range(P.X_MIN, P.X_MAX)
            total = P.X_MAX
            ini = P.X_MIN
        elif by=="y":
            x = "x"
            var_cte_range = range(P.Y_MIN, P.Y_MAX)
            total = P.Y_MAX
            ini = P.Y_MIN
        var_cte = by
        query_str = "{}<=x<={} and {}<=y<={}".format(P.X_MIN, P.X_MAX,
                                                            P.Y_MIN, P.Y_MAX)
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
                    if x_2>x_val-P.INTERP_THRESHOLD:
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

class InterpolatedPixelTablebycenter(PixelTable):
    """
    Primero calcula el posible cenith según lo que entregue el módulo
    circles_detector (carpeta)
    Luego hace el merge con una tabla vacía
    """
    def __init__(self, table):
        super().__init__(new_matrix = True)
        self.init_interpolation(table)

    def init_interpolation(self, table):
        print("Calculando cenith...")
        self._get_cenith()
        print("Iniciando interpolación con cenith x: {}, y: {}...".format(
                                                self.x_center, self.y_center))
        df = self._interpolate_df(table.df)
        print("Interpolacion finalizada.")
        self.merge_dataframe(df)

    def _interpolate_df(self, data):
        """
        data: dataframe del tipo .pixtab
        by: determina si se interpolan filas o columnas

        retorna un dataframe del tipo .dat
        """
        query_str = "{}<=x<={} and {}<=y<={}".format(P.X_MIN, P.X_MAX,
                                                            P.Y_MIN, P.Y_MAX)
        data = data.dropna(thresh = 7).query(query_str)
        df_header = ["xcentroid", "ycentroid", "alt", "az"]
        df_data = []
        r_range = np.linspace(0, P.MAX_RADIO, P.RADIO_STEPS)
        lib.printProgressBar(0, P.MAX_RADIO)
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
            lib.printProgressBar(r, P.MAX_RADIO)
        print("Done!\n")
        df = pd.DataFrame(df_data, columns= df_header)
        return df.dropna(thresh = 4)

    def _get_cenith(self):
        circle = circle_detector()
        self.x_center = int(circle.detections_mean[1])
        self.y_center = int(circle.detections_mean[0])
