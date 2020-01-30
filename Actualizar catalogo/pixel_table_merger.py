import numpy as np
import numpy as np
import pandas as pd
from multiprocessing import Pool
from tools import ProgressBar, PBarATP
import time


class MergeError(Exception):
    pass

class Merger:
    PIXTAB_X_RESOLUTION = 1548
    PIXTAB_Y_RESOLUTION = 1040
    X_MIN = 300
    X_MAX = 1200
    Y_MIN = 0
    Y_MAX = 900

    def __init__(self):
        pass

    def merge(self, df_pixtab, df_dat):
        print("\nIniciando Merger...")
        # df_merged = self.empty_pixtab()
        # df_merged = self._merge_dataframe(df_pixtab, df_dat)
        df_merged = self._merge_dataframe_multitask(df_pixtab, df_dat)
        return df_merged

    def _merge_dataframe_multitask(self, df_pixtab, df_dat):
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        p = Pool(10)
        df_data = p.imap(self._worker, self._gen_worker_args(df_pixtab, df_dat), 40000)
        df_merged = pd.DataFrame(df_data, columns= df_header)
        return df_merged

    def _gen_worker_args(self, df_pixtab, df_dat):
        m_alt, m_az = self._extract_3dmatrix(df_dat)
        print("\nReduciendo y fusionando nuevos datos...")
        df = df_pixtab
        for x,y,alt,az,alt_err,az_err,samsize in PBarATP( zip(df.x.values,
                                                        df.y.values,
                                                        df.alt.values,
                                                        df.az.values,
                                                        df.alt_err.values,
                                                        df.az_err.values,
                                                        df.sample_size.values),
                                                        total=len(df.x.values),
                                                                name="Pixels"):

            yield (x,y,alt,az,alt_err,az_err,samsize, m_alt[y][x], m_az[y][x])

    def _worker(self, args):
        x,y,alt,az,alt_err,az_err,samsize, m_alt, m_az  = args
        if len(m_alt) and not samsize:
            pixel_info = self._get_new_pixel(x, y, m_alt, m_az)
            return pixel_info
        elif len(m_alt) and samsize:
            pixel_info = self._get_merged_pixel(x, y, alt, az, alt_err, az_err,
                                                    samsize, m_alt, m_az, samsize)
            return pixel_info
        elif not len(m_alt):
            return [x,y,alt,az,alt_err,az_err,samsize]

    def _merge_dataframe(self, df_pixtab, df_dat):
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        M_alt, M_az = self._extract_3dmatrix(df_dat)
        print("Reduciendo y fusionando nuevos datos...")
        df = df_pixtab
        for x,y,alt,az,alt_err,az_err,samsize in PBarATP( zip(df.x.values,
                                                        df.y.values,
                                                        df.alt.values,
                                                        df.az.values,
                                                        df.alt_err.values,
                                                        df.az_err.values,
                                                        df.sample_size.values),
                                                        total=len(df.x.values),
                                                                name="Pixels"):
            m_alt = M_alt[y][x]
            m_az = M_az[y][x]
            if len(m_alt) and not samsize:
                pixel_info = self._get_new_pixel(x, y, m_alt, m_az)
                df_data.append([x,y,alt,az,alt_err,az_err,samsize])
            elif len(m_alt) and samsize:
                pixel_info = self._get_merged_pixel(x, y, alt, az, alt_err, az_err,
                                                        samsize, m_alt, m_az, samsize)
                df_data.append([x,y,alt,az,alt_err,az_err,samsize])
            elif not len(m_alt):
                df_data.append([x,y,alt,az,alt_err,az_err,samsize])
        df_merged = pd.DataFrame(df_data, columns= df_header)
        time.sleep(1)
        print("Done")
        return df_merged

    def _extract_3dmatrix(self, df):
        total = df.shape[0]
        m_alt = self.create_empty_matrix(self.PIXTAB_Y_RESOLUTION,
                                                    self.PIXTAB_X_RESOLUTION)
        m_az = self.create_empty_matrix(self.PIXTAB_Y_RESOLUTION,
                                                    self.PIXTAB_X_RESOLUTION)
        print("\nTamaño de la nueva muestra: {}".format(total))
        print("Extrayendo altura y azimuth...")
        for x, y, alt, az in PBarATP(zip(df.xcentroid.values, df.ycentroid.values,
                                        df.alt.values, df.az.values),
                                                    total=len(df.alt.values),
                                                             name="New Data"):
            m_alt[y][x].append(alt)
            m_az[y][x].append(az)
        time.sleep(1)
        print("Done")
        return m_alt, m_az

    def _new_row_desviation(self, samsize, old_err, prom_old, m):
        #esto podria ser una funcion
        s_n = (old_err*samsize)**2
        prom_i_old = prom_old
        for i, x_i in enumerate(m):
            prom_i = (prom_i_old * (samsize + i) + x_i)/(samsize + i + 1)
            s_n = s_n + (x_i - prom_i_old)*(x_i - prom_i)
            prom_i_old = prom_i
        new_samsize = samsize + len(m)
        return np.sqrt(s_n/new_samsize)

    def _get_new_pixel(self, x, y, m_alt, m_az):
        prom_alt = np.mean(m_alt)
        prom_az = np.mean(m_az)
        new_samsize = len(m_alt)
        prom_alt_new = prom_alt
        prom_az_new = prom_az
        new_err_alt = np.sqrt(np.mean((np.array(m_alt)
                                    -prom_alt)**2))
        new_err_az = np.sqrt(np.mean((np.array(m_az)
                                    -prom_az)**2))
        #
        # new_err_alt = np.sqrt(np.mean((np.array(m_alt[y][x])
        #                             -prom_alt)**2))/np.sqrt(new_samsize)
        # new_err_az = np.sqrt(np.mean((np.array(m_az[y][x])
        #                             -prom_az)**2))/np.sqrt(new_samsize)
        return [x,y,prom_alt_new,prom_az_new,new_err_alt,new_err_az,new_samsize]

    def _get_merged_pixel(self, x, y, prom_alt_old, prom_az_old,
                                    old_alt_err, old_az_err, samsize,
                                                            m_alt, m_az):
        new_samsize = samsize + len(m_alt)
        prom_alt_new = (prom_alt_old*samsize
                                    + sum(m_alt))/new_samsize
        prom_az_new = (prom_az_old*samsize
                                    + sum(m_az))/new_samsize
        new_err_alt = self._new_row_desviation(samsize, old_alt_err, prom_alt_old, m_alt)
        new_err_az = self._new_row_desviation(samsize, old_az_err, prom_az_old, m_az)
        return [x,y,prom_alt_new,prom_az_new,new_err_alt,new_err_az,new_samsize]

    def _get_old_pixel(self, indx, x, y):
        new_samsize = df_pixtab.at[indx, "sample_size"]
        prom_alt_new = df_pixtab.at[indx, "alt"]
        prom_az_new = df_pixtab.at[indx, "az"]
        new_err_alt = df_pixtab.at[indx, "alt_err"]
        new_err_az = df_pixtab.at[indx, "az_err"]
        return [x,y,prom_alt_new,prom_az_new,new_err_alt,new_err_az,new_samsize]

    @staticmethod
    def create_empty_matrix(y, x):
        im = []
        for i in range(y):
            im.append([])
            for j in range(x):
                im[i].append([])
        return im
