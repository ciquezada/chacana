import os
from class_pixeltable import PixelTable, InterpolatedPixelTable, InterpolatedPixelTablebycenter
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import lib as lib
from surface_test import show_surface, test_surface
from scipy import interpolate
from metrics import plot_interpolation_vs_experimental, plot_experimental_pixel_row, animation_3d_plot_interpolation_vs_experimental, animation_plot_interpolation_vs_experimental
from circles_detector.class_circle_detector import circle_detector
from scipy import stats




class P:
    #######################
    """ Merge Parameters """
    #######################
    """ New Table or Open Table """
    NEW_MATRIX = False  # True para empezar desde cero
    PATH_ACTUAL_DATA = "Data.pixtab"

    """ Merge new data? """
    MERGE = False    # Si es False no habrá ningún cambio
    PATH_NEW_DATA = "Carlos.dat"

    """ Save changes? """
    SAVE = False
    PATH_OUTPUT_FILE = "Data.pixtab"

    """ Save pixtab copy backup?"""
    SAVE_BCKP = False
    BCKP_FILE_FOLDER = "pixtab_bckps"
    PATH_OUTPUT_BCKP_FILE = "Data_{}.pixtab"

    """ Save image preview """
    # PREVIEW_IMAGES_FOLDER = "preview_images"
    # PATH_PREVIEW_IMAGE = "Data_{}_Preview.png"
    PREVIEW_IMAGES_FOLDER = "interpolated_preview_images"
    PATH_PREVIEW_IMAGE = "Interpolated_Data_{}_Preview.png"
    SAVE_PREVIEW = True

    """ Log """
    LOG_FOLDER = "logs"
    PATH_LOG = "logs_merge.log"
    TEMPLATE_LOG = "\n[{}]:\nUpdating Pixel Table: {}\nNew data: {}\n"
    TEMPLATE_SAVE_LOG = "Writing on: {}\n"
    TEMPLATE_IMAGE_LOG = "Saving preview image on: {}\n"
    TEMPLATE_BCKP_LOG = "Saving backup pixtab on: {}\n"

    """ Misc """
    TIME_FORMAT = "%d-%m-%Y_%Hh%Mm%Ss"

cwd = os.getcwd()


if __name__=="__main__":
    # rangos sugeridos
    # x: (400, 1100), y: (100, 800)
    # posible centro 757, 472

    """ obtener imagen de la tabla """
    # table = PixelTable(data_path = "Data.pixtab")
    # table = PixelTable(data_path = "Interpolated_Data.pixtab")
    # if P.SAVE_PREVIEW:
    #     time = datetime.now().strftime(P.TIME_FORMAT)
    #     path_image = P.PREVIEW_IMAGES_FOLDER+os.sep+P.PATH_PREVIEW_IMAGE.format(time)
    #     table.save_preview_image(cwd+os.sep+path_image)
        # table.save_preview_image_az(cwd+os.sep+path_image)
    """                            """

    """ vista previa de la superficie (alt) """
    # table = PixelTable(new_matrix = P.NEW_MATRIX, data_path = P.PATH_ACTUAL_DATA)
    # test_surface(table)
    # interpolated_table = PixelTable(data_path = "Interpolated_Data.pixtab")
    # test_surface(interpolated_table)
    """                                     """

    """ graficar una linea de pixeles """
    # pos = "x"
    # pixel = 757
    # component = "alt"
    # experimental_path = "Data.pixtab"
    # plot_experimental_pixel_row(pos, pixel, component, experimental_path)
    """                               """

    """ comparar tabla experimental con interpolada """
    # pos = "y"
    # for pixel in range(491,600):
    #     # pixel = 757
    #     component = "alt"
    # experimental_path = "Data.pixtab"
    # interpolated_path = "Interpolated_Data.pixtab"
    # #     plot_interpolation_vs_experimental(pos, pixel, component,
    # #                                     experimental_path, interpolated_path)
    # animation_3d_plot_interpolation_vs_experimental(experimental_path, interpolated_path)


    """                                             """

    """ obtener altura y azimuth según pixeles """
    # table = PixelTable(data_path = "Data.pixtab")
    # table = PixelTable(data_path = "Interpolated_Data.pixtab")
    # x = 730
    # y = 740
    # print(table.df.query("x==730").dropna())
    """                                        """

    """ obtener altura y azimuth según pixeles """
    # table = PixelTable(data_path = "Data.pixtab")
    # az = 30
    # alt = 31
    # print(table.df["x"].dropna().values)
    # print(table.df.query("alt == {} and az == {}".format(alt, az)))
    """                                        """

    """ detector de circulos """
    # circle_detector()
    """                      """
