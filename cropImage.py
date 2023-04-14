from PIL import Image, ImageTk
import tkinter as tk

file = f'/Users/k.y.chen/Library/CloudStorage/OneDrive-國立陽明交通大學/文件/交大電物/實驗室/7. 實驗 Data/20230413 SEM/AP/18.tif'

class App:
    def __init__(self, master, file):
        self.master = master
        self.canvas = tk.Canvas(master, width=1280, height=1024)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.img = Image.open(file)
        self.img_tk = ImageTk.PhotoImage(self.img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img_tk)

        self.label = tk.Label(master, text='')
        self.label.pack()

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 
                                                  self.start_x, self.start_y, 
                                                  outline='red')

    def on_move_press(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        # Calculate the length and direction of the square edge
        edge_length = min(abs(cur_x - self.start_x), abs(cur_y - self.start_y))
        if cur_x < self.start_x:
            edge_length = -edge_length
        if cur_y < self.start_y:
            edge_length = -edge_length

        # Calculate the coordinates of the square
        square_x1 = self.start_x
        square_y1 = self.start_y
        square_x2 = self.start_x + edge_length
        square_y2 = self.start_y + edge_length

        # Update the square on the canvas
        self.canvas.coords(self.rect, square_x1, square_y1, square_x2, square_y2)

        self.label.config(text=f'X: {cur_x}, Y: {cur_y}')

    def on_button_release(self, event):
        self.end_x = self.canvas.canvasx(event.x)
        self.end_y = self.canvas.canvasy(event.y)

        # Calculate the coordinates of the square
        square_x1 = self.start_x
        square_y1 = self.start_y
        square_x2 = self.start_x + min(abs(self.end_x - self.start_x), abs(self.end_y - self.start_y))
        square_y2 = self.start_y + min(abs(self.end_x - self.start_x), abs(self.end_y - self.start_y))

        # Extract the region of interest and show it
        if square_x1 < square_x2 and square_y1 < square_y2:
            box = (square_x1, square_y1, square_x2, square_y2)
            region = self.img.crop(box)
            region.show()

        self.rect = None
    

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, file)
    root.mainloop()
