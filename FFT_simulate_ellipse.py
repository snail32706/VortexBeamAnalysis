import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as plt_ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import heapq
import tkinter as tk
import os
from scipy.optimize import minimize

import FFT as FFTfunc
import simulateLIPSS as LIPSS
import find_SEM_scalebarPixel as Scalebarfunc
import MathTool

'''
此檔案利用 load 指定 file.
透過 `plt_SEM_imshow` 得到 "twoD_FFT", "scalebar"

`ArrayViewer` 主要是用 tkinter.
透過鼠標互動，點出 「peak point」； simulate 橢圓形。

注意：
    `self.ellClass` 設定 "theta = 0"

'''



file = f'/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP/18.tif'

def plt_SEM_imshow(file_path, center, length):
    file_name = file_path.split('/')[-2] + '/' + file_path.split('/')[-1]
    scalebarClass = Scalebarfunc.Find_SEM_scalebarPixel(file_path, scalebar_width_um=1)
    scalebar = scalebarClass.caculate_scaleBar()

    fftClass = FFTfunc.FFT(file_path)
    im_array = fftClass.image2Array()
    # 裁減 array 
    cropped_array = fftClass.arrayCutSquare(array=im_array, center=center, length=length)
    # FFT
    twoD_FFT = fftClass.array2FFT(cropped_array)
    return twoD_FFT, scalebar
   
class ArrayViewer:
    def __init__(self, array):

        self.array = array  # FFT array
        width, length = array.shape

        self.fftClass = FFTfunc.FFT(file)
        self.change_axis = self.fftClass.extent4FFT(width, length)
        
        self.ellClass = MathTool.Simulate_ellipse(center=(width//2, length//2), theta=0) # theta 設定為 0
        
        # 建立 tkinter 視窗
        self.root = tk.Tk()
        self.root.title('Array Viewer')

        # 建立 matplotlib 圖形
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.imshow(np.log(self.array), cmap='jet', vmin=-9, vmax=18, extent=self.change_axis, aspect=1)
        self.fftlim = 70
        self.ax.set_xlim(-self.fftlim, self.fftlim)
        self.ax.set_ylim(-self.fftlim, self.fftlim)

        # 將 matplotlib 圖形嵌入 tkinter 視窗中
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 建立點選功能所需的空串列
        self.point_list = [[], []]

        # 建立 Get Point 按鈕
        get_point_button = tk.Button(master=self.root, text='Get Point', command=self.get_point)
        get_point_button.pack(side=tk.LEFT)

        # 建立 Clear Point 按鈕
        clear_point_button = tk.Button(master=self.root, text='Clear all', command=self.clear_point)
        clear_point_button.pack(side=tk.LEFT)

        # 建立 simulate 按鈕
        simulate_ellipse_button = tk.Button(master=self.root, text='Simulate', command=self.simulate_ellipse)
        simulate_ellipse_button.pack(side=tk.LEFT)

        # 將圖形與按鈕顯示於視窗中
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        get_point_button.pack(side=tk.LEFT)
        clear_point_button.pack(side=tk.LEFT)

        # 設定圖形的鼠標點擊事件
        self.canvas.mpl_connect('button_press_event', self.on_click)

        # 啟動 tkinter 視窗
        self.root.mainloop()

    def on_click(self, event):
        if event.inaxes is not None:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            self.point_list[0].append(x)
            self.point_list[1].append(y)
            self.ax.scatter(x, y, s=10, c='g')
            self.fig.canvas.draw()

    def get_point(self):
        print(self.point_list)
        return self.point_list

    def clear_point(self):
        self.point_list[0].clear()
        self.point_list[1].clear()
        self.ax.clear()
        self.ax.imshow(np.log(self.array), cmap='jet', vmin=-9, vmax=18, extent=self.change_axis, aspect=1)
        self.ax.set_xlim(-self.fftlim, self.fftlim)
        self.ax.set_ylim(-self.fftlim, self.fftlim)
        self.fig.canvas.draw()

    def simulate_ellipse(self):
        
        if len(self.point_list[0]) < 3:
            print('too little point!')
            return 

        width, length = self.array.shape
        a, b = self.ellClass.fit_ellipse(x=self.point_list[0], y=self.point_list[1])
        distance = self.ellClass.ellipse_distance_between_center(self.array, a, b)

        x, y = np.meshgrid(self.fftClass.FFTAxisCenterbeZero(width), self.fftClass.FFTAxisCenterbeZero(width))
        self.ax.contour(x, y, distance, levels=[0], colors='white')
        self.fig.canvas.draw()
        print(a, b)

viewer = ArrayViewer(plt_SEM_imshow(file, center=(.45, .48), length=.399)[0])



