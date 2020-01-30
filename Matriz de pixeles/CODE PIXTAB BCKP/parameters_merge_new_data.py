#######################
""" Merge Parameters """
#######################
""" New Table or Open Table """
NEW_MATRIX = True  # True para empezar desde cero
PATH_ACTUAL_DATA = "Data.pixtab"

""" Merge new data? """
MERGE = True    # Si es False no habrá ningún cambio
PATH_NEW_DATA = "drop_outlayer.dat"

""" Save changes? """
SAVE = True
PATH_OUTPUT_FILE = "drop_outlayers.pixtab"

""" Save pixtab copy backup?"""
SAVE_BCKP = False
BCKP_FILE_FOLDER = "pixtab_bckps"
PATH_OUTPUT_BCKP_FILE = "Data_{}.pixtab"

""" Save image preview """
PREVIEW_IMAGES_FOLDER = "preview_images"
SAVE_PREVIEW = False
PATH_PREVIEW_IMAGE = "Data_{}_Preview.png"

""" Log """
LOG_FOLDER = "logs"
PATH_LOG = "logs_merge.log"
TEMPLATE_LOG = "\n[{}]:\nUpdating Pixel Table: {}\nNew data: {}\n"
TEMPLATE_SAVE_LOG = "Writing on: {}\n"
TEMPLATE_IMAGE_LOG = "Saving preview image on: {}\n"
TEMPLATE_BCKP_LOG = "Saving backup pixtab on: {}\n"

""" Misc """
TIME_FORMAT = "%d-%m-%Y_%Hh%Mm%Ss"
