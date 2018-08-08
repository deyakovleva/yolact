
import torch
import os
import math
from pathlib import Path

class MovingAverage():
    """ Keeps an average window of the specified number of items. """

    def __init__(self, max_window_size=1000):
        self.max_window_size = max_window_size
        self.window = []
        self.sum = 0

    def add(self, elem):
        """ Adds an element to the window, removing the earliest element if necessary. """
        if not math.isfinite(elem):
            print('Warning: Moving average ignored a value of %f' % elem)
            return
        
        self.window.append(elem)
        self.sum += elem

        if len(self.window) > self.max_window_size:
            self.sum -= self.window.pop(0)
    
    def append(self, elem):
        """ Same as add just more pythonic. """
        self.add(elem)

    def get_avg(self):
        """ Returns the average of the elements in the window. """
        return self.sum / max(len(self.window), 1)

    def __str__(self):
        return str(self.get_avg())
    
    def __repr__(self):
        return repr(self.get_avg())


class ProgressBar():
    """ A simple progress bar that just outputs a string. """

    def __init__(self, length, max_val):
        self.max_val = max_val
        self.length = length
        self.cur_val = 0
        
        self.cur_num_bars = -1
        self._update_str()

    def set_val(self, new_val):
        self.cur_val = new_val

        if self.cur_val > self.max_val:
            self.cur_val = self.max_val
        if self.cur_val < 0:
            self.cur_val = 0

        self._update_str()
    
    def is_finished(self):
        return self.cur_val == self.max_val

    def _update_str(self):
        num_bars = int(self.length * (self.cur_val / self.max_val))

        if num_bars != self.cur_num_bars:
            self.cur_num_bars = num_bars
            self.string = '█' * num_bars + '░' * (self.length - num_bars)
    
    def __repr__(self):
        return self.string
    
    def __str__(self):
        return self.string

def sanitize_coordinates(_x1, _x2, img_size, cast=True):
    """
    Sanitizes the input coordinates so that x1 < x2, x1 != x2, x1 >= 0, and x2 <= image_size.
    Also converts from relative to absolute coordinates and casts the results to long tensors.

    If cast is false, the result won't be cast to longs.
    """
    _x1 *= img_size
    _x2 *= img_size
    if cast:
        _x1 = _x1.long()
        _x2 = _x2.long()
    x1 = torch.min(_x1, _x2)
    x2 = torch.max(_x1, _x2)
    x1 = torch.clamp(x1-1, min=0)
    x2 = torch.clamp(x2+1, max=img_size)

    return x1, x2


def init_console():
    """
    Initialize the console to be able to use ANSI escape characters on Windows.
    """
    if os.name == 'nt':
        from colorama import init
        init()


class SavePath:
    """
    Why is this a class?
    Why do I have a class for creating and parsing save paths?
    What am I doing with my life?
    """

    def __init__(self, model_name:str, epoch:int, iteration:int):
        self.model_name = model_name
        self.epoch = epoch
        self.iteration = iteration

    def get_path(self, root:str=''):
        file_name = self.model_name + '_' + str(self.epoch) + '_' + str(self.iteration) + '.pth'
        return os.path.join(root, file_name)

    @staticmethod
    def from_str(path:str):
        file_name = os.path.basename(path)
        
        if file_name.endswith('.pth'):
            file_name = file_name[:-4]
        
        params = file_name.split('_')

        if file_name.endswith('interrupt'):
            params = params[:-1]
        
        model_name = '_'.join(params[:-2])
        epoch = params[-2]
        iteration = params[-1]
        
        return SavePath(model_name, int(epoch), int(iteration))

    @staticmethod
    def remove_interrupt(save_folder):
        for p in Path(save_folder).glob('*_interrupt.pth'):
            p.unlink()
    
    @staticmethod
    def get_interrupt(save_folder):
        for p in Path(save_folder).glob('*_interrupt.pth'): 
            return str(p)