import sys
import os
cwd = os.getcwd()
sys.path.append(cwd + os.sep + "..")
from class_pixeltable import PixelTable
import matplotlib.pyplot as plt
import matplotlib.animation as animation


EXP_PATH = ".." + os.sep + "Data.pixtab"
INT_PATH = ".." + os.sep + "Interpolated_Data.pixtab"

CTE_PARAM = "x"
X_AXIS = "y"
Y_AXIS = "alt"

SAVE_PATH = None

def update_lines(i, tables, lines, title, cte_param, x_axis, y_axis):
    title.set_text('Interpolating vs Experimental data on x={}'.format(i))
    for line, table in zip(lines, tables):
        # NOTE: there is no .set_data() for 3 dim data...
        n_table = table.df.query("{}=={}".format(cte_param, i))
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

    exp_n_table = experimental_table.df.query("{}==260".format(cte_param))
    exp_x_dat = exp_n_table[x_axis].values
    exp_y_dat = exp_n_table[y_axis].values

    int_n_table = interpolated_table.df.query("{}==260".format(cte_param))
    int_x_dat = int_n_table[x_axis].values
    int_y_dat = int_n_table[y_axis].values

    fig, ax = plt.subplots()

    tables = [experimental_table, interpolated_table]
    lines = [ax.plot(exp_x_dat, exp_y_dat, "r*",
                                        markersize=4, label = "Experimental")[0],
                    ax.plot(int_x_dat, int_y_dat, "b",
                                    linewidth=1, label = "Interpolation")[0]]

    ax.set_xlim([0.0, 900.0])
    ax.set_xlabel('{} Pixel'.format(x_axis.upper()))

    ax.set_ylim([0.0, 100.0])
    ax.set_ylabel('{}'.format(y_axis.upper()))

    title = ax.set_title('Interpolating vs Experimental data')
    plt.legend(loc='upper right')

    # Creating the Animation object
    line_ani = animation.FuncAnimation(fig, update_lines, range(261,1200),
                                            fargs=(tables, lines, title,
                                                cte_param, x_axis, y_axis),
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
    animation_plot_experimental_vs_interpolation(experimental_table, interpolated_table)
