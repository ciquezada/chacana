#######################
""" Merge Parameters """
#######################
""" Open Table """
NEW_MATRIX = False  # Debe ser False o se interpolará una matriz vacía
PATH_ACTUAL_DATA = "Data.pixtab"

""" Save changes? """
SAVE = True
PATH_OUTPUT_FILE = "Interpolated_Data.pixtab"

""" Save pixtab copy backup?"""
SAVE_BCKP = True
BCKP_FILE_FOLDER = "interpolated_pixtab_bckps"
PATH_OUTPUT_BCKP_FILE = "Interpolated_Data_{}.pixtab"

""" Save image preview """
PREVIEW_IMAGES_FOLDER = "interpolated_preview_images"
SAVE_PREVIEW = False
PATH_PREVIEW_IMAGE = "Interpolated_Data_{}_Preview.png"

""" Log """
LOG_FOLDER = "logs"
PATH_LOG = "logs_interpolation.log"
TEMPLATE_LOG = "\n[{}]:\nInterpolating Pixel Table: {}\n"
TEMPLATE_SAVE_LOG = "Writing on: {}\n"
TEMPLATE_IMAGE_LOG = "Saving preview image on: {}\n"
TEMPLATE_BCKP_LOG = "Saving backup pixtab on: {}\n"


""" Misc """
TIME_FORMAT = "%d-%m-%Y_%Hh%Mm%Ss"
