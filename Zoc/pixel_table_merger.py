import lib as lib
import numpy as np
import lib as lib
import numpy as np
import pandas as pd
from multiprocessing import Pool
from tools import ProgressBarCounter, PBarATP
import time


class MergeError(Exception):
    pass

class Merger:
    PIXTAB_X_RESOLUTION = 1548
    PIXTAB_Y_RESOLUTION = 1040

    def __init__(self):
        pass

    def merge(self, df_pixtab, df_dat):
        df_merged = self.empty_pixtab()
        self._merge_dataframe(df_merged, df_pixtab, df_dat)
        return df_merged

    def _merge_dataframe_multitask(self, df_merged, df_pixtab, df_dat):
#         with Pool(10) as p:
        p = Pool(10)
        pixel_info_list = p.imap(self._worker, self._gen_worker_args(df_pixtab, df_dat))
        p.close()
        p.join()
        print("Exito!")
        filtered_info = filter(lambda x: x, pixel_info_list)
        for info in filtered_info:
            self._save_row(df_merged, **info)


    def _gen_worker_args(self, df_pixtab, df_dat):
        m_alt, m_az = self._extract_3dmatrix(df_dat)
        total = df_pixtab.shape[0]
        print("\nReduciendo y fusionando nuevos datos...")
        for indx in PBarATP(df_pixtab.index, total=total, name="Pixels"):
            yield (indx, m_alt, m_az, df_pixtab)

    def _worker(self, args):
        indx, m_alt, m_az, df_pixtab = args
        x = df_pixtab.at[indx,'x']
        y = df_pixtab.at[indx,'y']
        samsize = df_pixtab.at[indx,"sample_size"]
        # lib.printProgressBar(indx, 1609920)
        if len(m_alt[y][x]) and not samsize:
            pixel_info = self._get_new_pixel(indx, x, y, m_alt, m_az)
            return pixel_info
        elif len(m_alt[y][x]) and samsize:
            pixel_info = self._get_merged_pixel(indx, x, y, m_alt, m_az, samsize, df_pixtab)
            return pixel_info
        elif not len(m_alt[y][x]) and samsize:
            pixel_info = self._get_old_pixel(indx, x, y)
            return pixel_info

    def _merge_dataframe(self, df_merged, df_pixtab, df_dat):
        print("\nIniciando Merger...")
        m_alt, m_az = self._extract_3dmatrix(df_dat)
        # pbar = ProgressBarCounter(df_pixtab.shape[0])
        print("\nReduciendo y fusionando nuevos datos...")
        for indx in PBarATP(df_pixtab.index, name="Pixels"):
            x = df_pixtab.at[indx,'x']
            y = df_pixtab.at[indx,'y']
            samsize = df_pixtab.at[indx,"sample_size"]
            if len(m_alt[y][x]) and not samsize:
                pixel_info = self._get_new_pixel(indx, x, y, m_alt, m_az)
                self._save_row(df_merged, **pixel_info)
            elif len(m_alt[y][x]) and samsize:
                pixel_info = self._get_merged_pixel(indx, x, y, m_alt, m_az, samsize, df_pixtab)
                self._save_row(df_merged, **pixel_info)
            elif not len(m_alt[y][x]) and samsize:
                pixel_info = self._get_old_pixel(indx, x, y)
                self._save_row(df_merged, **pixel_info)
            # pbar.notify()
        time.sleep(1)
        print("Done")

    def _extract_3dmatrix(self, df):
        total = df.shape[0]
        m_alt = lib.create_empty_matrix(self.PIXTAB_Y_RESOLUTION,
                                                    self.PIXTAB_X_RESOLUTION)
        m_az = lib.create_empty_matrix(self.PIXTAB_Y_RESOLUTION,
                                                    self.PIXTAB_X_RESOLUTION)
        print("\nTamaño de la nueva muestra: {}".format(total))
        print("Extrayendo altura y azimuth...")
        # pbar = ProgressBarCounter(total)
        for i in PBarATP(df.index, total, name="New Data"):
            x = int(df.at[i,'xcentroid'])
            y = int(df.at[i,'ycentroid'])
            m_alt[y][x].append(df.at[i,'alt'])
            m_az[y][x].append(df.at[i,'az'])
            # pbar.notify()
        time.sleep(1)
        print("Done")
        return m_alt, m_az

    def _new_row_desviation(self, df_pixtab, indx, samsize, col, prom_old, m):
        #esto podria ser una funcion
        s_n = (df_pixtab.at[indx, col]*samsize)**2
        prom_i_old = prom_old
        for i, x_i in enumerate(m):
            prom_i = (prom_i_old * (samsize + i) + x_i)/(samsize + i + 1)
            s_n = s_n + (x_i - prom_i_old)*(x_i - prom_i)
            prom_i_old = prom_i
        new_samsize = samsize + len(m)
        return np.sqrt(s_n/new_samsize)

    def _get_new_pixel(self, indx, x, y, m_alt, m_az):
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
        return {"indx":indx, "x":x, "y":y, "new_samsize":new_samsize,
            "prom_alt_new":prom_alt_new, "prom_az_new":prom_az_new, "new_err_alt":new_err_alt, "new_err_az":new_err_az}

    def _get_merged_pixel(self, indx, x, y, m_alt, m_az, samsize, df_pixtab):
        new_samsize = samsize + len(m_alt[y][x])
        prom_alt_old = df_pixtab.at[indx, "alt"]
        prom_az_old = df_pixtab.at[indx, "az"]
        prom_alt_new = (prom_alt_old*samsize
                                    + sum(m_alt[y][x]))/new_samsize
        prom_az_new = (prom_az_old*samsize
                                    + sum(m_az[y][x]))/new_samsize
        new_err_alt = self._new_row_desviation(df_pixtab, indx,
                samsize, "alt_err", prom_alt_old, m_alt[y][x])
        new_err_az = self._new_row_desviation(df_pixtab, indx,
                    samsize, "az_err", prom_az_old, m_az[y][x])
        return {"indx":indx, "x":x, "y":y, "new_samsize":new_samsize,
            "prom_alt_new":prom_alt_new, "prom_az_new":prom_az_new, "new_err_alt":new_err_alt, "new_err_az":new_err_az}

    def _get_old_pixel(self, indx, x, y):
        new_samsize = df_pixtab.at[indx, "sample_size"]
        prom_alt_new = df_pixtab.at[indx, "alt"]
        prom_az_new = df_pixtab.at[indx, "az"]
        new_err_alt = df_pixtab.at[indx, "alt_err"]
        new_err_az = df_pixtab.at[indx, "az_err"]
        return {"indx":indx, "x":x, "y":y, "new_samsize":new_samsize,
            "prom_alt_new":prom_alt_new, "prom_az_new":prom_az_new, "new_err_alt":new_err_alt, "new_err_az":new_err_az}

    def _save_row(self, df_merged, indx, x, y, new_samsize, prom_alt_new, prom_az_new, new_err_alt, new_err_az, **kwargs):
        if df_merged.at[indx, "x"] == x and df_merged.at[indx, "y"] == y:
            df_merged.at[indx, "sample_size"] = new_samsize
            df_merged.at[indx, "alt"] = prom_alt_new
            df_merged.at[indx, "az"] = prom_az_new
            df_merged.at[indx, "alt_err"] = new_err_alt
            df_merged.at[indx, "az_err"] = new_err_az
        else:
            err = "FORMATO EN EL PIXTAB INCORRECTO (pixtab: x,y = {},{}) (new_pixtab: x,y = {},{})"
            raise MergeError(err.format(x,y,df_merged.at[indx, "x"],
                                                    df_merged.at[indx, "y"]))

    @staticmethod
    def empty_pixtab():
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        for j in range(Merger.PIXTAB_Y_RESOLUTION):
            for i in range(Merger.PIXTAB_X_RESOLUTION):
                df_data.append([i, j, np.NaN, np.NaN, np.NaN, np.NaN, 0])
        return pd.DataFrame(df_data, columns= df_header)
