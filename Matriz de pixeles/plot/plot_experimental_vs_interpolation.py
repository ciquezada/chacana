import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
from class_pixeltable import PixelTable
import matplotlib.pyplot as plt


EXP_PATH = ".." + os.sep + "Data.pixtab"
INT_PATH = ".." + os.sep + "Interpolated_Data.pixtab"
CTE_PARAMS = ("x", 757)
X_AXIS = "y"
Y_AXIS = "alt"

SAVE_PATH = "plots"+os.sep+"{}.png"

def plot_experimental_vs_interpolation(experimental_table,
                                        interpolated_table,
                                         cte_params = CTE_PARAMS,
                                         x_axis = X_AXIS,
                                         y_axis = Y_AXIS):
    cte_param, cte_pixel = cte_params

    x = experimental_table.df.query("{}=={}".format(cte_param, cte_pixel))[x_axis].values
    y = experimental_table.df.query("{}=={}".format(cte_param, cte_pixel))[y_axis].values

    xnew = interpolated_table.df.query("{}=={}".format(cte_param, cte_pixel))[x_axis].values
    ynew = interpolated_table.df.query("{}=={}".format(cte_param, cte_pixel))[y_axis].values

    f, ax = plt.subplots()
    ax.set_title('Interpolating {} on {}={}'.format(y_axis.upper(), cte_param, cte_pixel))
    ax.set_xlabel("{}".format(cte_param))
    ax.set_ylabel("{}".format(y_axis))
    ax.plot(x, y, "r*", markersize = 4, label = "Experimental")
    ax.plot(xnew, ynew, "b", linewidth = 1, label = "Interpolation")
    ax.legend()
    # plt.savefig(SAVE.PATH.format(cte_pixel))
    plt.show()
    plt.close()

if __name__=="__main__":
    experimental_table = PixelTable(data_path = EXP_PATH)
    interpolated_table = PixelTable(data_path = INT_PATH)
    plot_experimental_vs_interpolation(experimental_table, interpolated_table)
