import os
import re
import sys
import time
from collections import OrderedDict
from itertools import permutations
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog, ttk

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from func_GUI import *
from func_X import Xyy


def main():
    root = Tk()
    root.title("A little App")
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
