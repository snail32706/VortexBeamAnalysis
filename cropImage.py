from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import os

'''
問題：
    choose folder 時`load file button`被繼承過去，希望可以不被繼承。
- Answer： 辦不到

目標：
    更改存擋方式。

    - 現在存擋的檔名使用的方式：
        rigion named : row3_324324.jpg
        save file name: crop_ro3_1.jpg
    - 使用方法：
        count = 1.
        saving success => count += 1
        when count > 



注意：
    all_file_list 由檔案名組成，故缺少了絕對路徑

'''

# file_path = None
folder = '/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230508_OM'

def tk_choose_path(master):

    file_path = filedialog.askopenfilename(
        initialdir=folder)
    return file_path

def tk_choose_folder(master):

    folder_path = filedialog.askdirectory(
        initialdir=folder)
    return folder_path

def read_folder_all_file(folder, keyword):
    '''
    folder : 將需要待匯入資料夾輸入。     <type> string
    keyword: folder 中篩選資料的關鍵字。 <type> string
    '''
    folder, keyword = str(folder), str(keyword)
    file_list = sorted(os.listdir(folder)) #普通排序
    all_file_with_keyword = list(filter(lambda x: keyword in x, file_list)) 
    return all_file_with_keyword

def file_name(file_path):

    # 移除副檔名
    file_name = file_path.split('/')[-1].split('.')[0]
    return f"{file_path.split('/')[-2]}/{file_name}"



class CropImageApp:
    def __init__(self, master, file_path):
        
        self.file_path = file_path
        self.master = master
        self.master.geometry('1440x1024')
        self.master.title('Crop Image')

        # 建立 matplotlib 圖形
        self.fig = Figure(figsize=(6, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.image_set_up()

        # 將 matplotlib 圖形嵌入 tkinter 視窗中
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # 建立 load file 按鈕
        self.load_file_button = tk.Button(master=self.master, text='Load File', command=self.__load_file)
        self.load_file_button.pack(side=tk.LEFT)

        # 建立 Crop 按鈕
        self.get_point_button = tk.Button(master=self.master, text='Crop', command=self.crop)
        self.get_point_button.pack(side=tk.LEFT)

        # 建立 Clear Point 按鈕
        self.clear_point_button = tk.Button(master=self.master, text='Clear', command=self.clear)
        self.clear_point_button.pack(side=tk.LEFT)

        # 建立 save 按鈕
        self.save_fig_button = tk.Button(master=self.master, text='save', command=self.save_fig)
        self.save_fig_button.pack(side=tk.LEFT)
        self.master.bind('s', lambda event: self.save_fig()) # 使用鍵盤 觸發相同事件

        # 建立 tkinter Scale 物件
        scale_label  = tk.Label(self.master, text="crop image pixel:").pack(side=tk.LEFT)
        self.pixel_scale = tk.Scale(master=self.master, from_=100, to=f'{self.length}', tickinterval= f'{200}', resolution=20, 
                                orient=tk.HORIZONTAL, length=300, command=self.update_crop_square_pixel)
        self.pixel_scale.set(800)
        self.pixel_scale.pack(side=tk.LEFT, fill=tk.X)

        # 新增空間
        self.entry_frame = tk.Frame(master, bg="#D3D3D3")
        self.entry_frame.place(relx=0.2, rely=0.87, relwidth=0.61, relheight=0.05)
        self.illustrate_text = tk.Text(self.entry_frame, bg="#D3D3D3", fg='red', font=("Arial", 20))

        # 設置點擊事件回調函數
        self.canvas.mpl_connect('button_press_event', self.on_click)

        # 參數
        self.crop_pixel = self.pixel_scale.get()
        self.x_pixel, self.y_pixel = None, None
        self.save_count = 0

    def image_set_up(self):
        
        # load file
        self.img_arr = mpimg.imread(self.file_path) # RGB array?
        self.width, self.length, _ = self.img_arr.shape # tkinter Scale 要使用
        
        self.ax.clear()
        self.ax.set_title(file_name(self.file_path))
        self.ax.imshow(self.img_arr, cmap='gray', vmin=0, vmax=255)
        self.fig.canvas.draw()

    def on_click(self, event):
        
        if event.xdata is not None:
            # 獲取點擊位置的座標
            self.x_pixel, self.y_pixel = int(round(event.xdata)), int(round(event.ydata))
            # 畫圖
            self.plt_square()
        
    def plt_square(self):

        if self.check_crop_exist():
            return
        # 計算正方形的位置
        x, y, size = self.x_pixel, self.y_pixel, self.crop_pixel
        rect_pos = (x - size / 2, y - size / 2)
        self.img_crop_param = rect_pos 

        self.clear() 
        self.rect = plt.Rectangle(rect_pos, size, size, fill=False, linestyle='--', alpha=0.5, edgecolor='red')
        self.ax.add_patch(self.rect)
        self.fig.canvas.draw()

    def check_crop_exist(self):
        return self.x_pixel is None

    def crop(self):
  
        if self.check_crop_exist():
            return
        col, row, size = self.x_pixel, self.y_pixel, self.crop_pixel
        self.img_crop = self.img_arr[row-size//2: row+size//2, col-size//2: col+size//2]

        self.ax.clear()
        self.ax.set_title(file_name(self.file_path))
        self.ax.imshow(self.img_crop, cmap='gray', vmin=0, vmax=255)
        self.fig.canvas.draw()

    def clear(self):
        self.ax.clear()
        self.ax.set_title(file_name(self.file_path))
        self.ax.imshow(self.img_arr, cmap='gray', vmin=0, vmax=255)
        self.fig.canvas.draw()
        
    def file_name_add_time(self, abs_path):
        
        _item2 = abs_path.split('/')[-1].split('_')[0]
        _item3  = time.strftime("%H%M%S")
        return f'{_item2}_{_item3}' # 'row1_225456'

    
    def save_fig(self):

        if self.check_crop_exist():
            self.save_status()
            return

        col, row, size = self.x_pixel, self.y_pixel, self.crop_pixel
        self.img_crop = self.img_arr[row-size//2: row+size//2, col-size//2: col+size//2]
        img = Image.fromarray(self.img_crop.astype('uint8'))     # 將 ndarray 存成 jpg
        '''
        若 self.count 存在，則直接使「順序」當作檔案。
        
        '''
        if self.count is None:
            file_name_add_time = self.file_name_add_time(self.file_path)
            folder_path   = os.path.dirname(self.file_path)
            self.save_where = folder_path + f"/crop_{file_name_add_time}.jpg"

        elif len(self.entry_get()) == 0:      # --- Entry 有沒有填入東西 --- #
            print("輸入 col number") # 實驗中的 colume size. ex: 5*10, 重複 10 個 point
            return

        else:
            col_number = self.entry_get()
            col_number = int(col_number)
            _item1 = self.folder_path
            _item2 = self.file_path.split('/')[-1].split('_')[0]

            output = (self.save_count+1) % col_number
            if output == 0:
                output = col_number

            self.save_where = f"{_item1}/crop_{_item2}_{output}.jpg"

        # 存擋及查看狀況
        img.save(self.save_where)
        self.save_status()
        self.save_count += 1

    def save_status(self):
        
        if self.check_crop_exist():
            word = f"Faill"
        else:
            word = f"save at: {self.save_where.split('/')[-2]}/{self.save_where.split('/')[-1]}" 
        
        self.illustrate_text.delete("1.0", tk.END)
        self.illustrate_text.insert(tk.END, word)    
        self.illustrate_text.pack(fill=tk.BOTH, expand=True)


    def update_crop_square_pixel(self, value):
        self.crop_pixel = int(value)
        self.plt_square()

    def __load_file(self):

        self.file_path = tk_choose_path(master=root)
        self.image_set_up()


class CropImageAppFromFolder(CropImageApp):
    def __init__(self, master, file_path, all_file_list):
        super().__init__(master, file_path)
        self.all_file_list = all_file_list
        self.folder_path = os.path.dirname(self.file_path)
        self.first_set_up()
        self.image_set_up()

        self.choose_folder_button = tk.Button(master=self.master, text='Choose Folder', command=self.choose_folder)
        self.choose_folder_button.pack(side=tk.LEFT)

        # 左箭頭 button
        self.arrow_left_image  = ImageTk.PhotoImage(Image.open('arrow_left.png')) # 載入圖片並轉換成 PhotoImage
        self.arrow_left_button = tk.Button(master=self.master, image=self.arrow_left_image, bg='lightgray', command=self.left_image)
        self.arrow_left_button.pack(side=tk.LEFT)
        self.master.bind('<Left>', lambda event: self.left_image()) # 使用鍵盤 觸發相同事件

        self.arrow_right_image  = ImageTk.PhotoImage(Image.open('arrow_right.png'))
        self.arrow_right_button = tk.Button(master=self.master, image=self.arrow_right_image, bg='lightgray', command=self.right_image)
        self.arrow_right_button.pack(side=tk.LEFT)
        self.master.bind('<Right>', lambda event: self.right_image()) # 使用鍵盤 觸發相同事件

        self.col_number_entry = tk.Entry(self.master)
        self.col_number_entry.pack(side=tk.LEFT)

    def first_set_up(self):
        '''
        Whan load new folder, `self.file_path` need to be reset.

        因為 load all file 按造檔案名顯示，
        故每次 reset `self.save_count` 從 0 開始。
                    `self.save_count` 也因該從 0 開始計算。
        '''
        self.count = 0    
        self.save_count = 0
        self.file_path = f"{self.folder_path}/{self.all_file_list[self.count]}"

    def choose_folder(self):
        
        self.folder_path   = tk_choose_folder(master=root)
        self.all_file_list = read_folder_all_file(folder=self.folder_path, keyword='.jpg')

        # after choose folder, image need to be reset
        self.first_set_up()
        self.image_set_up()


    def entry_get(self):
        return self.col_number_entry.get()

    def left_image(self):

        if self.count == 0:
            return
        self.count -= 1
        self.file_path = f"{self.folder_path}/{self.all_file_list[self.count]}"

        self.img_arr = mpimg.imread(self.file_path)
        self.clear()

    def right_image(self):
        
        if self.count == len(self.all_file_list)-1:
            return
        self.count += 1
        self.file_path = f"{self.folder_path}/{self.all_file_list[self.count]}"
        
        self.img_arr = mpimg.imread(self.file_path)
        self.clear()


class ChooseAPPversion:
    def __init__(self, master):

        self.master = master
        self.master.geometry('450x600')
        self.master.title('Choose APP version')

        self.add_sum_button = tk.Button(master, text="load file only", command=self.load_file_only, font=("Arial", 18), bg='#87CEEB')
        self.add_sum_button.place(relx=0.3, rely=0.18, anchor=tk.CENTER, width=150, height=40)

        self.add_clear_button = tk.Button(master, text='choose folder', command=self.tk_choose_folder, font=("Arial", 18), bg="yellow")
        self.add_clear_button.place(relx=0.7, rely=0.18, anchor=tk.CENTER, width=150, height=40)

        # 新增空間
        self.entry_frame = tk.Frame(master)
        self.entry_frame.place(relx=0.15, rely=0.3, relwidth=0.7, relheight=0.5)

        c = '\n'
        t = '\t'
        word = f"load file only:{c}  透過 tkinter 讀取指定圖片檔{c}{c}choose folder:{c}  透過 tkinter 取得 folder，然後 load folder 底下所有的檔案"
        self.illustrate_text = tk.Text(self.entry_frame, bg="#D3D3D3", fg='black', font=("Arial", 14))
        self.illustrate_text.insert(tk.END, word)
        self.illustrate_text.pack(fill=tk.BOTH, expand=True)

    def load_file_only(self):

        file_path = tk_choose_path(root) 
        CropImageApp(self.master, file_path)


    def tk_choose_folder(self):

        file_abs_path = tk_choose_folder(root)
        all_file_list = read_folder_all_file(folder=file_abs_path, keyword='.jpg')
        if len(all_file_list) > 1:
            CropImageAppFromFolder(self.master, f"{file_abs_path}/{all_file_list[0]}", all_file_list)
        else:
            print("There is no file!!!")


if __name__ == "__main__":

    root = tk.Tk()
    app = ChooseAPPversion(root)
    root.mainloop()
