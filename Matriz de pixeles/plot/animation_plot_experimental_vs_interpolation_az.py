import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
from class_pixeltable import PixelTable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as np


EXP_PATH = ".." + os.sep + "Data.pixtab"
# EXP_PATH = ".." + os.sep + "drop_outlayers.pixtab"
INT_PATH = ".." + os.sep + "Interpolated_Data[pipeline].pixtab"


CTE_PARAM = "az"
X_AXIS = "x"
Y_AXIS = "y"

SAVE_PATH = None
# SAVE_PATH = "plot_doble_azimut_map.mp4"

def update_lines(i, tables, lines, title, cte_param, x_axis, y_axis):
    title.set_text('$Xi^2_a=15.75$ Interpolated data on Az={}'.format(i))
    for line, table in zip(lines, tables):
        # NOTE: there is no .set_data() for 3 dim data...
        n_table = table.df.query("({}>{} and {}<={}) or ({}<360-{} and {}>=360-{})".format(cte_param, i-1, cte_param, i, cte_param, i-1, cte_param, i))
        # n_table = table.df.query("{}>{} and {}<={}".format(cte_param, i-1, cte_param, i))
        x_dat = n_table[x_axis].values
        y_dat = n_table[y_axis].values
        line.set_data(x_dat, y_dat)
    return lines

def animation_plot_experimental_vs_interpolation(experimental_table,
                                        interpolated_table,
                                         cte_param = CTE_PARAM,
                                         x_axis = X_AXIS,
                                         y_axis = Y_AXIS,
                                         save_path = SAVE_PATH):

    exp_n_table = experimental_table.df.query("({}>0 and {}<=1) or ({}<360-0 and {}>=360-1)".format(cte_param,
                                                                    cte_param, cte_param, cte_param))
    # exp_n_table = experimental_table.df.query("{}>0 and {}<=1".format(cte_param, cte_param))
    exp_x_dat = exp_n_table[x_axis].values
    exp_y_dat = exp_n_table[y_axis].values

    int_n_table = interpolated_table.df.query("({}>0 and {}<=1) or ({}<360-0 and {}>=360-1)".format(cte_param,
                                                                    cte_param, cte_param, cte_param))
    # int_n_table = interpolated_table.df.query("{}>0 and {}<=1".format(cte_param, cte_param))
    int_x_dat = int_n_table[x_axis].values
    int_y_dat = int_n_table[y_axis].values

    fig, ax = plt.subplots()

    ax.plot(experimental_table.df.dropna()[x_axis].values,
     experimental_table.df.dropna()[y_axis].values, "g*", markersize=0.5, label = "Experimental")[0]

    tables = [experimental_table, interpolated_table]
    # lines = [ax.plot(exp_x_dat, exp_y_dat, "r*",
    #                                     markersize=4, label = "Experimental")[0],
    #                 ax.plot(int_x_dat, int_y_dat, "b",
    #                                 linewidth=1, label = "Interpolation")[0]]
    lines = [ax.plot(exp_x_dat, exp_y_dat, "r*",
                                        markersize=4, label = "Experimental")[0],
                    ax.plot(int_x_dat, int_y_dat, "bo", markersize=0.1,
                                    linewidth=0.1, label = "Interpolation")[0]]

    ax.set_xlim([0.0, 1200.0])
    ax.set_xlabel('{} Pixel'.format(x_axis.upper()))

    ax.set_ylim([900.0, 0.0])
    ax.set_ylabel('{} Pixel'.format(y_axis.upper()))

    title = ax.set_title('$Xi^2_a=15.73$ Interpolated data')
    plt.legend(loc='upper right')

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_lines, [*range(2,360),*range(1,360)],
                                            fargs=(tables, lines, title,
                                                cte_param, x_axis, y_axis),
                                            interval=1, blit=False)
    if save_path:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Carlos Quezada'), bitrate=1800)
        line_ani.save("animations" + os.sep + save_path, writer = writer)

    plt.show()

    return line_ani

if __name__=="__main__":
    experimental_table = PixelTable(data_path = EXP_PATH)
    interpolated_table = PixelTable(data_path = INT_PATH)
    animation_plot_experimental_vs_interpolation(experimental_table, interpolated_table)
