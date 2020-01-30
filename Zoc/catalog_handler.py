import pandas as pd
import numpy as np
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from pixel_table import PixelTable
from pixel_table_image_handler import ImageHandler
from multiprocessing import Pool
import imageio
import matplotlib.pyplot as plt
from datetime import datetime
from tools import PBarATP


CATALOG_PATH = "bsc5.dat"
EL_SAUCE = EarthLocation(lat=-30.4726064*u.deg, lon=-70.7653747*u.deg, height=789*u.m)
BEST_QUERY = "alt > 20 and Vmag < 4"
# PIXTAB_PATH = "09-10-2019_05h24m41s_Interpolated_Data_handcraft.pixtab"
PIXTAB_PATH = "Interpolated_Data[pipeline].pixtab"

OBS_TIME = [
            "2019-9-7 08:30:10"
            # "2019-9-10 09:00:02",
            # "2019-9-10 09:15:17",
            # "2019-9-10 09:29:58",
            # "2019-9-10 09:45:04",
            # "2019-9-10 10:00:00"
            ]

class Catalog():
    PLACE = EL_SAUCE
    # utcoffset = -4*u.hour
    NUM_PROC = 10

    def __init__(self, path, time):
        print("Cargando catalogo")
        df = self.load_catalog(path, time)
        self.df = df.query(BEST_QUERY).sort_values("Vmag")
        print("Exito...")

    def load_catalog(self, path, time):
        alt_az_frame = AltAz(obstime=time,location=self.PLACE)
        header = ["star_name", "Vmag", "ra", "dec", "alt", "az",
                                            "astropy_coords", "astropy_altaz"]
        p = Pool(self.NUM_PROC)
        raw_data = p.imap(self._worker_read_catalog,
                    self._gen_worker_args_read_catalog(path, alt_az_frame))

        data = pd.DataFrame(raw_data, columns = header)
        return data

    def find_on_pixtab(self, df_pixtab):
        print("Ubicando objetos en el pixtab...")
        p = Pool(self.NUM_PROC)
        pixel_list = p.imap(self._worker, self._gen_worker_args(self.df, df_pixtab))
        p.close()
        p.join()
        pixel_df = pd.concat(pixel_list, axis=1, ignore_index=True).transpose()
        # pixel_df["ra"] = pixel_df.astropy_coords.apply(lambda x: x.ra)
        print("Exito!")
        return pixel_df

    def find_nearest_pixel(self, star_data, df_pixtab):
        best_alt_az = ((df_pixtab.dropna().alt - star_data.alt).abs()
                           + (df_pixtab.dropna().az - star_data.az).abs())
        return df_pixtab.loc[best_alt_az.idxmin()]

    def _gen_worker_args(self, catalogue_df, df_pixtab, *args, **kwargs):
        for indx in PBarATP(catalogue_df.index, name="Objects"):
            yield (catalogue_df.loc[indx], df_pixtab)

    def _worker(self, args):
        star_data, df_pixtab= args
        nearest_pixel = self.find_nearest_pixel(star_data, df_pixtab)
        star_data["real_alt"] = star_data["alt"]
        star_data["real_az"] = star_data["az"]
        return nearest_pixel.append(star_data[["star_name", "ra", "dec", "real_alt", "real_az"]])

    def _gen_worker_args_read_catalog(self, path, alt_az_frame):
        with open(path, "r", encoding="utf-8") as file:
            for line in PBarATP(file, 9110, name="{}".format(path)):
                if line.replace("\n","")[75:77] != "  ":
                    yield (line, alt_az_frame)

    def _worker_read_catalog(self, args):
        line, alt_az_frame = args
        star_name = line.replace("\n","")[4:14]
        RAh = line.replace("\n","")[75:77]
        RAm = line.replace("\n","")[77:79]
        RAs = line.replace("\n","")[79:83]
        DE_sign = line.replace("\n","")[83]
        DE_deg = line.replace("\n","")[84:86]
        DE_arcmin = line.replace("\n","")[86:88]
        DE_arcseg = line.replace("\n","")[88:90]
        Vmag = float(line.replace("\n","")[102:107])
        ra = '{}h{}m{}s'.format(RAh,RAm, RAs)
        dec = "{}{}d{}m{}s".format(DE_sign, DE_deg, DE_arcmin, DE_arcseg)
        c = SkyCoord(ra, dec, frame='icrs')
        c_altaz = c.transform_to(alt_az_frame)
        return [star_name, Vmag, ra, dec, c_altaz.alt.value, c_altaz.az.value, c, c_altaz]


class CatalogImageHandler(ImageHandler):

    NUM_PROC = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._image_preview = None

    def create(self):
        print("\nCreando vista previa de pixeles")
        # self._image_alt = imageio.imread(self.PATH_MASK)
        # self._image_az = imageio.imread(self.PATH_MASK)
        self._image_preview = imageio.imread(self.PATH_MASK)
        for indx in PBarATP(self._pixels.index, name="Pixels"):
            x = self._pixels.at[indx,'x']
            y = self._pixels.at[indx,'y']
            # alt = self._pixels.at[indx, "alt"]
            # az = self._pixels.at[indx, "az"]
            # self._coloring_pixels_alt(x, y, alt)
            # self._coloring_pixels_az(x, y, az)
            self._coloring_pixels_preview(x, y)
        print("Exito!")

    def _coloring_pixels_preview(self, x, y):
        for i in range(3):
            for j in range(3):
                self._image_preview[int(y-1+j),int(x-1+i),0] = 250
                self._image_preview[int(y-1+j),int(x-1+i),1] = 250
                self._image_preview[int(y-1+j),int(x-1+i),2] = 250

    def save(self):
        if not isinstance(self._image_preview, type(np.array([]))):
            self.create()
        time = datetime.now().strftime(self.TIME_FORMAT)
        imageio.imwrite("{}_catalog_preview.png".format(time), self._image_preview)

    @property
    def preview(self):
        if not isinstance(self._image_preview, type(np.array([]))):
            self.create()
        plt.imshow(self._image_preview)
        plt.axis("off")
        plt.show()

if __name__=="__main__":
    for obs_time in OBS_TIME:
        catalog = Catalog(CATALOG_PATH, Time(obs_time))
        pixtab = PixelTable(PIXTAB_PATH)
        catalog_pixtab = catalog.find_on_pixtab(pixtab.df)
        print(catalog_pixtab)
        catalog_pixtab.to_csv("catalog.dat", sep=',', index=False)
        # preview = CatalogImageHandler(catalog_pixtab)
        # preview.preview
        # preview.save()
