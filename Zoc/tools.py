from itertools import count
from atpbar import atpbar, register_reporter, find_reporter, flush


class ProgressBar:

    def __init__(self, total):
        self.total = total

    def notify(self, iteration):
        self._printProgressBar(iteration)

    def _printProgressBar(self, iteration):
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
        if not (100 * (iteration / float(self.total)) ) % 1 * 10 // 1:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(self.total))//1)
            filledLength = int(length * iteration // self.total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
            # Print New Line on Complete
        if iteration >= self.total:
            print("")

class ProgressBarCounter(ProgressBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counter = count(0)

    def notify(self):
        self._printProgressBar(next(self.counter))

def PBarATP(gen, total=False, **kwargs):
    if not total:
        for it in atpbar(gen, **kwargs):
            yield it
    else:
        for i, it in zip(atpbar(range(total), **kwargs),gen):
            yield it
