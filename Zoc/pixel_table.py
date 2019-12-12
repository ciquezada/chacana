from pixel_table_image_handler import ImageHandler
from pixel_table_merger import Merger
from datetime import datetime
import parameters_pixeltable as P
import numpy as np
import pandas as pd


class PixelTable:
    """
    Por ahora solo con alt y az
    contiene informacion de un lienzo de 1548x1040 pixeles
    """
    X_RESOLUTION = P.X_RESOLUTION
    Y_RESOLUTION = P.Y_RESOLUTION
    NAME = "Data"
    EXTENSION = ".pixtab"
    TIME_FORMAT = "%m-%d-%Y_%Hh%Mm%Ss"

    def __init__(self, from_file = False):
        if not from_file:
            self.df = self.empty_pixtab()
        else:
            self.df = pd.read_csv(from_file, sep=" ")
        self.preview = ImageHandler(self.df)
        self._merger = Merger()

    @staticmethod
    def empty_pixtab():
        df_header = ["x", "y", "alt", "az", "alt_err", "az_err", "sample_size"]
        df_data = []
        for j in range(P.Y_RESOLUTION):
            for i in range(P.X_RESOLUTION):
                df_data.append([i, j, np.NaN, np.NaN, np.NaN, np.NaN, 0])
        return pd.DataFrame(df_data, columns= df_header)

    def export_to_file(self):
        """
        como es un dataframe con un formato especial
        usemos la extension ".pixtab"
        """
        time = datetime.now().strftime(self.TIME_FORMAT)
        file_name = "{}_".format(time) + self.NAME + self.EXTENSION
        self.df.to_csv(file_name, sep=' ', index=False)
        return 1

    def merge(self, dat):
        df_merged_pixtab = self._merger.merge(self.df, dat)
        self.df = df_merged_pixtab
        self.preview = ImageHandler(self.df)

    def interpolation(self, interpolator_class):
        interpolator = interpolator_class()
        interpolated_df = interpolator.interpolate_pixtab(self.df)
        interpolated_table = PixelTable()
        interpolated_table.NAME = "Interpolated_Data"
        interpolated_table.merge(interpolated_df)
        return interpolated_table
