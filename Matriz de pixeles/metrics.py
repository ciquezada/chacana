from class_pixeltable import PixelTable
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data
import numpy as np
import os

cwd = os.getcwd()

def plot_interpolation_vs_experimental(pos, pixel, component,
                                                    experimental_data_path,
                                                        interpolated_data_path):
    complem_pos = "x" if pos=="y" else "y"
    table = PixelTable(data_path = experimental_data_path)
    x = table.df.query("{}=={}".format(pos, pixel))[complem_pos].values
    y = table.df.query("{}=={}".format(pos, pixel))[component].values

    interpolated_table = PixelTable(data_path = interpolated_data_path)
    xnew = interpolated_table.df.query("{}=={}".format(pos, pixel))[complem_pos].values
    ynew = interpolated_table.df.query("{}=={}".format(pos, pixel))[component].values

    f, ax = plt.subplots()
    ax.set_title('Interpolating {} on {}={}'.format(component.upper(), pos, pixel))
    ax.set_xlabel("{}".format(pos))
    ax.set_ylabel("{}".format(component))
    ax.plot(x, y, "ro", label = "Experimental")
    ax.plot(xnew, ynew, label = "Interpolation")
    ax.legend()
    plt.savefig("metrics"+os.sep+"{}.png".format(pixel))

    # plt.show()

def plot_experimental_pixel_row(pos, pixel, component, experimental_data_path):
    complem_pos = "x" if pos=="y" else "y"
    table = PixelTable(data_path = experimental_data_path)
    x = table.df.query("{}=={}".format(pos, pixel))[complem_pos].values
    y = table.df.query("{}=={}".format(pos, pixel))[component].values
    plt.title('Interpolating {} on {}={}'.format(component.upper(), pos, pixel))
    plt.xlabel("{}".format(pos))
    plt.ylabel("{}".format(component))
    plt.plot(x, y, "ro", label = "Experimental")
    plt.legend()
    plt.show()

def update_lines(x, tables, lines, ax):
    ax.set_title('Interpolating vs Experimental data on x={}'.format(x))
    for line, table in zip(lines, tables):
        # NOTE: there is no .set_data() for 3 dim data...
        n_table = table.df.query("x=={}".format(x))
        y_dat = n_table["y"].values
        alt_dat = n_table["alt"].values
        line.set_data(y_dat, alt_dat)
    return lines

def animation_plot_interpolation_vs_experimental(experimental_data_path,
                                                interpolated_data_path):



    exp_table = PixelTable(data_path = experimental_data_path)
    exp_n_table = exp_table.df.query("x==260")
    exp_y_dat = exp_n_table["y"].values
    exp_alt_dat = exp_n_table["alt"].values

    int_table = PixelTable(data_path = interpolated_data_path)
    int_n_table = int_table.df.query("x==260")
    int_y_dat = int_n_table["y"].values
    int_alt_dat = int_n_table["alt"].values

    # Attaching 3D axis to the figure
    fig, ax = plt.subplots()

    tables = [exp_table, int_table]
    lines = [ax.plot(exp_y_dat, exp_alt_dat, "r*",
                                        linewidth=4, label = "Experimental")[0],
                    ax.plot(int_y_dat, int_alt_dat, "b",
                                    markersize=1, label = "Interpolation")[0]]

    ax.set_xlim([0.0, 900.0])
    ax.set_xlabel('Y Pixel')

    ax.set_ylim([0.0, 100.0])
    ax.set_ylabel('Altitude')

    ax.set_title('Interpolating vs Experimental data')

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_lines, range(261,1200), fargs=(tables, lines, ax),
                                       interval=2, blit=False)



    plt.legend(loc='upper right')

    # line_ani.save("animation.mpeg", writer="ffmpeg")
    plt.show()

def update_3d_lines(x, tables, lines, title):
    title.set_text('Interpolating vs Experimental data on x={}'.format(x))
    for line, table in zip(lines, tables):
        # NOTE: there is no .set_data() for 3 dim data...
        n_table = table.df.query("x=={}".format(x))
        x_dat = n_table["x"].values
        y_dat = n_table["y"].values
        alt_dat = n_table["alt"].values
        line.set_data(x_dat, y_dat)
        line.set_3d_properties(alt_dat)
    return lines

def animation_3d_plot_interpolation_vs_experimental(experimental_data_path,
                                                        interpolated_data_path):



    exp_table = PixelTable(data_path = experimental_data_path)
    exp_n_table = exp_table.df.query("x==260")
    exp_x_dat = exp_n_table["x"].values
    exp_y_dat = exp_n_table["y"].values
    exp_alt_dat = exp_n_table["alt"].values

    int_table = PixelTable(data_path = interpolated_data_path)
    int_n_table = int_table.df.query("x==260")
    int_x_dat = int_n_table["x"].values
    int_y_dat = int_n_table["y"].values
    int_alt_dat = int_n_table["alt"].values

    # Attaching 3D axis to the figure
    fig = plt.figure()
    ax = p3.Axes3D(fig)

    # Creating fifty line objects.
    # NOTE: Can't pass empty arrays into 3d version of plot()
    tables = [exp_table, int_table]
    lines = [ax.plot(exp_x_dat, exp_y_dat, exp_alt_dat, "r*",
                                    linewidth=4, label = "Experimental")[0],
                ax.plot(int_x_dat, int_y_dat, int_alt_dat, "b",
                                markersize=1, label = "Interpolation")[0]]

    # Setting the axes properties
    ax.set_xlim3d([0.0, 1500.0])
    ax.set_xlabel('X Pixel')

    ax.set_ylim3d([0.0, 900.0])
    ax.set_ylabel('Y Pixel')

    ax.set_zlim3d([0.0, 100.0])
    ax.set_zlabel('Altitude')

    title = ax.set_title('Interpolating vs Experimental data')

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_3d_lines, range(261,1200), fargs=(tables, lines, title),
                                       interval=2, blit=False)

    # fn = get_sample_data(cwd + os.sep + "mask.png", asfileobj=False)
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
    # ax.plot_surface(X1, Y1, np.atleast_2d(0.0), rstride=50, cstride=50, facecolors=arr)

    # line_ani.save("animation.mp4", writer="ffmpeg")
    plt.show()
