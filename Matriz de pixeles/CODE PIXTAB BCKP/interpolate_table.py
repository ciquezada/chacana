import os
import parameters_interpolate_table as P
from class_pixeltable import PixelTable, InterpolatedPixelTable, InterpolatedPixelTablebycenter, InterpolatedPixelTablebyBorovicka
from datetime import datetime


cwd = os.getcwd()

if __name__=="__main__":
    time = datetime.now().strftime(P.TIME_FORMAT)
    log = P.TEMPLATE_LOG.format(time, P.PATH_ACTUAL_DATA)

    # table = PixelTable(new_matrix = P.NEW_MATRIX, data_path = P.PATH_ACTUAL_DATA)

    """ Paths: """
    out_path = P.PATH_OUTPUT_FILE
    out_bckp_path = P.BCKP_FILE_FOLDER+os.sep+P.PATH_OUTPUT_BCKP_FILE.format(time)
    path_image = P.PREVIEW_IMAGES_FOLDER+os.sep+P.PATH_PREVIEW_IMAGE.format(time)
    path_log = P.LOG_FOLDER+os.sep+P.PATH_LOG

    """  Interpolate Table """
    # new_table = InterpolatedPixelTable(table)
    # new_table = InterpolatedPixelTablebycenter(table)
    new_table = InterpolatedPixelTablebyBorovicka()
    if P.SAVE:
        new_table.export_to_file(out_path)
        log += P.TEMPLATE_SAVE_LOG.format(out_path)
    if P.SAVE_PREVIEW:
        new_table.preview.save(cwd+os.sep+path_image)
        log += P.TEMPLATE_IMAGE_LOG.format(path_image)
    if P.SAVE_BCKP:
        new_table.export_to_file(cwd+os.sep+out_bckp_path)
        log += P.TEMPLATE_BCKP_LOG.format(out_bckp_path)
    with open(cwd+os.sep+path_log, mode = "a", encoding = "UTF-8") as file:
        file.write(log)
