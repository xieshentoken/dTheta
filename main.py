import os
import re
import sys
import time
from collections import OrderedDict
from itertools import permutations
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog, ttk

# Mac下使用这两行，Win下可以注释掉————————————————————
import matplotlib
matplotlib.use("TkAgg")
#——————————————————————————————————
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from func_GUI import *
from func_X import Xyy


def main():
    root = Tk()
    root.title("A Grain of Sand")
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
