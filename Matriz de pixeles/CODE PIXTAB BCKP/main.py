import os
from class_pixeltable import PixelTable, InterpolatedPixelTable, InterpolatedPixelTablebycenter
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import lib as lib
from scipy import interpolate
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
    table = PixelTable(data_path = "Interpolated_Data.pixtab")
    table.preview.alt
    table.preview.az
    if P.SAVE_PREVIEW:
        path_image = (cwd + os.sep + P.PREVIEW_IMAGES_FOLDER + os.sep)
        table.preview.save(path_image + "Interpolated_Data_")
        # table.save_preview_image_az(cwd+os.sep+path_image)
    """                            """

    """ obtener altura y azimuth según pixeles """
    # table = PixelTable(data_path = "Data.pixtab")
    # table = PixelTable(data_path = "Interpolated_Data.pixtab")
    # x = 730
    # y = 740
    # print(table.df.query("x==730").dropna())
    """                                        """

    """ obtener pixeles según altura y azimuth """
    # table = PixelTable(data_path = "Data.pixtab")
    # az = 30
    # alt = 31
    # print(table.df["x"].dropna().values)
    # print(table.df.query("alt == {} and az == {}".format(alt, az)))
    """                                        """

    """ detector de circulos """
    # circle_detector()
    """                      """
