import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
from class_pixeltable import PixelTable
import matplotlib.pyplot as plt


PATH = ".." + os.sep + "Data.pixtab"
CTE_PARAMS = ("x", 757)
X_AXIS = "y"
Y_AXIS = "alt"

SAVE_PATH = "plots"+os.sep+"{}.png"

def plot_pixels(table, cte_params = CTE_PARAMS,
                        x_axis = X_AXIS, y_axis = Y_AXIS, **kwargs):
    cte_param, cte_pixel = cte_params

    x = table.df.query("{}=={}".format(cte_param, cte_pixel))[x_axis].values
    y = table.df.query("{}=={}".format(cte_param, cte_pixel))[y_axis].values

    f, ax = plt.subplots()
    ax.set_title('Plotting {} on {}={}'.format(y_axis.upper(), cte_param, cte_pixel))
    ax.set_xlabel("{}".format(cte_param))
    ax.set_ylabel("{}".format(y_axis))
    ax.plot(x, y, label = "pixel data", **kwargs)
    ax.legend()
    # plt.savefig(SAVE.PATH.format(cte_pixel))
    plt.show()
    plt.close()

if __name__=="__main__":
    table = PixelTable(data_path = PATH)
    plot_pixels(table)
