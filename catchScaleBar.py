import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as plt_ticker
from matplotlib.colors import LogNorm
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
# import cv2 as cv
from PIL import Image
# from scipy.misc import electrocardiogram
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import heapq
# import seaborn as sns

def find_SEM_scalebarPixel(scalebar_array):
	
	'''
	切開 SEM 找出 scalebar 長度為多少個 pixel。
	'''
	
    scalebar_left, scalebar_right = None, None 
    for idx, val in enumerate(scalebar_array):
        if scalebar_array[idx] > 200 and scalebar_array[idx +3] > 200:
            if scalebar_left is None:
                scalebar_left = idx
        elif scalebar_array[idx] > 200 and scalebar_array[idx +1] < 200:
            if scalebar_right is None:
                scalebar_right = idx
            elif scalebar_right is not None:
                break
    return scalebar_right - scalebar_left