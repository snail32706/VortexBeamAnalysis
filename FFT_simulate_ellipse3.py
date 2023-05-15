import numpy as np
# import matplotlib
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.ticker as plt_ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.optimize import curve_fit
import tkinter as tk
from tkinter import filedialog
import os
# from scipy.optimize import minimize

import FFT as plt_FFT
import simulateLIPSS as LIPSS
import find_SEM_scalebarPixel as Scalebarfunc
import MathTool

'''
此檔案利用 `tk.filedialog` load file.
再透過 `plt_SEM_imshow` 得到 "twoD_FFT", "scalebar"

`FFTUI` 主要用 tkinter 管理 UI, `FigureCanvasTkAgg`將`matplotlib`的功能時現在`tkUI`中顯示。
並透過鼠標互動，點出 「peak point」； simulate 橢圓形； 顯示「空間頻率」在圖上。

注意：
    1. `self.ellClass` 設定 "theta = 0"
    2. spatial frequency 倒數為週期
    3. save_fig() 中的路徑需要改

'''
###
def OM_imshow(file_path):
    file_name = os.path.basename(file_path)

    im   = Image.open(file_path)
    im_gray  = im.convert('L') # image to gray scale mole
    im_array = np.asarray(im_gray, dtype = np.float32)

    return im_array, file_name
###


def tk_choose_path(master):

    file_path = tk.filedialog.askopenfilename(
        initialdir='/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP')
    return file_path

def tk_choose_folder(master):
    folder_path = tk.filedialog.askdirectory(
        initialdir='/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/')
    return folder_path

def file_name(file_path):

    # 移除副檔名
    file_name = file_path.split('/')[-1].split('.')[0]
    return f"{file_path.split('/')[-2]}_{file_name}"

def read_folder_all_file(folder, keyword=None):
    '''
    folder : 將需要待匯入資料夾輸入。     <type> string
    keyword: folder 中篩選資料的關鍵字。 <type> string
    '''
    # folder, keyword = str(self.folder), str(self.keyword)
    file_list = sorted(os.listdir(folder)) #普通排序
    if keyword:
        file_list_with_keyword = list(filter(lambda x: keyword in x, file_list))
        return file_list_with_keyword
    else:
        return file_list

def list_filter(file_list, keyword):
    return list(filter(lambda x: keyword in x, file_list))




class FFTUI:
    def __init__(self, master):

        self.master   = master
        self.master.geometry('1500x1024')
        self.master.title('Simulated ellipse from selecting points in FFT image')

        # 參數
        self.folder_path   = None
        self.all_file_list = []
        self.file_path = None
        self.file_name = None
        # self.scalebar = 0.0


        # FFT image
        self.fig = Figure(figsize=(6, 6), dpi=100) # 建立 matplotlib 圖形
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("FFT image")

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master) # 將 matplotlib 圖形嵌入 tkinter 視窗中
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        ### --- 新增 file list 空間 --- ###
        self.entry_frame1 = tk.Frame(master, bg="#D3D3D3") #D3D3D3 灰色
        self.entry_frame1.place(relx=0.01, rely=0.05, relwidth=0.25, relheight=0.86)

        ### --- 新增 OM Image & scale bar 空間 --- ###
        self.entry_frame3 = tk.Frame(master, bg="#D3D3D3") #D3D3D3 灰色
        self.entry_frame3.place(relx=0.75, rely=0.05, relwidth=0.23, relheight=0.85)

        self.canvas_origin_image = tk.Canvas(self.entry_frame3)
        self.canvas_origin_image.place(x=10, y=20, width=320, height=330)

        # 顯示原始圖片
        self.fig_row = Figure(figsize=(6, 6), dpi=100) # 建立 row image 圖形
        self.ax_row = self.fig_row.add_subplot(111)

        self.canvas_row = FigureCanvasTkAgg(self.fig_row, master=self.canvas_origin_image)
        self.canvas_row.draw()
        self.canvas_row.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 建立 Clear Point 按鈕
        clear_point_button = tk.Button(master=self.master, text='Clear all', command=self.clear_point)
        clear_point_button.pack(side=tk.LEFT)

        # 建立 save 按鈕
        save_fig_button = tk.Button(master=self.master, text='save', command=self.save_fig)
        save_fig_button.pack(side=tk.LEFT)


    def clear_point(self):
        
        pass


    def display_row_image(self):
        
        try:
            array, file_name = OM_imshow(self.file_path)
            # print('成功')
        except:
            # print('失敗')
            return
        self.ax_row.clear()
        self.ax_row.set_title(file_name)
        self.ax_row.imshow(array, cmap='gray')#, vmin=0, vmax=255)#, extent=self.change_axis, aspect=1)
        self.ax_row.axis('off')
        self.fig_row.canvas.draw()

    def save_fig(self):

        file_name = file_path.split('/')[-2] + '_' + file_path.split('/')[-1].split('.')[0]
        # abs_file_folder = f"/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP_choose_point/"
        
        self.fig.savefig(abs_file_folder + f"FFT_{file_name}.png")
        
        if self.check_numbers_of_data() == False:
            a_f, b_f = None, None
        else:
            a_f, b_f = self.pixel_2_frequency()
        with open(abs_file_folder + 'fft_peak.txt', 'a') as f:
            f.write(f"{file_name}\t{a_f}\t{b_f}\n")

        self.master.destroy() # 關閉視窗


class FFTUI_add_file_list(FFTUI):

    def __init__(self, master):
        super().__init__(master)

        # 參數設定
        self.count = 0

        # 最上面
        self.choose_folder_button = tk.Button(master=self.entry_frame1, text='Choose Folder', command=self.choose_folder)
        self.choose_folder_button.place(relx=0.01, rely=0.05, relwidth=0.3, relheight=0.07)
        
        extension_label = tk.Label(master=self.entry_frame1, text='extension:', bg='white', fg='black', font=('Arial', 14))
        extension_label.place(relx=0.33, rely=0.052)
        keyword_label = tk.Label(master=self.entry_frame1,   text='keyword  :', bg='white', fg='black', font=('Arial', 14))
        keyword_label.place(relx=0.33, rely=0.091)
        
        self.extension_entry = tk.Entry(master=self.entry_frame1, bg='black', fg='white')
        self.extension_entry.place(relx=0.55, rely=0.05, relwidth=0.43, relheight=0.032)
        self.keyword_entry = tk.Entry(master=self.entry_frame1, bg='black', fg='white')
        self.keyword_entry.place(relx=0.55, rely=0.09, relwidth=0.43, relheight=0.032)
        # reset button
        self.keyword_reset_button = tk.Button(master=self.entry_frame1, text='Reset', command=self.folder_reset, fg='red', font=('Arial', 8))
        self.keyword_reset_button.place(relx=0.83, rely=0.12, relwidth=0.1, relheight=0.03)

        self.folder_path_view = tk.Label(master=self.entry_frame1,   text='', bg='yellow', fg='black', font=('Arial', 14))
        self.folder_path_view.place(relx=0.04, rely=0.15, relwidth=0.92, relheight=0.04)

        # 顯示「檔案」區域
        self.text_widget = tk.Frame(self.entry_frame1) # 新增空間
        self.text_widget.place(x=10, y=150, width=350, height=560)
        # 設置
        self.listbox = tk.Listbox(self.text_widget)
        self.listbox.pack(side = tk.LEFT, fill = tk.BOTH)
        
        self.scrollbar = tk.Scrollbar(self.text_widget)# Creating a Scrollbar(滾動條)
        self.scrollbar.pack(side = tk.RIGHT, fill = tk.BOTH)

        # self.file_list_reset()

        # 將列錶框附加到滾動條，因為我們需要有一個垂直的滾動
        # 我們使用 yscroll 命令
        self.listbox.config(yscrollcommand = self.scrollbar.set)
          
        # 設置滾動條命令參數到 listbox.yview 方法它的 yview 
        # 因為我們需要一個垂直視圖
        self.scrollbar.config(command = self.listbox.yview)

        # 新增選擇檔案箭頭
        self.arrow_left_image = Image.open('arrow_left.png') 
        self.arrow_left_image = self.arrow_left_image.resize((27, 27), Image.LANCZOS)  # 調整 width 和 height 為所需值
        self.arrow_left_image = ImageTk.PhotoImage(self.arrow_left_image)                # 載入圖片並轉換成 PhotoImage
        self.arrow_left_button = tk.Button(master=self.entry_frame1, image=self.arrow_left_image, bg='lightgray', command=self.left_image)
        self.arrow_left_button.pack(side=tk.LEFT, anchor=tk.SW, padx=10, pady=10)
        self.master.bind('<Left>', lambda event: self.left_image()) # 使用鍵盤 觸發相同事件

        self.arrow_right_image = Image.open('arrow_right.png') 
        self.arrow_right_image = self.arrow_right_image.resize((27, 27), Image.LANCZOS)  # 調整 width 和 height 為所需值
        self.arrow_right_image = ImageTk.PhotoImage(self.arrow_right_image)                # 載入圖片並轉換成 PhotoImage
        self.arrow_right_button = tk.Button(master=self.entry_frame1, image=self.arrow_right_image, bg='lightgray', command=self.right_image)
        self.arrow_right_button.pack(side=tk.LEFT, anchor=tk.SW, padx=20, pady=10)
        self.master.bind('<Right>', lambda event: self.right_image()) # 使用鍵盤 觸發相同事件

    def choose_folder(self):

        self.all_file_list.clear() # clear list
        self.folder_path   = tk_choose_folder(master=root)
        self.folder_reset()

    def folder_reset(self):

        self.listbox.delete(0, tk.END) # 清空 file lise 列表
        # 讀檔
        extension, keyword = self.extension_entry.get(), self.keyword_entry.get()
        
        self.all_file_list = read_folder_all_file(folder=self.folder_path, keyword=keyword)
        if extension is not None:
            self.all_file_list = list_filter(self.all_file_list, extension)

        # 顯示資料夾位置
        folder_name = os.path.basename(self.folder_path)
        parent_dir = os.path.dirname(self.folder_path)
        folder_info = os.path.join(os.path.basename(parent_dir), folder_name)
        self.folder_path_view = tk.Label(master=self.entry_frame1, text=folder_info, bg='yellow', fg='black', font=('Arial', 14))
        self.folder_path_view.place(relx=0.04, rely=0.15, relwidth=0.92, relheight=0.04)
        self.file_list_reset()

    def file_list_reset(self):

        self.count = 0

        self.listbox.delete(0, tk.END) # clear
        # 逐行顯示 file list
        for file_i in self.all_file_list:
            self.listbox.insert(tk.END, file_i)
        if len(self.all_file_list) == 0:
            return

        self.listbox.selection_set(self.count)
        self.file_name = self.all_file_list[self.count]                    # 設置 count 為選取檔案
        self.file_path = os.path.join(self.folder_path, self.file_name)    # 設置 count 為選取 file_path
        self.display_row_image() # 畫出原始圖

    def right_image(self):

        if not self.count < len(self.all_file_list):
            return
        self.listbox.selection_clear(self.count, tk.END) # clear 原本的
        self.count += 1
        self.listbox.selection_set(self.count) # 顯示下一個

        self.file_name = self.all_file_list[self.count]                    # 設置 count 為選取檔案
        self.file_path = os.path.join(self.folder_path, self.file_name)    # 設置 count 為選取 file_path
        self.display_row_image() # 畫出原始圖

    def left_image(self):
        
        if self.count  == 0:
            return
        self.listbox.selection_clear(self.count, tk.END) # clear 原本的
        self.count -= 1
        self.listbox.selection_set(self.count)
        self.listbox.selection_set(self.count) # 顯示下一個

        self.file_name = self.all_file_list[self.count]                    # 設置 count 為選取檔案
        self.file_path = os.path.join(self.folder_path, self.file_name)    # 設置 count 為選取 file_path
        self.display_row_image()


class FFTUI_add_Scalebar(FFTUI_add_file_list):

    def __init__(self, master):
        super().__init__(master)

        
        # 實際長度
        self.scalebar_length_entry = tk.Entry(master=self.entry_frame3, bg='black', fg='white')
        self.scalebar_length_entry.place(relx=0.05, rely=0.5, relwidth=0.15, relheight=0.032)
        unit_label = tk.Label(master=self.entry_frame3,   text='um', bg='white', fg='black', font=('Arial', 14))
        unit_label.place(relx=0.22, rely=0.5)
        # scarl bar pixle value
        self.scalebar_pixel_entry = tk.Entry(master=self.entry_frame3, bg='black', fg='white')
        self.scalebar_pixel_entry.place(relx=0.05, rely=0.55, relwidth=0.2, relheight=0.032)
        pixel_label = tk.Label(master=self.entry_frame3,   text='pixel', bg='white', fg='black', font=('Arial', 14))
        pixel_label.place(relx=0.27, rely=0.55)
        # reset scale bar
        self.scalebar_reset_button = tk.Button(master=self.entry_frame3, text='Reset', command=self.caculate_scalebar, fg='red', font=('Arial', 8))
        self.scalebar_reset_button.place(relx=0.83, rely=0.51, relwidth=0.1, relheight=0.03)

        self.scalebar_lalbel = tk.Label(master=self.entry_frame3,  text='', bg='white', fg='black', font=('Arial', 14))
        self.scalebar_lalbel.place(relx=0.2, rely=0.6)

    def caculate_scalebar(self):

        length, pixel = self.scalebar_length_entry.get(), self.scalebar_pixel_entry.get()
        self.scalebar = float(length) / float(pixel)
        word = f"scale bar: {np.round(self.scalebar, 4)} um per pixel"

        self.scalebar_lalbel = tk.Label(master=self.entry_frame3,  text=word, bg='white', fg='black', font=('Arial', 14))
        self.scalebar_lalbel.place(relx=0.05, rely=0.6)





if __name__ == '__main__':
    
    root = tk.Tk()  # 建立 tkinter 視窗
    # file_path = tk_choose_path(master=root)
    file_path = '/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413_SEM/AP/18.tif'
    # array  = plt_SEM_imshow(file_path, center=(.45, .48), length=.399)[0]
    viewer = FFTUI_add_Scalebar(master=root)
    root.mainloop() # 啟動 tkinter 視窗

