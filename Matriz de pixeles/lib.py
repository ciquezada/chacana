import imageio
import numpy as np
import pandas as pd


def create_empty_matrix(y, x):
    im = []
    for i in range(y):
        im.append([])
        for j in range(x):
            im[i].append([])
    return im

def printProgressBar(iteration, total):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    prefix = 'Progress:'
    suffix = 'Complete'
    decimals = 1
    length = 50
    fill = '█'
    iteration += 1
    if not (100 * (iteration / float(total)) ) % 1 * 10 // 1:
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total))//1)
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
        # Print New Line on Complete
    if iteration >= total:
        print("")
