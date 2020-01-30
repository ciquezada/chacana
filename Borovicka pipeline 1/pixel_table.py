from pixel_table_image_handler import ImageHandler, ImageHandlerPlot
from pixel_table_merger import Merger
from pixel_table_interpolators import InterpolatorSimple, InterpolatorBycenter, InterpolatorBorovicka
from datetime import datetime
import numpy as np
import pandas as pd

X_RESOLUTION = 1548
Y_RESOLUTION = 1040


class PixelTable:
    """
    Por ahora solo con alt y az
    contiene informacion de un lienzo de 1548x1040 pixeles
    """
    X_RESOLUTION = X_RESOLUTION
    Y_RESOLUTION = Y_RESOLUTION
    X_MIN = 300
    X_MAX = 1201
    Y_MIN = 0
    Y_MAX = 901
    NAME = "Data_corrected_1"
    EXTENSION = ".pixtab"
    TIME_FORMAT = "%d-%m-%Y_%Hh%Mm%Ss"

    def __init__(self, from_file = False, ihandler = "simple", *args, **kwargs):
        self.ihandler = ihandler
        self.ihandler_list = {"simple":ImageHandler, "plot": ImageHandlerPlot}
        if not from_file:
            self.df = self.empty_pixtab()
        else:
            self.df = pd.read_csv(from_file, sep=" ")
        self.preview = self.ihandler_list[ihandler](self.df)
        self._merger = Merger()
        self.interpolator_list = {"borovicka": InterpolatorBorovicka,
                                    "simple": InterpolatorSimple,
                                    "bycenter": InterpolatorBycenter}

    @staticmethod
    def empty_pixtab():
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        Y_MIN = PixelTable.Y_MIN
        Y_MAX = PixelTable.Y_MAX
        X_MIN = PixelTable.X_MIN
        X_MAX = PixelTable.X_MAX
        x = np.arange(X_MIN, X_MAX)
        y = np.arange(Y_MIN, Y_MAX)
        X, Y = np.meshgrid(x, y)
        for row_x, row_y in zip(X,Y):
            for x, y in zip(row_x, row_y):
                df_data.append([int(x), int(y), np.NaN, np.NaN, np.NaN, np.NaN, 0])
        return pd.DataFrame(df_data, columns= df_header)

    def save(self):
        """
        como es un dataframe con un formato especial
        usemos la extension ".pixtab"
        """
        time = datetime.now().strftime(self.TIME_FORMAT)
        file_name = "{}_".format(time) + self.NAME + self.EXTENSION
        self.df.to_csv(file_name, sep=' ', index=False)
        return 1

    def merge(self, dat):
        """
        dat es un dataframe["xcentroid","ycentroid","alt","az"]
        """
        df_merged_pixtab = self._merger.merge(self.df, dat)
        self.df = df_merged_pixtab
        self.preview = self.ihandler_list[self.ihandler](self.df)

    def interpolate(self, by, *args, **kwargs):
        interpolator = self.interpolator_list[by](*args, **kwargs)
        interpolated_df = interpolator.interpolate_pixtab(pixtab_df = self.df.copy(),
                                                                *args, **kwargs)
        interpolated_table = PixelTable(ihandler = self.ihandler)
        interpolated_table.NAME = "Interpolated_Data"
        interpolated_table.merge(interpolated_df)
        return interpolated_table

if __name__ == "__main__":
    """ mergear pixtab con un archivo .dat """
    pixtab = PixelTable(ihandler="plot")
    dat = pd.read_csv("01-29-2020_13h34m09s_updated_catalog.dat", sep=" ")
    pixtab.merge(dat)
    # pixtab.save()

    """ interpolar pixtab con borovicka """
    # X0, Y0, a0 = 724, 472, 0
    # C, A, F = 1.11782417, 0, 0
    # V, S, D, P, Q = 0.003, 0.0001, 0.00001, 0, 0
    # E, ep = 0, 0.001
    # params = [C, A, F, V, S, D, P, Q, E, ep, X0, Y0, a0]
    # pixtab = PixelTable(ihandler = "plot")
    # before_borovicka_pixtab = pixtab.interpolate("borovicka", save = False)
    # before_borovicka_pixtab.preview.alt
    # before_borovicka_pixtab.preview.az
    after_borovicka_pixtab = pixtab.interpolate("borovicka", update_params=True, save = False)
    after_borovicka_pixtab.preview.alt
    after_borovicka_pixtab.preview.az

    # after_borovicka_pixtab.save()

    """ cargar pixtab para mirarlo """
    # pixtab = PixelTable("Interpolated_Data[pipeline a0].pixtab", ihandler="plot")
    # pixtab.preview.save()
