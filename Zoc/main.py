import pandas as pd
import numpy as np


def load_data(path):
    raw_data = []
    header = ["name", "RAh", "RAm", "RAs", "DE_sign",
                        "DE_deg", "DE_arcmin", "DE_arcseg", "Vmag"]
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            # name = line.replace("\n","")[4:14]
            # RAh = int(line.replace("\n","")[75:77])
            # RAm = int(line.replace("\n","")[77:79])
            # RAs = float(line.replace("\n","")[79:83])
            # DE_sign = line.replace("\n","")[83]
            # DE_deg = int(line.replace("\n","")[84:86])
            # DE_arcmin = int(line.replace("\n","")[86:88])
            # DE_arcseg = int(line.replace("\n","")[88:90])
            # Vmag = float(line.replace("\n","")[102:107])
            name = line.replace("\n","")[4:14]
            RAh = line.replace("\n","")[75:77]
            RAm = line.replace("\n","")[77:79]
            RAs = line.replace("\n","")[79:83]
            DE_sign = line.replace("\n","")[83]
            DE_deg = line.replace("\n","")[84:86]
            DE_arcmin = line.replace("\n","")[86:88]
            DE_arcseg = line.replace("\n","")[88:90]
            Vmag = line.replace("\n","")[102:107]
            raw_data.append([name, RAh, RAm, RAs, DE_sign, DE_deg, DE_arcmin, DE_arcseg, Vmag])

    data = pd.DataFrame(raw_data, columns = header)
    return data
