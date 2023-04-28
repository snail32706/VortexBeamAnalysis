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
此檔案利用 `tk.filedialog` load file.
再透過 `plt_SEM_imshow` 得到 "twoD_FFT", "scalebar"

`FFTUI` 主要用 tkinter 管理 UI, `FigureCanvasTkAgg`將`matplotlib`的功能時現在`tkUI`中顯示。
並透過鼠標互動，點出 「peak point」； simulate 橢圓形； 顯示「空間頻率」在圖上。

注意：
    `self.ellClass` 設定 "theta = 0"

'''

file_path = None
# file_path = f'/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP/18.tif'

def choose_path(master):

    global file_path
    file_path = tk.filedialog.askopenfilename(
        initialdir='/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP')
    # '/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP'
    return file_path

def file_name(file_path):

    # 移除副檔名
    file_name = file_path.split('/')[-1].split('.')[0]
    return f"{file_path.split('/')[-2]}_{file_name}"

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
   
class FFTUI:
    def __init__(self, master, array):

        self.master   = master
        self.master.title('Simulated ellipse from selecting points in FFT image')
        self.array    = array  # FFT array
        width, length = array.shape
        self.fftClass = FFTfunc.FFT(file_path)
        self.change_axis = self.fftClass.extent4FFT(width, length)
        self.ellClass = MathTool.Simulate_ellipse(center=(width//2, length//2), theta=0) # theta 設定為 0

        # 建立 matplotlib 圖形
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(file_name(file_path))
        self.ax.imshow(np.log(self.array), cmap='jet', vmin=-9, vmax=18, extent=self.change_axis, aspect=1)

        # 將 matplotlib 圖形嵌入 tkinter 視窗中
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 建立 Get Point 按鈕
        get_point_button = tk.Button(master=self.master, text='Get Point', command=self.get_point)
        get_point_button.pack(side=tk.LEFT)

        # 建立 Clear Point 按鈕
        clear_point_button = tk.Button(master=self.master, text='Clear all', command=self.clear_point)
        clear_point_button.pack(side=tk.LEFT)

        # 建立 simulate 按鈕
        simulate_ellipse_button = tk.Button(master=self.master, text='Simulate', command=self.plt_ab_on_fig)
        simulate_ellipse_button.pack(side=tk.LEFT)

        # 建立 save 按鈕
        save_fig_button = tk.Button(master=self.master, text='save', command=self.save_fig)
        save_fig_button.pack(side=tk.LEFT)

        # 將圖形與按鈕顯示於視窗中
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        get_point_button.pack(side=tk.LEFT)
        clear_point_button.pack(side=tk.LEFT)

        # 建立點選功能所需的空串列
        self.point_list = [[], []]

        # 建立 tkinter Scale 物件
        scale_label  = tk.Label(self.master, text="axis lim").pack(side=tk.LEFT)
        self.fftlim_scale = tk.Scale(master=self.master, from_=5, to=f'{width//2}', tickinterval= f'{200}', resolution=5, 
                                orient=tk.HORIZONTAL, length=300, command=self.update_fftlim)
        self.fftlim_scale.set(50)
        self.fftlim_scale.pack(side=tk.LEFT, fill=tk.X)

        # 設定圖形的鼠標點擊事件
        self.canvas.mpl_connect('button_press_event', self.on_click)

    def update_fftlim(self, value):
        self.fftlim = int(value)
        self.ax.set_xlim(-self.fftlim, self.fftlim)
        self.ax.set_ylim(-self.fftlim, self.fftlim)
        self.canvas.draw()

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

    def check_numbers_of_data(self):

        if len(self.point_list[0]) < 3:
            print('too little point!')
            return False

    def simulate_ellipse(self):
        
        if self.check_numbers_of_data() == False:
            return 

        width, length = self.array.shape
        a, b = self.ellClass.fit_ellipse(x=self.point_list[0], y=self.point_list[1])
        distance = self.ellClass.ellipse_distance_between_center(self.array, a, b)

        x, y = np.meshgrid(self.fftClass.FFTAxisCenterbeZero(width), self.fftClass.FFTAxisCenterbeZero(width))
        self.ax.contour(x, y, distance, levels=[0], colors='white')
        self.fig.canvas.draw()
        return int(round(a)), int(round(b))

    def plt_ab_on_fig(self):
        
        if self.check_numbers_of_data() == False:
            return 

        a_f, b_f = self.pixel_2_frequency()
        a_f, b_f = round(a_f,1), round(b_f,1)
        y_lim = self.fftlim_scale.get()
        self.ax.text(0, 0.9*y_lim, f'x:{a_f} y:{b_f}', fontsize=12, ha='center', va='center')
        self.fig.canvas.draw()

    def pixel_2_frequency(self):

        a, b = self.simulate_ellipse()
        width, length = self.array.shape
        scalebar = plt_SEM_imshow(file_path, center=(.45, .48), length=.399)[1]
        a_f = a * width * scalebar
        b_f = b * width * scalebar
        return a_f, b_f

    def save_fig(self):

        file_name = file_path.split('/')[-2] + '_' + file_path.split('/')[-1].split('.')[0]
        abs_file_folder = f"/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP_choose_point/"
        
        self.fig.savefig(abs_file_folder + f"FFT_{file_name}.png")
        
        if self.check_numbers_of_data() == False:
            a_f, b_f = None, None
        else:
            a_f, b_f = self.pixel_2_frequency()
        with open(abs_file_folder + 'fft_peak.txt', 'a') as f:
            f.write(f"{file_name}\t{a_f}\t{b_f}\n")

        self.master.destroy() # 關閉視窗


if __name__ == '__main__':
    
    root = tk.Tk()  # 建立 tkinter 視窗
    file_path = choose_path(master=root)
    array  = plt_SEM_imshow(file_path, center=(.45, .48), length=.399)[0]
    viewer = FFTUI(master=root, array=array)
    root.mainloop() # 啟動 tkinter 視窗

