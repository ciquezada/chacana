import parameters_merge_new_data as P
import pandas as pd
import os
from datetime import datetime
from class_pixeltable import PixelTable


cwd = os.getcwd()

if __name__=="__main__":
    time = datetime.now().strftime(P.TIME_FORMAT)
    log = P.TEMPLATE_LOG.format(time, P.PATH_ACTUAL_DATA, P.PATH_NEW_DATA)

    table = PixelTable(new_matrix = P.NEW_MATRIX, data_path = P.PATH_ACTUAL_DATA)

    """ Paths: """
    out_path = P.PATH_OUTPUT_FILE
    out_bckp_path = P.BCKP_FILE_FOLDER+os.sep+P.PATH_OUTPUT_BCKP_FILE.format(time)
    path_image = P.PREVIEW_IMAGES_FOLDER+os.sep+P.PATH_PREVIEW_IMAGE.format(time)
    path_log = P.LOG_FOLDER+os.sep+P.PATH_LOG

    """ Merge new data """
    if P.MERGE:
        data = pd.read_csv(P.PATH_NEW_DATA, sep=" ")
        table.merge_dataframe(data)
    if P.SAVE:
        table.export_to_file(out_path)
        log += P.TEMPLATE_SAVE_LOG.format(out_path)
    if P.SAVE_PREVIEW:
        table.save_preview_image(cwd+os.sep+path_image)
        log += P.TEMPLATE_IMAGE_LOG.format(path_image)
    if P.SAVE_BCKP:
        table.export_to_file(cwd+os.sep+out_bckp_path)
        log += P.TEMPLATE_BCKP_LOG.format(out_bckp_path)
    with open(cwd+os.sep+path_log, mode = "a", encoding = "UTF-8") as file:
        file.write(log)
