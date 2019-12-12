import imageio
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from tools import ProgressBarCounter, PBarATP
from multiprocessing import Pool
import time


class ImageHandler:

    TIME_FORMAT = "%m-%d-%Y_%Hh%Mm%Ss"
    PATH_MASK = "black_mask.png"
    NUM_PROC = 10

    def __init__(self, pixels, *args, **kwargs):
        self._pixels = pixels
        self._image_alt = None
        self._image_az = None

    @property
    def alt(self):
        if not isinstance(self._image_alt, type(np.array([]))):
            self.create()
        plt.imshow(self._image_alt)
        plt.axis("off")
        plt.show()

    @property
    def az(self):
        if not isinstance(self._image_az, type(np.array([]))):
            self.create()
        plt.imshow(self._image_az)
        plt.axis("off")
        plt.show()

    def save(self):
        if not isinstance(self._image_az, type(np.array([]))):
            self.create()
        time = datetime.now().strftime(self.TIME_FORMAT)
        imageio.imwrite("{}_altitude.png".format(time), self._image_alt)
        imageio.imwrite("{}_azimuth.png".format(time), self._image_az)

    def create(self):
        print("\nCreando vista previa de pixeles")
        self._image_alt = imageio.imread(self.PATH_MASK)
        self._image_az = imageio.imread(self.PATH_MASK)
        # pbar = ProgressBarCounter(self._pixels.shape[0])
        for indx in PBarATP(self._pixels.index, name="Pixels"):
            x = self._pixels.at[indx,'x']
            y = self._pixels.at[indx,'y']
            alt = self._pixels.at[indx, "alt"]
            az = self._pixels.at[indx, "az"]
            self._coloring_pixels_alt(x, y, alt)
            self._coloring_pixels_az(x, y, az)
            # pbar.notify()
        print("Exito!")

    def _coloring_pixels_alt(self, x, y, val):
        c = [*range(0,86,20)]
        if not np.isnan(val):
            # if 88 <= val < 90:
            #     new_im[y,x,0] = 250
            if any([*(c[i-1]<=val<c[i] for i in range(1, len(c), 3))]):
                self._image_alt[y,x,0] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(2, len(c), 3))]):
                self._image_alt[y,x,1] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(3, len(c), 3))]):
                self._image_alt[y,x,2] = 250
            elif 80 <= val < 85:
                self._image_alt[y,x,1] = 250
            elif 85 <= val:
                self._image_alt[y,x,0] = 140
                self._image_alt[y,x,1] = 140
                self._image_alt[y,x,2] = 250
            else:
                self._image_alt[y,x,0] = 250
                self._image_alt[y,x,1] = 250
                self._image_alt[y,x,2] = 250

    def _coloring_pixels_az(self, x, y, val):
        c = [*range(0,360,20)]
        if not np.isnan(val):
            # if 88 <= val < 90:
            #     new_im[y,x,0] = 250
            if any([*(c[i-1]<=val<c[i] for i in range(1, len(c), 3))]):
                self._image_az[y,x,0] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(2, len(c), 3))]):
                self._image_az[y,x,1] = 250
            elif any([*(c[i-1]<=val<c[i] for i in range(3, len(c), 3))]):
                self._image_az[y,x,2] = 250
            elif 340 <= val:
                self._image_az[y,x,0] = 250
                self._image_az[y,x,1] = 250
                self._image_az[y,x,2] = 250
