import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plt_ticker
import pandas as pd
from PIL import Image
from scipy.signal import find_peaks
# from scipy.misc import electrocardiogram
# import cv2 as cv
# import seaborn as sns

class FFT():
    
    '''
    first:
        input photo.
    second:
        get: cut down image size (x, y) and scalebar.
    third:
        caculate real image size and real FFT inverse-space.
    '''
    
    def __init__(self, file_path):
        self.file_path = file_path
        # self.im_array  = self.imageToArray()

    def image2Array(self):
        global file_path

        file = str(self.file_path)
        im   = Image.open(file)
        im_gray  = im.convert('L') # image to gray scale mole
        im_array = np.asarray(im_gray, dtype = np.float32)
        return im_array

    def array2FFT(self, array):

        twoD_FFT = np.fft.fft2(array)
        twoD_FFT = np.fft.fftshift(twoD_FFT)
        return np.abs(twoD_FFT)
    
    def arrayCut(self, array, top, bottom, left, right):
        '''
        input array & cut top, bottom, left, right.
        then all paremeter range be 0 ~ 1.
        And cut image shape must be even.
        '''

        length, width = array.shape
        top_, bottom_, left_, right_ = int(top*length), int(bottom*length), int(left*width), int(right*width), 
        if (bottom_ - top_) % 2 != 0:  # 如果不是偶数
            bottom += 1              # 使其变为偶数
        if (right_ - left_) % 2 != 0:  
            right_ += 1 
        return array[top_: bottom_, left_: right_]

    def arrayCutSquare(self, array, center, length):
        '''
        input array, center, length.

        paremeter:
            center: (0 ~ 1, 0 ~ 1)    # --- center type must be a tuple --- #
            length: 0 ~ 1.

        And cut image shape must be even & square.
        '''
        if not isinstance(center, tuple) or len(center) != 2:
            print('Argument "center" must be of type tuple. ex: (0.5, 0.5)')
        elif not isinstance(length, float) or length <= 0 or length >= 0.5:
            print('Argument "length" must be a float number and between 0 to 0.5')

        else:
            height, width = array.shape
            
            # 找到正方形邊長
            side_length = min(width, height)

            # 根據 length 參數縮放正方形大小
            scale = length / 0.5
            square_size = int(side_length * scale)

            # 找到正方形左上角的位置
            center_x = int(center[1] * width)
            center_y = int(center[0] * height)
            square_x = center_x - square_size // 2
            square_y = center_y - square_size // 2
            
            # 將 square_size 設定為偶數
            if square_size % 2 != 0:
                square_size -= 1
        
            # 裁切成正方形
            return array[square_y:square_y+square_size, square_x:square_x+square_size]

    def extent(self, pixel_length, pixel_width):
        '''
        Input : 180, 
        Output: 90, 89
        '''
        return -pixel_width/2, pixel_width/2 -1, -pixel_length/2, pixel_length/2 -1

    def extent4FFT(self, pixel_length, pixel_width):
        '''
        Input : 180, 
        Output: 90, 89
        '''
        return -pixel_width/2, pixel_width/2 -1, pixel_length/2-1, -pixel_length/2 

    def realSpaceAxis(self, array, scalebar):
        '''
        Input : image array
        Output: 長,寬（y,x）實際比例
        '''
        length, width = array.shape
        y = np.linspace(0, length-1, length) * scalebar
        x = np.linspace(0, width-1, width) * scalebar
        return y, x

    
    def realSpace_pixelToWavenumber(self, num_of_realSpaceShape, scalebar):
        '''
        input  : 500
        create array,
                 [0, 1, ..., 499]
        return : scalebar*[0, 1, ..., 499]
        '''
        array = np.linspace(0, num_of_realSpaceShape-1, num_of_realSpaceShape)
        return array * scalebar
        

    def FFTAxisCenterbeZero(self, num_of_realSpaceShape):
        '''
        In : 720
        Out: [-360, -379, ..., 379]
                float type
        '''
        return np.linspace(-num_of_realSpaceShape/2, num_of_realSpaceShape/2 -1, num_of_realSpaceShape)

    def get_image_scalebar(self, image):
        '''
        imput type 尚未決定
        return: um/pixel
        '''
        pass

    def pixel_2_InverseSpaceAxis(self, num_of_realSpaceShape, scale_bar):
        '''
        caculate real-space and inverse-space axis
        input 'pixel of real-space' and 'scale bar'.
        '''
        pixel  = num_of_realSpaceShape
        width = pixel * scale_bar
        pixel_inverseSpace = self.FFTAxisCenterbeZero(pixel)
        inverseSpace_axis  = pixel_inverseSpace / width
        return np.around(inverseSpace_axis, 2) # 取小數點

    def cut_45degree(self, array, scalebar=None):
        '''
        Input: array
        對 array 45度 取出值，並輸出 x,y 1D array.
        '''
        a = []
        row, col = array.shape
        center_x, center_y = row//2, col//2     # int
        for i in range(row):
            for j in range(col):
                if i - center_x == j - center_y:
                    a.append(array[i][j])
        '''
        x axis 乘根號 2.
        '''
        if scalebar is None:
            if col > row:
                return self.FFTAxisCenterbeZero(row)*np.sqrt(2), np.array(a)
            else:
                return self.FFTAxisCenterbeZero(col)*np.sqrt(2), np.array(a)
        else:
            if col > row:
                return self.pixel_to_InverseSpaceAxis(row, scalebar)*np.sqrt(2), np.array(a)
            else:
                return self.pixel_to_InverseSpaceAxis(col, scalebar)*np.sqrt(2), np.array(a)










        

        
    