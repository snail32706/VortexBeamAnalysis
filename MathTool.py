import numpy as np
from scipy.signal import find_peaks
from scipy.optimize import curve_fit


class Math():

    def __init__(self):
        pass

    def noice(self, row, col, randomRange):
        '''
        產生一個 row * col 的隨機數陣列，每個元素的值在 -randomRange ~ randomRange 之間
        '''
        # return (1/A)*np.random.randint(-A*randomRange, A*randomRange)
        return np.random.rand(row, col) * 2*randomRange - randomRange

    def simulateArray(self, N, simulateRange):
        '''
        simulate an array. 
        array range:  2*simulateRange * 2*simulateRange
        array size : N * N
        
        並且以 r 替換 x,y。
        '''
        N = 1000
        simulateRange = 100
        x = np.linspace(-simulateRange, simulateRange, N)
        y = np.linspace(-simulateRange, simulateRange, N)
        XX, YY = np.meshgrid(x, y)
        r = np.sqrt(XX**2 + YY**2)
        return x, r, N, simulateRange

    def findSecondPeak(self, data, selectPeak):
        '''
        selectPeak: 第幾根 peak.
        因為 FFT 左右對稱，因此找第 1,3,5,... 的值。
        '''
        selectPeak  = int(selectPeak)
        peak_pos, _ = find_peaks(data)
        peak_values = data[peak_pos]
        n = 2*selectPeak - 1
        nst_largest  = heapq.nlargest(n, peak_values)[-1]
        nst_peak_pos = peak_pos[np.where(peak_values == nst_largest)[0][0]]
        return nst_largest

    def findBackage(self, array):
        '''
        用 histogram 找出背景最多的值分佈位置
        hist: 橫軸（分佈值）
        bin : 縱軸（分佈數量）
        '''
        hist, bins = np.histogram(array, bins=30)  
        max_idx    = np.argmax(hist)
        return bins[max_idx]
