import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
from class_pixeltable import PixelTable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data
import numpy as np


EXP_PATH = ".." + os.sep + "Data.pixtab"
INT_PATH = ".." + os.sep + "Interpolated_Data.pixtab"

X_AXIS = "x"
Y_AXIS = "y"
Z_AXIS = "alt"

SAVE_PATH = None

def update_3d_lines(i, tables, lines, title, x_axis, y_axis, z_axis):
    title.set_text('Interpolating vs Experimental data on {}={}'.format(x_axis,
                                                                            i))
    for line, table in zip(lines, tables):
        # NOTE: there is no .set_data() for 3 dim data...
        n_table = table.df.query("{}=={}".format(x_axis, i))
        x_dat = n_table[x_axis].values
        y_dat = n_table[y_axis].values
        z_dat = n_table[z_axis].values
        line.set_data(x_dat, y_dat)
        line.set_3d_properties(z_dat)
    return lines

def animation_3d_plot_experimental_vs_interpolation(experimental_table,
                                        interpolated_table,
                                         x_axis = X_AXIS,
                                         y_axis = Y_AXIS,
                                         z_axis = Z_AXIS,
                                         save_path = SAVE_PATH):

    exp_n_table = experimental_table.df.query("{}==260".format(x_axis))
    exp_x_dat = exp_n_table[x_axis].values
    exp_y_dat = exp_n_table[y_axis].values
    exp_z_dat = exp_n_table[z_axis].values


    int_n_table = interpolated_table.df.query("{}==260".format(x_axis))
    int_x_dat = int_n_table[x_axis].values
    int_y_dat = int_n_table[y_axis].values
    int_z_dat = int_n_table[z_axis].values

    fig = plt.figure()
    ax = p3.Axes3D(fig)

    tables = [experimental_table, interpolated_table]
    lines = [ax.plot(exp_x_dat, exp_y_dat, exp_z_dat, "r*",
                                        markersize=4, label = "Experimental")[0],
                    ax.plot(int_x_dat, int_y_dat, int_z_dat, "b",
                                    linewidth=1, label = "Interpolation")[0]]

    # Setting the axes properties
    ax.set_xlim3d([0.0, 1500.0])
    ax.set_xlabel('X Pixel')

    ax.set_ylim3d([0.0, 900.0])
    ax.set_ylabel('Y Pixel')

    ax.set_zlim3d([0.0, 100.0])
    ax.set_zlabel('Altitude')

    title = ax.set_title('Interpolating vs Experimental data')
    plt.legend()

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_3d_lines, range(261,1200),
                                            fargs=(tables, lines, title,
                                                x_axis, y_axis, z_axis),
                                            interval=2, blit=False)

    if save_path:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Carlos Quezada'), bitrate=1800)
        line_ani.save("animations" + os.sep + save_path, writer = writer)

    plt.show()

    return line_ani

if __name__=="__main__":
    experimental_table = PixelTable(data_path = EXP_PATH)
    interpolated_table = PixelTable(data_path = INT_PATH)
    animation_3d_plot_experimental_vs_interpolation(experimental_table, interpolated_table)

    # fn = get_sample_data(cwd + os.sep + "background.png", asfileobj=False)
    # arr = read_png(fn)
    # # 10 is equal length of x and y axises of your surface
    # stepX, stepY = 1549. / arr.shape[0], 1041. / arr.shape[1]
    #
    # X1 = np.arange(0, 1549, 1.)
    # Y1 = np.arange(0, 1041, 1.)
    # X1, Y1 = np.meshgrid(X1, Y1)
    # # stride args allows to determine image quality
    # # stride = 1 work slow
    # print("ok")
    # ax.plot_surface(X1, Y1, np.atleast_2d(0.0), rstride=10, cstride=10, facecolors=arr)
