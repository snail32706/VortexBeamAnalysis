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

import FFT as FFTfunc
# import simulateLIPSS as LIPSS
# import find_SEM_scalebarPixel as Scalebarfunc
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
        self.array = None


        # FFT image
        self.fig_FFT = Figure(figsize=(6, 6), dpi=100) # 建立 matplotlib 圖形
        self.ax_FFT = self.fig_FFT.add_subplot(111)
        self.ax_FFT.set_title("FFT image")

        self.canvas = FigureCanvasTkAgg(self.fig_FFT, master=self.master) # 將 matplotlib 圖形嵌入 tkinter 視窗中
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

        ##### ------- 最底下的按鈕 ------- #####
        # 建立 Get Point 按鈕
        get_point_button = tk.Button(master=self.master, text='Get Point', command=self.get_point)
        get_point_button.pack(side=tk.LEFT)

        # 建立 Clear Point 按鈕
        clear_point_button = tk.Button(master=self.master, text='Clear point', command=self.clear_point)
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
        ##### ---------- end ---------- #####

        # 設定圖形的鼠標點擊事件
        self.canvas.mpl_connect('button_press_event', self.on_click)


    def update_fftlim(self, value):
        # print(value)
        self.fftlim = int(value)
        self.ax_FFT.set_xlim(-self.fftlim, self.fftlim)
        self.ax_FFT.set_ylim(-self.fftlim, self.fftlim)
        self.canvas.draw()

    def on_click(self, event):
        if event.inaxes is not None:
            x, y = int(round(event.xdata)), int(round(event.ydata))
            self.point_list[0].append(x)
            self.point_list[1].append(y)
            self.ax_FFT.scatter(x, y, s=10, c='g')
            self.fig_FFT.canvas.draw()

    def get_point(self):
        print(self.point_list)
        return self.point_list

    def clear_point(self):
        
        self.point_list[0].clear()
        self.point_list[1].clear()
        self.ax_FFT.clear()
        try:
            self.array, file_name = OM_imshow(self.file_path)
        except:
            print('失敗')
            return
        print('1')
        self.ax_FFT.imshow(np.log(self.array), cmap='jet', vmin=-9, vmax=18, extent=self.change_axis, aspect=1)
        self.ax_FFT.set_xlim(-self.fftlim, self.fftlim)
        print('1')
        self.ax_FFT.set_ylim(-self.fftlim, self.fftlim)
        self.fig_FFT.canvas.draw()
        print('1')

    def display_row_image(self):
        
        try:
            self.array, file_name = OM_imshow(self.file_path)
            # print('成功')
        except:
            # print('失敗')
            return
        self.ax_row.clear()
        self.ax_row.set_title(file_name)
        self.ax_row.imshow(self.array, cmap='gray')#, vmin=0, vmax=255)#, extent=self.change_axis, aspect=1)
        self.ax_row.axis('off')
        self.fig_row.canvas.draw()

        self.display_FFT()

    def plt_ab_on_fig(self):
        # 後面會重新設定。
        pass

    def display_FFT(self):
        # 後面會重新設定。
        pass

    def save_fig(self):
        pass

        # file_name = file_path.split('/')[-2] + '_' + file_path.split('/')[-1].split('.')[0]
        # # abs_file_folder = f"/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP_choose_point/"
        
        # self.fig.savefig(abs_file_folder + f"FFT_{file_name}.png")
        
        # if self.check_numbers_of_data() == False:
        #     a_f, b_f = None, None
        # else:
        #     a_f, b_f = self.pixel_2_frequency()
        # with open(abs_file_folder + 'fft_peak.txt', 'a') as f:
        #     f.write(f"{file_name}\t{a_f}\t{b_f}\n")



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
        self.point_list[0].clear()
        self.point_list[1].clear()

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

        self.point_list[0].clear()
        self.point_list[1].clear()

        if not self.count < len(self.all_file_list):
            return
        self.listbox.selection_clear(self.count, tk.END) # clear 原本的
        self.count += 1
        self.listbox.selection_set(self.count) # 顯示下一個

        self.file_name = self.all_file_list[self.count]                    # 設置 count 為選取檔案
        self.file_path = os.path.join(self.folder_path, self.file_name)    # 設置 count 為選取 file_path
        self.display_row_image() # 畫出原始圖

    def left_image(self):
        
        self.point_list[0].clear()
        self.point_list[1].clear()

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
        self.scalebar_length_entry.insert(tk.END, "10")  # 插入預設值
        self.scalebar_length_entry.place(relx=0.05, rely=0.5, relwidth=0.15, relheight=0.032)
        unit_label = tk.Label(master=self.entry_frame3,   text='um', bg='white', fg='black', font=('Arial', 14))
        unit_label.place(relx=0.22, rely=0.5)
        # scarl bar pixle value
        self.scalebar_pixel_entry = tk.Entry(master=self.entry_frame3, bg='black', fg='white')
        self.scalebar_pixel_entry.insert(tk.END, "329")  # 插入預設值
        self.scalebar_pixel_entry.place(relx=0.05, rely=0.55, relwidth=0.2, relheight=0.032)
        pixel_label = tk.Label(master=self.entry_frame3,   text='pixel', bg='white', fg='black', font=('Arial', 14))
        pixel_label.place(relx=0.27, rely=0.55)
        # reset scale bar
        self.scalebar_reset_button = tk.Button(master=self.entry_frame3, text='Reset', command=self.caculate_scalebar, fg='red', font=('Arial', 8))
        self.scalebar_reset_button.place(relx=0.83, rely=0.51, relwidth=0.1, relheight=0.03)

        self.scalebar_lalbel = tk.Label(master=self.entry_frame3,  text='', bg='white', fg='black', font=('Arial', 14))
        self.scalebar_lalbel.place(relx=0.2, rely=0.6)

    def check_input(self):
        try:
            float(self.scalebar_length_entry.get())
            float(self.scalebar_pixel_entry.get())
        except:
            tk.messagebox.showinfo('Error', 'Input scalebar information')

    def caculate_scalebar(self):

        self.check_input() # 檢查 scalebar 有沒有輸入資訊
        length, pixel = self.scalebar_length_entry.get(), self.scalebar_pixel_entry.get()
        try:
            self.scalebar = float(length) / float(pixel)
        except:
            return
        word = f"scale bar: {np.round(self.scalebar, 4)} um per pixel"

        self.scalebar_lalbel = tk.Label(master=self.entry_frame3,  text=word, bg='white', fg='black', font=('Arial', 14))
        self.scalebar_lalbel.place(relx=0.05, rely=0.6)


class UI_add_FFT_image(FFTUI_add_Scalebar):


    def __init__(self, master):
        super().__init__(master)

        # 測試用的
        self.folder_path = '/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230508_OM/AP_1750_n3'
        self.folder_reset() # 測試用的

        self.fftClass    = None
        self.change_axis = None
        self.twoD_FFT    = None
        self.ellClass    = None



        # 建立 tkinter Scale 物件
        scale_label  = tk.Label(self.master, text="axis lim").pack(side=tk.LEFT)
        self.fftlim_scale = tk.Scale(master=self.master, from_=5, to=f'{500//2}', tickinterval= f'{200}', resolution=5, 
                                orient=tk.HORIZONTAL, length=300, command=self.update_fftlim)
        self.fftlim_scale.set(70)
        self.fftlim_scale.pack(side=tk.LEFT, fill=tk.X)


        
        
    def setup(self):

        '''
        1. caculate_scalebar
            若沒通過，會跳出 視窗說明，
            通過，則得到 `self.scalebar`。
        2. 設定 class
            因為 file_path 必須為 array 才可以畫圖。
            display FFT 與 image 一起觸發。
            之前有設定 try: OM_show。
            
            現在要再次設定 OM_show 突過才會 設定 <class>。

        '''
        self.caculate_scalebar() # 檢查 `scalebar entry` 有沒有輸入資訊，順便取得 `self.scalebar`
        
        try:
            self.array, file_name = OM_imshow(self.file_path)
        except:
            file_name = os.path.basename(self.file_path)
            print("{file_name} isn't an array!")
            return

        self.fftClass = FFTfunc.FFT(self.file_path)
        self.width, self.length = self.array.shape
        self.change_axis = self.fftClass.extent4FFT(self.width, self.length)
        self.twoD_FFT = self.fftClass.array2FFT(self.array)
        self.ellClass = MathTool.Simulate_ellipse(center=(self.width//2, self.length//2), theta=0) # theta 設定為 0

        self.fftlim_scale.destroy()  # 刪除舊的 tk.Scale
        self.fftlim_scale = tk.Scale(master=self.master, from_=5, to=f'{self.width//2}', tickinterval= f'{200}', resolution=5, 
                                orient=tk.HORIZONTAL, length=300, command=self.update_fftlim)
        self.fftlim_scale.set(self.fftlim)
        self.fftlim_scale.pack(side=tk.LEFT, fill=tk.X)

    def display_FFT(self):
        
        self.setup() # 預先設定

        self.ax_FFT.clear()
        file_name = os.path.basename(self.file_path)
        self.ax_FFT.set_title(file_name)
        
        if self.twoD_FFT is not None:
            self.ax_FFT.imshow(np.log(self.twoD_FFT), cmap='jet', vmin=-9, vmax=18, extent=self.change_axis, aspect=1)
        self.fig_FFT.canvas.draw()

    def check_numbers_of_data(self):

        if len(self.point_list[0]) < 3:
            tk.messagebox.showinfo('Too few points')
            print('too little point!')
            return False

    def simulate_ellipse(self):
        
        if self.check_numbers_of_data() == False:
            return 

        width, length = self.array.shape
        a, b = self.ellClass.fit_ellipse(x=self.point_list[0], y=self.point_list[1])
        distance = self.ellClass.ellipse_distance_between_center(self.array, a, b)

        x, y = np.meshgrid(self.fftClass.FFTAxisCenterbeZero(width), self.fftClass.FFTAxisCenterbeZero(width))
        self.ax_FFT.contour(x, y, distance, levels=[0], colors='white')
        self.fig_FFT.canvas.draw()
        return int(round(a)), int(round(b))

    def plt_ab_on_fig(self):
        
        if self.check_numbers_of_data() == False:
            return 

        a_f, b_f = self.pixel_2_frequency()
        a_f, b_f = round(a_f,1), round(b_f,1)
        y_lim = self.fftlim_scale.get()
        self.ax_FFT.text(0, 0.9*y_lim, f'x:{a_f}um-1 y:{b_f}um-1', fontsize=12, ha='center', va='center')
        self.fig_FFT.canvas.draw()

    def pixel_2_frequency(self):

        a, b = self.simulate_ellipse()
        print(f'長軸: {a} pixel, 短軸：{b} pixel')
        width, length = self.array.shape
        a_f = a / (width * self.scalebar)
        b_f = b / (width * self.scalebar)
        print(f'長軸: {1/a_f} um, 短軸：{1/b_f}m')
        return a_f, b_f


if __name__ == '__main__':
    
    root = tk.Tk()  # 建立 tkinter 視窗
    # file_path = tk_choose_path(master=root)
    # file_path = '/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413_SEM/AP/18.tif'
    viewer = UI_add_FFT_image(master=root)
    root.mainloop() # 啟動 tkinter 視窗

