from catalog_handler import Catalog, CatalogImageHandler
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2
import imageio
from datetime import datetime


TIME_FORMAT = "%m-%d-%Y_%Hh%Mm%Ss"

def onclick(event):
    df = pd.read_csv("temp_pixtab.dat", sep=" ")

    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))
    new_row = pd.DataFrame({"new_x":[int(event.xdata)],
                                                "new_y":[int(event.ydata)]})
    df = df.append(new_row, ignore_index = True)
    df.to_csv("temp_pixtab.dat", sep=' ', index=False)
    print("SAVED!\n")

def get_updated_df(catalog_pixtab, image_path):
    new_df_header = ["new_x", "new_y"]
    new_df_data = []
    new_df = pd.DataFrame(new_df_data, columns= new_df_header)
    new_df.to_csv("temp_pixtab.dat", sep=' ', index=False)

    reference_image = cv2.imread(image_path)
    ax = plt.gca()
    fig = plt.gcf()
    implot = ax.imshow(reference_image[...,::-1])
    plt.axis("off")
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    df = pd.read_csv("temp_pixtab.dat", sep=" ")
    out_df = catalog_pixtab.copy()
    out_df["x"] = df["new_x"]
    out_df["y"] = df["new_y"]
    return out_df

def highlight_pixels(image, pixels):
    for indx in pixels.index:
        x = pixels.at[indx, "x"]
        y = pixels.at[indx, "y"]
        color_red(x, y, image)
        plt.imshow(image)
        plt.axis("off")
        plt.show()
        color_green(x, y, image)

def color_red(x, y, image_preview):
    for i in range(3):
        for j in range(3):
           image_preview[int(y-1+j),int(x-1+i),0] = 250
           image_preview[int(y-1+j),int(x-1+i),1] = 0
           image_preview[int(y-1+j),int(x-1+i),2] = 0

def color_green(x, y, image_preview):
    for i in range(3):
        for j in range(3):
           image_preview[int(y-1+j),int(x-1+i),0] = 0
           image_preview[int(y-1+j),int(x-1+i),1] = 250
           image_preview[int(y-1+j),int(x-1+i),2] = 0


if __name__=="__main__":
    time = datetime.now().strftime(TIME_FORMAT)

    """ cargar el pixtab no completo del catalogo """
    catalog_pixtab = pd.read_csv("updatable_catalog.pixtab", sep=" ")
    catalog_image = CatalogImageHandler(catalog_pixtab).get_image()

    """ mostrar imagen de referencia y obtener pixeles actualizados """
    # updated_catalog_pixtab = get_updated_df(catalog_pixtab,
    #                                 image_path = "img_20190907_08h30m10s.png")
    # catalog_dat = Catalog.catpixtab2dat(updated_catalog_pixtab)
    # catalog_dat.to_csv("{}_updated_catalog.dat".format(time), sep=' ', index=False)


    """ destacar uno a uno los pixeles """
    highlight_pixels(catalog_image, catalog_pixtab)
